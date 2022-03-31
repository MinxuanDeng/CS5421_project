def text2List(text):
    '''
    :param: plain VALID simple check constraints, e.g. table1.annual_income = table1.salary * 12 and table2.age > 0
    :return: a lisf of tokens(terminals)
    it's actually a lexer, converting text into a list of strings(terminals)
    '''
    index = 0
    buffer = ''
    ret_list = list()
    cutter = {',',';','*','(',')','=','+','-','/','%','^','#','~','\'','@','.'}
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

def findTables(terminals):
    '''
    :param terminals: a list of tokens
    :return: a list of tables(str)
    find all tables involved in a query except for temp tables(with clause)
    '''
    ret_set = set()
    for i in range(0,len(terminals)):
        if i+1 < len(terminals) and terminals[i+1] == '.' and not terminals[i].isdigit():
            ret_set.add(terminals[i])
    return sorted(list(ret_set))

def generateComplexConstraint(simple_check:str):
    '''
    :param simple_check: plain text of constraint e.g. table1.id1 = table2.id2+1
    :return: a sql
    '''
    tables = detect_table(simple_check)
    ret = 'not exists\n(select *\nfrom '
    for table in tables:
        ret += table + ', '
    ret = ret[0:len(ret)-2]
    ret += '\nwhere not (' + simple_check + ')\n)'
    return ret

def detect_table(statement:str):
    return findTables(text2List(statement))

if __name__ == "__main__":
    simple_check = 'table1.annual_income = table1.salary * 12 and table2.age > 0 or table3.id = table2.id'
    print('the tables in simple checks are:')
    print(detect_table(simple_check))
    print()
    print('complex constraint generated from simple checks are:')
    print(generateComplexConstraint(simple_check))
