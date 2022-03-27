import pglast
import copy
from typing import Any, Tuple

LEFT_PARENTHESIS = "ASCII_40"
RIGHT_PARENTHESIS = "ASCII_41"
RESERVED_KEYWORD = "RESERVED_KEYWORD"
UNRESERVED_KEYWORD = "UNRESERVED_KEYWORD"
COL_NAME_KEYWORD = "COL_NAME_KEYWORD"

NO_KEYWORD = "NO_KEYWORD"
CREATE_KEYWORD = "CREATE"
ASSERTION_KEYWORD = "ASSERTION" 
IDENTIFIER_KEYWORD = "IDENT" 
CHECK_KEYWORD = "CHECK" 
NOT_KEYWORD = "NOT" 
EXISTS_KEYWORD = "EXISTS" 

MINIMUM_TOKEN_LENGTH = 6
MINIMUM_SEARCH_CONDITION_TOKEN_LENGTH = 4
INDEX_BEFORE_SEARCH_CONDITION = 4



def validate_syntax(statement: str)->Tuple[str, bool]:
    '''
    Valid raw statement input:
    CREATE ASSERTION any_name CHECK (<search condition>)

    <search condition> ::= exists/not exists (sql statement)

    Returns the extracted sql statement or boolean expression as the 1st parameter
    The second parameter is a boolean value indicating whether the extracted statement is in '[NOT] EXISTS(' format
    '''

    tokens = pglast.parser.scan(statement)
    if len(tokens) < MINIMUM_TOKEN_LENGTH:
        raise ValueError(f'Scanned statement does not match minimum token length. statement: \'{statement}\'')

    ## check the statement starts with "CREATE ASSERTION"
    if not _check_token(tokens[0], CREATE_KEYWORD) or not _check_token(tokens[1], ASSERTION_KEYWORD, UNRESERVED_KEYWORD):
        raise ValueError(f'Scanned statement does not start with \'create assertion\'. statement: \'{statement}\'')

    ## check there is identifier(assertion name) after "CREATE ASSERTION"
    if not _check_token(tokens[2], IDENTIFIER_KEYWORD, NO_KEYWORD):
        raise ValueError(f'Scanned statement does not contain assertion name. statement: \'{statement}\'')

    ## check there is `check` keyword after the identifier
    if not _check_token(tokens[3], CHECK_KEYWORD):
        raise ValueError(f'Scanned statement does not contain check clause. statement: \'{statement}\'')

    ## check there is `(` after the `check` keyword
    if not _check_token(tokens[4], LEFT_PARENTHESIS, NO_KEYWORD):
        raise ValueError(f'Scanned statement does not have \'(\' after \'check\'. statement: \'{statement}\'')

    ## get the tokens related to the search condition statement
    end_index = _get_search_condition_end_index(statement, tokens[INDEX_BEFORE_SEARCH_CONDITION:])
    search_condition = tokens[4: end_index+1]
    
    ## TODO: handle constraint characteristics

    ## check the validity of the search condition statement and return extract query
    return _validate_search_condition(statement, search_condition)


def _check_token(token:Any, name: str, type: str = RESERVED_KEYWORD)->bool:
    '''
    Validates the token has the same name and type as expected
    '''

    return token.name==name and token.kind==type


def _get_search_condition_end_index(statement: str, remaining_tokens: Tuple[Any, ...])->int:
    '''
    validates the parentheses are balanced in the search condition clause and outputs the index of the last token of search condition clause
    '''

    stack = []
    last_parenthesis_index = 0
    for i, t in enumerate(remaining_tokens):
        if t.name == LEFT_PARENTHESIS:
            stack.append(1)
        elif t.name == RIGHT_PARENTHESIS:
            if len(stack) <= 0:
                raise ValueError(f'Scanned statement does not have balanced parentheses. statement: \'{statement}\'')
            stack.pop()
            last_parenthesis_index = i
        
    if len(stack) != 0:
        raise ValueError(f'Scanned statement does not have balanced parentheses. statement: \'{statement}\'')

    return last_parenthesis_index+INDEX_BEFORE_SEARCH_CONDITION


def _validate_search_condition(statement: str, search_condition_tokens: Tuple[Any, ...])->Tuple[str, bool]:
    '''
    validates the search condition is in the below format and return the extracted statement
    [NOT] EXISTS (SQL Statement)
    OR
    (sql boolean expression)
    '''

    def strip_paretheses(tokens: Tuple[Any, ...])->Tuple[Any, ...]:
        if _check_token(tokens[0], LEFT_PARENTHESIS, NO_KEYWORD):
            if _check_token(tokens[-1], RIGHT_PARENTHESIS, NO_KEYWORD):
                tokens = strip_paretheses(tokens[1:-1])
            else:
                raise ValueError(f'search condition statement does not have balanced parentheses. statement: \'{statement}\'')

        return tokens

    if len(search_condition_tokens) < MINIMUM_SEARCH_CONDITION_TOKEN_LENGTH:
        raise ValueError(f'Search condition statement does not match minimum token length. statement: \'{statement}\'')

    ## strip all outer parentheses
    tokens = copy.deepcopy(search_condition_tokens)
    tokens = strip_paretheses(tokens)

    ## if the 1st token is 'NOT'
    is_not = False
    is_exist = False
    if _check_token(tokens[0], NOT_KEYWORD):
        tokens = strip_paretheses(tokens[1:])
        is_not = True
    
    ## check the 1st token is 'EXISTS' or other sql boolean expression
    if _check_token(tokens[0], EXISTS_KEYWORD, COL_NAME_KEYWORD):
        tokens = strip_paretheses(tokens[1:])
        is_exist = True
    else:
        tokens = strip_paretheses(tokens) 


    ## check the select statement inside the EXISTS clause
    start_index = tokens[0].start
    end_index = tokens[-1].end + 1
    inner_statement = statement[start_index: end_index]

    ## statement is (sql boolean expression). put a dummy select statement before it
    if not is_exist:
        check_statement = f"select * from dummy_check where {inner_statement}"
    else:
        check_statement = inner_statement

    pglast.parser.parse_sql(check_statement)

    full_statement = \
        (f"NOT " if is_not else "") + \
        (f"EXIST(" if is_exist else "") + \
        (f"{inner_statement}") + \
        (f")" if is_exist else "")

    return full_statement, is_exist