#!/usr/bin/env python3
"""Verify size parameter implementation."""

import ast
import sys


def check_function_has_size_param(file_path, func_name):
    """Check if a function has size parameter."""
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())

    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == func_name:
            args = node.args
            for arg in args.args:
                if arg.arg == 'size':
                    return True
            for arg in args.kwonlyargs:
                if arg.arg == 'size':
                    return True
    return False


# List of functions that should have size parameter
functions_to_check = [
    'get_projects',
    'get_project_tasks',
    'get_all_tasks',
    'get_tasks_by_priority',
    'get_tasks_due_today',
    'get_tasks_due_tomorrow',
    'get_tasks_due_in_days',
    'get_tasks_due_this_week',
    'get_overdue_tasks',
    'search_tasks',
    'get_engaged_tasks',
    'get_next_tasks',
]

file_path = 'ticktick_mcp/src/server.py'

print("Checking size parameter implementation...")
print("=" * 50)

all_ok = True
for func in functions_to_check:
    has_param = check_function_has_size_param(file_path, func)
    status = "PASS" if has_param else "FAIL"
    print(f"[{status}] {func}")
    if not has_param:
        all_ok = False

print("=" * 50)
if all_ok:
    print("All functions have size parameter!")
    sys.exit(0)
else:
    print("Some functions are missing size parameter!")
    sys.exit(1)
