import argparse
import pglast
import traceback
from typing import List

from assertionCompiler import validator
from assertionCompiler import table_detector
from assertionCompiler import table_detector_simple
from assertionCompiler import gen_all


DEBUG_ENABLE = False


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


def transfrom_statement(prefix: str, statement: str, tables: List[str], is_exist:bool)->str:
    '''
    transfrom sql bool statement(is_exist == False) to the below format
    NOT EXISTS(SELECT * FROM tables WHERE NOT(<sql boolean expression>))
    OR
    transfrom sql select statement(is_exist == True) to the below format
    NOT EXISTS(sql select statement)
    '''
    if is_exist:
        return f'{prefix}({statement})'
    else:
        return f"NOT EXISTS(SELECT * FROM {','.join(tables)} WHERE NOT({statement}))"


def parse_arguments(args:list)->argparse.Namespace:
    '''
    parses input arguments
    '''
    arg_parser = argparse.ArgumentParser(description="Postgres Assertion Constraint Compiler")
    arg_parser.add_argument("-v", "--verbose", dest='verbose', action='store_true', help="Enable verbose traceback log")
    arg_parser.add_argument("-d", "--debug", dest='debug', action='store_true', help="Enable debug log")

    input_args = arg_parser.add_mutually_exclusive_group(required=True)
    input_args.add_argument("-q", "--query", dest='raw_query', help="Specify raw create assertion query")
    input_args.add_argument("-f", "--file", dest='file_path', help="Specify the file path of the create assertion query")
    args = arg_parser.parse_args(args)
    if args.debug:
        global DEBUG_ENABLE
        DEBUG_ENABLE = True

    return args


def debug_print(*args, **kwargs):
    if DEBUG_ENABLE:
        print(*args, **kwargs)


def main(args=None):
    args = parse_arguments(args)
    query = get_create_assertion_constraint_query(args)
    try:
        for s in pglast.parser.split(query, with_parser=False):
            print("")
            ## validation
            assertion_name, prefix, inner_query, is_exist = validator.validate_syntax(s)
            debug_print(f"Step1 result: \n{{assertion_name: {assertion_name}, prefix: {prefix}, inner_query: {inner_query}, is_exist: {is_exist}}}\n")

            ## extract tables
            if is_exist:
                tables = table_detector.detect_table(inner_query)
            else:
                tables = table_detector_simple.detect_table(inner_query)

            ## transform statement to [NOT] EXISTS (select statement)
            extracted_query = transfrom_statement(prefix, inner_query, tables, is_exist)
            debug_print(f"Step2 result: \n{{tables: {tables}, query: {extracted_query}}}\n")

            ## TODO: generate function and triggers
            results = gen_all.gen_code(tables, extracted_query, assertion_name)

            ## TODO: print output
            print("Output:")
            for result in results:
                print("")
                print(result)
            

    except Exception as e:
        if args.verbose:
            print(traceback.format_exc())
        else:
            print(f'Failed to compile input statement. err: {e}')
