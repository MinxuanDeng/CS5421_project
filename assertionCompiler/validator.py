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



def validate_syntax(statement: str):
    '''
    Valid raw statement input:
    CREATE ASSERTION any_name CHECK (<search condition>) <constraint characteristics>

    <search condition> ::= exists/not exists (sql statement)
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
    
    ## check the validity of the search condition statement.
    _validate_search_condition(statement, search_condition)

    ## TODO: handle constraint characteristics


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


def _validate_search_condition(statement: str, search_condition_tokens: Tuple[Any, ...]):
    '''
    validates the search condition is in the below format
    [NOT] EXISTS (SQL Statement)
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
    if _check_token(tokens[0], NOT_KEYWORD):
        tokens = strip_paretheses(tokens[1:])
    
    ## check the 1st token is 'EXISTS' after stripping 'NOT' and parentheses
    if not _check_token(tokens[0], EXISTS_KEYWORD, COL_NAME_KEYWORD):
        raise ValueError(f'search statement does not contain exists keyword. statement: \'{statement}\'')

    ## check the select statement inside the EXISTS clause
    tokens = strip_paretheses(tokens[1:])
    start_index = tokens[0].start
    end_index = tokens[-1].end + 1
    pglast.parser.parse_sql(statement[start_index: end_index])
