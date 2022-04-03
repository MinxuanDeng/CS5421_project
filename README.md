# PACC
## Postgresql Assertion Constraint Compiler
This is a command line script written in python 3.8 that compiles create assertion statement(not supported in postgresql) and outputs create trigger and create function statements(supported in postgresql)

## Usage
Clone the repository
```
$ git clone git@github.com:MinxuanDeng/CS5421_project.git
```
## Running
```
$ python CS5421_project/cli/cli.py -q "create assertion assertion_name check (exists(select * from myTable where myTable.id = 1))"
```

## Help
```
$ python CS5421_project/cli/cli.py -h
```

## Testing
### Pytest
Install dependency
```
$ pip install -r ./CS5421_project/requirements-test.txt
```

Run pytest
```
pytest ./CS5421_project/test
```

### Manual test
There are couple of test sql files under ./test_data folder
```
$ python CS5421_project/cli/cli.py -f ./test_data/complex_boolean_text_query.sql -d -v
```