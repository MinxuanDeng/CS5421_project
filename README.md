# PACC
## Postgresql Assertion Constraint Compiler
This is a command line tool written in python 3.8 that compiles create assertion statement(not supported in postgresql) and outputs create trigger and create function statements(supported in postgresql)

## Installation
Clone the repository
```
$ git clone git@github.com:MinxuanDeng/CS5421_project.git
```

Install from the repo
```
$ pip install ./CS5421_project
```

## Running
```
$ pacc -q "create assertion assertion_name check (exists(select * from myTable where myTable.id = 1))"
```

## Help
```
$ pacc -h
```

## Testing
Install dependency
```
$ pip install -r ./CS5421_project/requirements-test.txt
```

Run pytest
```
pytest ./CS5421_project/test
```