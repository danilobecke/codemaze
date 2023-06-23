import sys

def modified_py_files(raw: str) -> str:
    files = raw.split('\n')
    py_files = list(filter(lambda file: file.endswith('.py'), files))
    print(' '.join(py_files))

if __name__ == '__main__':
    modified_py_files(sys.argv[1])
