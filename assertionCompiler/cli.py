import argparse
import pglast
import traceback
from typing import List

from assertionCompiler import validator
from assertionCompiler import table_detector


def get_create_assertion_constraint_query(args: argparse.Namespace)->str:
    '''
    gets the raw create assertion contraint query from file or stdin and returns the cleaned query
    '''
    if hasattr(args, "file_path") and args.file_path:
        with open(args.file_path, 'r') as f:
            query = f.read()
    else:
        query = args.raw_query
    
    ## remove newline and tab
    query = query.replace('\n', " ").replace('\r', " ").replace('\t', " ")

    ## replace multiple spaces to 1 space
    query = " ".join(query.split()) 
    return query


def transfrom_none_exists_statement(statement: str, tables: List[str], is_exist:bool)->str:
    '''
    transfrom sql bool statement(is_exist == False) to the below format
    NOT EXISTS(!(SELECT * FROM tables WHERE <sql boolean expression>))
    '''
    if is_exist:
        return statement
    else:
        return f" NOT EXISTS(!(SELECT * FROM {' '.join(tables)} WHERE {statement}))"


def parse_arguments(args:list)->argparse.Namespace:
    '''
    parses input arguments
    '''
    arg_parser = argparse.ArgumentParser(description="Postgres Assertion Constraint Compiler")
    arg_parser.add_argument("-v", "--verbose", dest='verbose', action='store_true', help="Enable verbose log")

    input_args = arg_parser.add_mutually_exclusive_group(required=True)
    input_args.add_argument("-q", "--query", dest='raw_query', help="Specify raw create assertion query")
    input_args.add_argument("-f", "--file", dest='file_path', help="Specify the file path of the create assertion query")
    return arg_parser.parse_args(args)


def main(args=None):
    args = parse_arguments(args)
    query = get_create_assertion_constraint_query(args)
    try:
        for s in pglast.parser.split(query, with_parser=False):
            ## validation
            extracted_query, is_exist = validator.validate_syntax(s)

            ## extract tables
            tables = table_detector.detect_table(extracted_query)

            ## transform none-exists statement(sql boolean expression)
            extracted_query = transfrom_none_exists_statement(extracted_query, tables, is_exist) 

            ## TODO: generate function and triggers

            ## TODO: print output
            
    except Exception as e:
        if args.verbose:
            print(traceback.format_exc())
        else:
            print(f'Failed to compile input statement. err: {e}')
