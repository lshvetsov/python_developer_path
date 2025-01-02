"""
A static code analysis tool that checks Python code for style and common programming errors.
It reads a single file or all Python files in a specified directory and reports any violations
of set coding standards.
"""

import argparse
import os
import re
import ast

regex_construction_spaces = re.compile(r'^(def|class)\s{2,}')
regex_camel_case = re.compile(r'^[A-Z][a-zA-Z0-9]+$')
regex_snake_case = re.compile(r'^[a-z_][a-z0-9_]*$')


def main():
    """
    Main function that orchestrates reading the folder, retrieving files, and running checks.
    """
    path = read_folder()
    files = get_sorted_files(path)
    for file in files:
        run_check_on_file(file)


def read_folder():
    """
    Parses command-line arguments to retrieve the folder or file path.

    Returns:
        str: Path to the folder or file provided by the user.
    """
    parser = argparse.ArgumentParser(usage="Static Code Analyzer")
    parser.add_argument('folder', type=str, help="takes a single file or folder path")
    args = parser.parse_args()
    return args.folder


def get_sorted_files(path):
    """
    Get a sorted list of Python files from a specified directory or a single file.

    Args:
        path (str): Path to the directory or a Python file.

    Returns:
        list: Sorted list of file paths.

    Raises:
        Exception: If the specified path does not exist or is invalid.
    """
    if not os.path.exists(path):
        raise Exception(f'Path {path} does not exist')
    if not os.path.isdir(path):
        return [path]
    files = []
    for root, dirs, files_list in os.walk(path):
        for file in files_list:
            if file.endswith('.py'):
                files.append(os.path.join(root, file))
    files.sort()
    return files


def run_check_on_file(file_path):
    """
    Process a single file and perform all style and structural checks.

    Args:
        file_path (str): Path to the Python file to be checked.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        tree = ast.parse(content)
        lines = content.splitlines()
        blank_line = 0

        for i, line in enumerate(lines, start=1):
            run_line_checks(file_path, line, i)

            if not line.strip():
                blank_line += 1
            else:
                if blank_line > 2:
                    print(f'{file_path}: Line {i}: S006 More than two blank lines used before this line')
                blank_line = 0

        run_ast_checks(tree, file_path)


def run_line_checks(file_path, line, i):
    """
    Perform checks on a single line of Python code.

    Args:
        file_path (str): Path to the file currently being checked.
        line (str): The line of code to check.
        i (int): Line number in the file.
    """
    if len(line) > 79:
        print(f'{file_path}: Line {i}: S001 Too Long')

    if (len(line) - len(line.lstrip(' '))) % 4 != 0:
        print(f'{file_path}: Line {i}: S002 Indentation is not a multiple of four')

    if '#' in line and line.split('#')[0].strip().endswith(';'):
        print(f'{file_path}: Line {i}: S003 Unnecessary semicolon')

    if '#' not in line and line.strip().endswith(';'):
        print(f'{file_path}: Line {i}: S003 Unnecessary semicolon')

    if not line.startswith('#') and '#' in line and not line.split('#')[0].endswith('  '):
        print(f'{file_path}: Line {i}: S004 At least two spaces before inline comment required')

    if '#' in line and 'todo' in line.split('#')[1].lower():
        print(f'{file_path}: Line {i}: S005 TODO found')

    if regex_construction_spaces.match(line.lstrip()):
        keyword = 'def' if 'def' in line else 'class'
        print(f'{file_path}: Line {i}: S007 Too many spaces after {keyword}')

    if regex_camel_case.match(line.lstrip()):
        keyword = 'def' if 'def' in line else 'class'
        print(f'{file_path}: Line {i}: S007 Too many spaces after {keyword}')


def run_ast_checks(tree, file_path):
    """
    Performs checks on the abstract syntax tree (AST) representation of the Python file.

    Args:
        tree (ast.AST): The parsed AST object of the Python file.
        file_path (str): Path to the file currently being checked.
    """
    for element in ast.walk(tree):
        if isinstance(element, ast.ClassDef):
            class_name = element.name
            if not regex_camel_case.match(class_name):
                print(
                    f"{file_path}: Line {element.lineno}: S008 Class name '{class_name}' should be written in CamelCase")

        if isinstance(element, ast.FunctionDef):
            function_name = element.name
            arguments = element.args.args
            defaults = element.args.defaults
            default_start_index = len(arguments) - len(defaults)

            if not regex_snake_case.match(function_name):
                print(f"{file_path}: Line {element.lineno}: S009 Function name '{function_name}' should be written in snake_case")

            for index, arg in enumerate(arguments):
                arg_name = arg.arg
                if not regex_snake_case.match(arg_name):
                    print(f"{file_path}: Line {arg.lineno}: S010 Argument name '{arg_name}' should be written in snake_case")
                if index >= default_start_index:
                    default_value = defaults[index - default_start_index]
                    if isinstance(default_value, (ast.List, ast.Dict, ast.Set)):
                        print(f"{file_path}: Line {arg.lineno}: S012 The default argument value is mutable")
            for line in element.body:
                if isinstance(line, ast.Assign):
                    for target in line.targets:
                        if isinstance(target, ast.Name) and not regex_snake_case.match(target.id):
                            print(
                                f"{file_path}: Line {target.lineno}: S011 Variable name '{target.id}' should be written in snake_case")


if __name__ == '__main__':
    main()
