import pytest
import argparse
import os

from .const import TEST_DATA_PATH
from assertionCompiler import cli



@pytest.mark.valid
def test_simple_statement():
    arguments = ['-q', 'create assertion assertion_name check (not exists(select * from myTable where myTable1.id = 1))']
    cli.main(arguments)

@pytest.mark.valid
def test_simple_statement_from_file_with_escape():
    arguments = ['-f', os.path.join(TEST_DATA_PATH, 'simple_test_query_valid_with_escape.sql')]
    cli.main(arguments)

@pytest.mark.valid
def test_clean_query_with_escape_signs():
    query = "create \rassertion \r\n\t\tassertion_name \r\ncheck (not exists (select * from myTable where myTable1.id = 1))"
    args = argparse.Namespace(raw_query=query)
    cleaned = cli.get_create_assertion_constraint_query(args)
    assert cleaned == "create assertion assertion_name check (not exists (select * from myTable where myTable1.id = 1))"

@pytest.mark.valid
def test_clean_query_with_escape_signs_from_file():
    path = os.path.join(TEST_DATA_PATH, 'simple_test_query_valid_with_escape.sql')
    args = argparse.Namespace(file_path=path)
    cleaned = cli.get_create_assertion_constraint_query(args)
    assert cleaned == "CREATE assertion single_table_assertion CHECK ( EXISTS ( SELECT id FROM mytable WHERE ID > 0 ) );"