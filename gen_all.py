def gen_code(tables_list, original_statement, assertion_name):
    '''

    :param tables_list: the name of the tables
    :param original_statement: "check ..."
    :param assertion_name: the name of the ASSERTION that the user creates
    :return: code: the code that generates all create statement required
    '''
    code = []
    trigger_code = gen_trigger(tables_list, assertion_name)
    func_code = gen_func(original_statement, assertion_name)
    code.append(func_code)
    code.extend(trigger_code)

    return code
def gen_trigger(tables_list, assertion_name):
    '''
    :param tables_List: a list of tables
    :param original_statement: statement after CHECK
    :return: a list of PostPreSQL Create Trigger Syntax
    '''
    output = []

    for i, tbl in enumerate(tables_list):
        trigger_name = tbl + '_' + str(i)
        trigger_name = "trigger_" + tbl + "_"+ assertion_name
        function_name = 'trigger_func_' + assertion_name
        output.append(gen_create_trigger(trigger_name, tbl,function_name))
    return output


def gen_create_trigger(trigger_name, table_name, function_name):
    sql = 'CREATE CONSTRAINT TRIGGER %s '%trigger_name
    sql += '\n    AFTER INSERT OR UPDATE OR DELETE'
    sql += '\n    ON %s'%table_name
    sql += '\n    DEFERRABLE INITIALLY DEFERRED'
    sql += '\n    FOR EACH ROW'
    sql += '\n    EXECUTE PROCEDURE %s();'%function_name
    return sql


def gen_func(statement, assertion_name):
    code_define_and_begin = "CREATE FUNCTION trigger_func_" + assertion_name + "() RETURNS TRIGGER as $$\n    BEGIN\n"
    code_if = "        IF " + statement + " THEN\n            NULL;\n        "
    code_else = "ELSE\n            RAISE EXCEPTION 'Violate ASSERTION %','" + assertion_name +"';\n        "
    code_endif = "END IF;\n        RETURN NULL;\n    "
    code_end = "END\n"
    code_plp = "$$ LANGUAGE plpgsql;"
    return code_define_and_begin + code_if + code_else + code_endif + code_end + code_plp


def main():
    results = gen_code(["table1"], "exists (select * from table1)", "test")
    for result in results:
        print(result)


if __name__ == '__main__':
    main()