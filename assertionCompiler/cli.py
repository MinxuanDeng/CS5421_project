import argparse
import pglast
import traceback

from assertionCompiler import validator



def main():
    arg_parser = argparse.ArgumentParser(description="Postgres Check Constraint Compiler")
    arg_parser.add_argument("-q", "--query", dest='raw_query', required=True, help="Specify raw check constraint")
    arg_parser.add_argument("-v", "--verbose", dest='verbose', action='store_true', help="Enable verbose log")

    args = arg_parser.parse_args()
    try:
        for s in pglast.parser.split(args.raw_query, with_parser=False):
            validator.validate_syntax(s)
    except Exception as e:
        if args.verbose:
            print(traceback.format_exc())
        else:
            print(f'Failed to compile input statement. err: {e}')
