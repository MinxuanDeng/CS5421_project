import pytest

from .const import read_test_data_file
from src import table_detector
from src import table_detector_simple


@pytest.mark.valid
def test_simple_statement():
    statement = "exists (select * from myTable)"
    tables = table_detector.detect_table(statement)
    assert "myTable".lower() in tables, "failed to detect correct tables"


@pytest.mark.valid
def test_complex_statement():
    statement = read_test_data_file("table_detector_input.txt")
    tables = table_detector.detect_table(statement)
    assert set(["table1", "table2", "table3", "table4"]) == set(tables), "failed to detect correct tables"


@pytest.mark.valid
def test_boolean_expression_statement():
    statement = "table1.ID = table2.ID"
    tables = table_detector_simple.detect_table(statement)
    assert set(["table1", "table2"]) == set(tables), "failed to detect correct tables"


@pytest.mark.valid
def test_multiple_boolean_expression_statement():
    statement = "table1.ID = table2.ID AND table3.ID = table3.ID"
    tables = table_detector_simple.detect_table(statement)
    assert set(["table1", "table2", "table3"]) == set(tables), "failed to detect correct tables"