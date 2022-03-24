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
    validator.validate_syntax(statement)


@pytest.mark.valid
def test_simple_statement_parenthesis_after_not_keyword():
    statement = "not (exists (select * from myTable))"
    statement = VALID_ASSERTION_CREATEION_STATEMENT.format(statement=statement)
    validator.validate_syntax(statement)


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