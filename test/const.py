import os

TEST_DIR = os.path.dirname(__file__)
TEST_DATA_PATH = os.path.join(TEST_DIR, "test_data")

def read_test_data_file(test_file_name: str):
    '''
    read data from the specified file under TEST_DATA_PATH and return the content
    '''
    with open(os.path.join(TEST_DATA_PATH, test_file_name), 'r') as f:
        return f.read()