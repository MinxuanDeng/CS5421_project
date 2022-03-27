def text2List(text):
    '''
    :param: plain valid sql text:
    :return: a list of tokens(terminals)
    it's actually a lexer, converting text into a list of strings(terminals)
    '''
    index = 0
    buffer = ''
    ret_list = list()
    cutter = {',',';','*','(',')','=','+','-','/','%','^','#','~','\'','@'}
    while(index<len(text)):
        if text[index] == ' ' or text[index] == '\t':
            if buffer != '':
                ret_list.append(buffer)
                buffer = ''
            index+=1
        elif text[index] == '\n':
            if buffer != '':
                ret_list.append(buffer)
                buffer = ''
            index+=1
        elif text[index] in cutter:
            if buffer != '':
                ret_list.append(buffer)
                buffer = ''
            ret_list.append(text[index])
            index += 1
        elif text[index] == '>':
            if buffer != '':
                ret_list.append(buffer)
                buffer = ''
            # might be > or >= or >>
            if len(text)>index+1 and text[index+1]=='=':
                ret_list.append('>=')
                index += 2
            elif len(text)>index+1 and text[index+1]=='>':
                ret_list.append('>=')
                index += 2
            else:
                ret_list.append('>')
                index += 1
        elif text[index] == '<':
            if buffer != '':
                ret_list.append(buffer)
                buffer = ''
            # might be < or <= or <> or <<
            if len(text) > index + 1 and text[index + 1] == '=':
                ret_list.append('<=')
                index += 2
            elif len(text) > index + 1 and text[index + 1] == '>':
                ret_list.append('<>')
                index += 2
            elif len(text) > index + 1 and text[index + 1] == '<':
                ret_list.append('<<')
                index += 2
            else:
                ret_list.append('<')
                index += 1
        elif text[index] == '!':
            if buffer != '':
                ret_list.append(buffer)
                buffer = ''
            if len(text) > index + 1 and text[index + 1] == '=':
                ret_list.append('!=')
                index += 2
            elif len(text) > index + 1 and text[index + 1] == '!':
                ret_list.append('!!')
                index += 2
            else:
                ret_list.append('!')
                index += 1
        elif text[index] == '|':
            if buffer != '':
                ret_list.append(buffer)
                buffer = ''
            if len(text) > index + 1 and text[index + 1] == '/':
                ret_list.append('|/')
                index += 2
            elif len(text) > index + 2 and text[index + 1] == '|' and text[index + 2] == '/':
                ret_list.append('||/')
                index += 3
            else:
                ret_list.append('|')
                index += 1
        else:
            buffer += text[index]
            index += 1
    if buffer != '':
        ret_list.append(buffer)
    # lower case all tokens
    for i in range(len(ret_list)):
        ret_list[i] = ret_list[i].lower()
    return ret_list

def list2Text(terminals):
    '''

    :param terminals: a list of terminals
    :return: plain text of sql
    convert a list of terminals back to plain text
    '''
    ret = ''
    no_blankspace = {'(',')',',',';','\n'}
    for i in range(len(terminals)):
        if i+1 < len(terminals) and terminals[i+1] in no_blankspace:
            ret += terminals[i]
        elif terminals[i] == '(':
            ret += terminals[i]
        elif terminals[i] =='\n' and i>=1 and terminals[i-1] == '\n':
            ret += ' '
        else:
            ret += terminals[i]+' '
    return ret

def removeRedundantNewLine(text):
    output = ''
    for char in text:
        if char == '\n':
            if len(output) > 0 and output[-1] == '\n':
                continue
            else:
                output += '\n'
        else:
            output += char
    return output

def createDictionary(text):
    '''
    split text into ddl without COMPLEX checks and checks
    return dict('ddl': ddl, 'checks':[check_text1, check_text2, ...])
    '''
    try:
        in_check_clause = False
        ddl_elements = []
        check_list = []
        check_elements = []
        not_matched_left_bracket = 0
        index = 0
        terminals = text2List(text)
        while index < len(terminals):
            if not in_check_clause:
                if terminals[index] == 'check':
                    # it may also be a simple check, which should be preserved in ddl
                    if terminals[index+2].lower() == 'not' or terminals[index+2].lower() == 'exists':
                        # complex checks
                        check_elements.clear()
                        check_elements.append('check')
                        check_elements.append('(')
                        not_matched_left_bracket = 1
                        index = index + 2
                        in_check_clause = True
                    else:
                        ddl_elements.append(terminals[index])
                        index += 1
                else:
                    ddl_elements.append(terminals[index])
                    index += 1
            else:
                if terminals[index] == ')':
                    if not_matched_left_bracket == 1:
                        check_elements.append(')')
                        not_matched_left_bracket = 0
                        in_check_clause = False
                        check_list.append(check_elements.copy())
                        check_elements.clear()
                        if terminals[index+1] == ',':
                            index += 2
                        else:
                            index += 1
                    else:
                        check_elements.append(')')
                        not_matched_left_bracket -= 1
                        index += 1
                elif terminals[index] == '(':
                    check_elements.append('(')
                    not_matched_left_bracket += 1
                    index += 1
                else:
                    check_elements.append(terminals[index])
                    index += 1
        ddl_string = removeRedundantNewLine(list2Text(ddl_elements))
        checks_strings = []
        for temp in check_list:
            checks_strings.append(removeRedundantNewLine(list2Text(temp)))
        ret = dict()
        ret['ddl'] = ddl_string
        ret['checks'] = checks_strings
        return ret
    except:
        print('input is not valid')
        return None

def findSubClauseEnd(terminals, clauseBegin):
    number_of_left_bracket = 1
    index = clauseBegin+1
    while number_of_left_bracket > 0:
        if terminals[index] == '(':
            number_of_left_bracket += 1
        elif terminals[index] == ')':
            number_of_left_bracket -= 1
        index += 1
    return index

def findTablesRecursion(terminals, clauseBegin, clauseEnd):
    tables = set()
    temp_tables = set()
    index = clauseBegin
    '''
        the following sql is valid:
        with temp as (
            select * from (
                with temp2 as (
                    select * from table2
                ) 
                select * 
                from table1,temp2
            ) a1
        )
        select *
        from temp
        So recursion is unavoidable
    '''
    # the grammar of sql indicates that if there's a with clause,
    # it must only appear at the very beginning
    if terminals[index] == 'with':
        # the next element must be a temp table's name
        index += 1
        temp_tables.add(terminals[index])
        index += 1
    while index < clauseEnd:
        # the grammar of sql indicates that if there's a with clause,
        #  it may only appear at the very beginning
        '''
        the only thing dividing two tables in a from clause is either comma or "join"
        '''
        if terminals[index] == 'from':
            end_of_from = {'where', 'group', 'union', 'intersect', 'except', 'order', 'limit', 'offset', 'for',')'}
            readTable = True
            index += 1
            while index < clauseEnd:
                if readTable:
                    if terminals[index] == '(':
                        sub_clause_end = findSubClauseEnd(terminals,index)
                        ret_tables,ret_temp_tables = findTablesRecursion(terminals,index+1,sub_clause_end-1)
                        tables = tables.union(ret_tables.copy())
                        temp_tables = temp_tables.union(ret_temp_tables.copy())
                        index = sub_clause_end
                    elif index < clauseEnd and terminals[index] not in end_of_from :
                        # the current token is the table name
                        tables.add(terminals[index])
                        index += 1
                    readTable = False
                else:
                    if terminals[index] == ',' or terminals[index] == 'join':
                        readTable = True
                        index += 1
                    elif terminals[index] in end_of_from:
                        break
                    else:
                         index += 1
        else:
            index += 1
    return tables,temp_tables

def findTables(terminals):
    '''
    :param terminals: a list of tokens
    :return: a list of tables(str)
    find all tables involved in a query except for temp tables(with clause)
    '''
    index = 0
    tables,temp_tables = findTablesRecursion(terminals,0,len(terminals))
    ret = tables.difference(temp_tables)
    return sorted(ret)


def detect_table(statement:str):
    return findTables(text2List(statement))

# with open('input2.txt','r') as f:
#     # input contains the ddl with(without) complex check
#     # createDictionary would split complex checks out of ddl
#     text = f.read()
#     tokens = text2List(text)
#     #for i in range(len(tokens)):
#     #    print(i,tokens[i])
#     print(findTables(tokens))

