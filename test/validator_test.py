import pytest
import pglast

from assertionCompiler import validator


VALID_ASSERTION_CREATEION_STATEMENT = "create assertion any_assertion check ({statement});"

@pytest.mark.valid
def test_simple_statement():
    statement = "exists (select * from myTable)"
    statement = VALID_ASSERTION_CREATEION_STATEMENT.format(statement=statement)
    validator.validate_syntax(statement)


@pytest.mark.valid
def test_complex_statement():
    statement = '''
NOT
(
  EXISTS (WITH temp AS
  (
         SELECT *
         FROM   mytable_2)
  SELECT *
  FROM   mytable,
         temp
  WHERE  temp.name = 'any')
)
'''
    statement = VALID_ASSERTION_CREATEION_STATEMENT.format(statement=statement)
    validator.validate_syntax(statement)


@pytest.mark.valid
def test_simple_statement_not_exist():
    statement = "not exists (select * from myTable)"
    statement = VALID_ASSERTION_CREATEION_STATEMENT.format(statement=statement)
    extarcted, is_exist = validator.validate_syntax(statement)
    assert is_exist, "extracted statement should be in [NOT] EXISTS format"
    assert extarcted == "NOT EXIST(select * from myTable)"


@pytest.mark.valid
def test_simple_statement_parenthesis_after_not_keyword():
    statement = "not (exists (select * from myTable))"
    statement = VALID_ASSERTION_CREATEION_STATEMENT.format(statement=statement)
    extarcted, is_exist = validator.validate_syntax(statement)
    assert is_exist, "extracted statement should be in [NOT] EXISTS format"
    assert extarcted == "NOT EXIST(select * from myTable)"


@pytest.mark.valid
def test_simple_statement_sql_boolean_expression():
    statement = "table1.ID = table2.ID"
    statement = VALID_ASSERTION_CREATEION_STATEMENT.format(statement=statement)
    extarcted, is_exist = validator.validate_syntax(statement)
    assert not is_exist, "extracted statement should be in sql boolean expression format"
    assert extarcted == "table1.ID = table2.ID"


@pytest.mark.valid
def test_simple_statement_sql_boolean_expression_not():
    statement = "not table1.ID = table2.ID"
    statement = VALID_ASSERTION_CREATEION_STATEMENT.format(statement=statement)
    extarcted, is_exist = validator.validate_syntax(statement)
    assert not is_exist, "extracted statement should be in sql boolean expression format"
    assert extarcted == "NOT table1.ID = table2.ID"


@pytest.mark.valid
def test_simple_statement_sql_boolean_expression_multiple_condition():
    statement = "table1.ID = table2.ID and table3.ID = table1.ID"
    statement = VALID_ASSERTION_CREATEION_STATEMENT.format(statement=statement)
    extarcted, is_exist = validator.validate_syntax(statement)
    assert not is_exist, "extracted statement should be in sql boolean expression format"
    assert extarcted == "table1.ID = table2.ID and table3.ID = table1.ID"


@pytest.mark.invalid
def test_assertion_statement_create_assertion():
    statement = '''
SELECT *
FROM   mytable,
       temp
WHERE  temp.name = 'any' 
'''
    with pytest.raises(ValueError) as exc_info:
        validator.validate_syntax(statement)

    assert "does not start with \'create assertion\'" in str(exc_info)


@pytest.mark.invalid
def test_assertion_statement_no_assertion_name():
    statement = '''
CREATE assertion CHECK (EXISTS
(
       SELECT *
       FROM   mytable
       WHERE  mytable.name = 'any' 
));
'''
    with pytest.raises(ValueError) as exc_info:
        validator.validate_syntax(statement)

    assert "does not contain assertion name" in str(exc_info)


@pytest.mark.invalid
def test_assertion_statement_missing_check():
    statement = '''
CREATE assertion any_assertion (EXISTS
(
       SELECT *
       FROM   mytable
       WHERE  mytable.name = 'any' 
));
'''
    with pytest.raises(ValueError) as exc_info:
        validator.validate_syntax(statement)

    assert "does not contain check clause" in str(exc_info)


@pytest.mark.invalid
def test_assertion_statement_no_parenthsis_after_check():
    statement = '''
CREATE assertion any_assertion CHECK EXISTS
(
       SELECT *
       FROM   mytable
       WHERE  mytable.name = 'any' 
);
'''
    with pytest.raises(ValueError) as exc_info:
        validator.validate_syntax(statement)

    assert "does not have \'(\' after \'check\'" in str(exc_info)


@pytest.mark.invalid
def test_assertion_statement_inner_statement():
    statement = '''
CREATE assertion any_assertion CHECK (EXISTS
(
       SELECT *
       WHERE  mytable.name = 'any'
       FROM   mytable     
));
'''
    with pytest.raises(pglast.Error) as exc_info:
        validator.validate_syntax(statement)

    assert "syntax error" in str(exc_info)


@pytest.mark.invalid
def test_simple_statement_sql_boolean_expression_invalid():
    statement = "table1..ID = table2.ID"
    statement = VALID_ASSERTION_CREATEION_STATEMENT.format(statement=statement)
    with pytest.raises(pglast.Error) as exc_info:
        validator.validate_syntax(statement)


@pytest.mark.invalid
def test_simple_statement_sql_boolean_expression_invalid_full_statement():
    statement = "select * from table1 where id = 111"
    statement = VALID_ASSERTION_CREATEION_STATEMENT.format(statement=statement)
    with pytest.raises(pglast.Error) as exc_info:
        validator.validate_syntax(statement)