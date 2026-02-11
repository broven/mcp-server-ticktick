# Add Size Parameter to List APIs Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a `size` parameter to all list-related MCP tools to limit the number of returned items, preventing AI context explosion when users have many tasks or projects.

**Architecture:**
- Add optional `size` parameter (default: 50, max: 200) to all list-returning MCP tools
- Implement truncation logic in the `_get_project_tasks_by_filter` helper function
- Add size limiting to `get_projects()` and `get_project_tasks()` tools
- Return a warning message when results are truncated so users know data was limited

**Tech Stack:** Python, FastMCP, TickTick API

---

## Overview of Changes

The following MCP tools need the `size` parameter added:

1. `get_projects()` - Returns list of projects
2. `get_project_tasks(project_id)` - Returns tasks in a project
3. `get_all_tasks()` - Returns all tasks across all projects
4. `get_tasks_by_priority(priority_id)` - Returns tasks filtered by priority
5. `get_tasks_due_today()` - Returns tasks due today
6. `get_tasks_due_tomorrow()` - Returns tasks due tomorrow
7. `get_tasks_due_in_days(days)` - Returns tasks due in X days
8. `get_tasks_due_this_week()` - Returns tasks due within 7 days
9. `get_overdue_tasks()` - Returns overdue tasks
10. `search_tasks(search_term)` - Returns tasks matching search
11. `get_engaged_tasks()` - Returns high priority/due today/overdue tasks
12. `get_next_tasks()` - Returns medium priority/due tomorrow tasks

---

## Task 1: Add Size Parameter to `get_projects()` Tool

**Files:**
- Modify: `ticktick_mcp/src/server.py:115-137`

**Step 1: Write the failing test**

Create test file `tests/test_size_parameter.py`:

```python
import pytest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ticktick_mcp', 'src'))

from server import get_projects, initialize_client

@pytest.mark.asyncio
async def test_get_projects_with_size_parameter():
    """Test that get_projects accepts and respects size parameter."""
    # Mock the ticktick client
    mock_client = MagicMock()
    mock_projects = [{'id': f'proj_{i}', 'name': f'Project {i}'} for i in range(100)]
    mock_client.get_projects.return_value = mock_projects

    with patch('server.ticktick', mock_client):
        result = await get_projects(size=10)

    # Should only show 10 projects
    assert "Found 10 projects" in result or "Showing 10 of 100 projects" in result
    # Should not show project 11
    assert "Project 11:" not in result

@pytest.mark.asyncio
async def test_get_projects_default_size():
    """Test that get_projects uses default size of 50."""
    mock_client = MagicMock()
    mock_projects = [{'id': f'proj_{i}', 'name': f'Project {i}'} for i in range(100)]
    mock_client.get_projects.return_value = mock_projects

    with patch('server.ticktick', mock_client):
        result = await get_projects()

    # Should show default 50 projects
    assert "Found 50 projects" in result or "Showing 50 of 100 projects" in result
```

**Step 2: Run test to verify it fails**

```bash
cd /Users/metajs/conductor/workspaces/ticktick-cli/luxembourg
python -m pytest tests/test_size_parameter.py::test_get_projects_with_size_parameter -v
```

Expected: FAIL with "unexpected keyword argument 'size'"

**Step 3: Implement size parameter in `get_projects()`**

Modify `ticktick_mcp/src/server.py` line 115-137:

```python
@mcp.tool()
async def get_projects(size: int = 50) -> str:
    """
    Get all projects from TickTick.

    Args:
        size: Maximum number of projects to return (default: 50, max: 200)
    """
    if not ticktick:
        if not initialize_client():
            return "Failed to initialize TickTick client. Please check your API credentials."

    # Validate size parameter
    if size < 1:
        return "Size must be at least 1."
    if size > 200:
        size = 200

    try:
        projects = ticktick.get_projects()
        if 'error' in projects:
            return f"Error fetching projects: {projects['error']}"

        if not projects:
            return "No projects found."

        total_projects = len(projects)
        truncated_projects = projects[:size]

        result = f"Found {total_projects} projects"
        if total_projects > size:
            result += f" (showing first {size})"
        result += ":\n\n"

        for i, project in enumerate(truncated_projects, 1):
            result += f"Project {i}:\n" + format_project(project) + "\n"

        return result
    except Exception as e:
        logger.error(f"Error in get_projects: {e}")
        return f"Error retrieving projects: {str(e)}"
```

**Step 4: Run test to verify it passes**

```bash
python -m pytest tests/test_size_parameter.py::test_get_projects_with_size_parameter -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add ticktick_mcp/src/server.py tests/test_size_parameter.py
git commit -m "feat: add size parameter to get_projects() tool"
```

---

## Task 2: Add Size Parameter to `get_project_tasks()` Tool

**Files:**
- Modify: `ticktick_mcp/src/server.py:161-189`

**Step 1: Write the failing test**

Add to `tests/test_size_parameter.py`:

```python
@pytest.mark.asyncio
async def test_get_project_tasks_with_size_parameter():
    """Test that get_project_tasks accepts and respects size parameter."""
    mock_client = MagicMock()
    mock_tasks = [{'id': f'task_{i}', 'title': f'Task {i}', 'projectId': 'proj_1'} for i in range(100)]
    mock_client.get_project_with_data.return_value = {'project': {'name': 'Test Project'}, 'tasks': mock_tasks}

    with patch('server.ticktick', mock_client):
        result = await get_project_tasks(project_id='proj_1', size=10)

    # Should only show 10 tasks
    assert "Found 100 tasks" in result or "showing first 10" in result
```

**Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_size_parameter.py::test_get_project_tasks_with_size_parameter -v
```

Expected: FAIL

**Step 3: Implement size parameter in `get_project_tasks()`**

Modify `ticktick_mcp/src/server.py` line 161-189:

```python
@mcp.tool()
async def get_project_tasks(project_id: str, size: int = 50) -> str:
    """
    Get all tasks in a specific project.

    Args:
        project_id: ID of the project
        size: Maximum number of tasks to return (default: 50, max: 200)
    """
    if not ticktick:
        if not initialize_client():
            return "Failed to initialize TickTick client. Please check your API credentials."

    # Validate size parameter
    if size < 1:
        return "Size must be at least 1."
    if size > 200:
        size = 200

    try:
        project_data = ticktick.get_project_with_data(project_id)
        if 'error' in project_data:
            return f"Error fetching project data: {project_data['error']}"

        tasks = project_data.get('tasks', [])
        if not tasks:
            return f"No tasks found in project '{project_data.get('project', {}).get('name', project_id)}'."

        total_tasks = len(tasks)
        truncated_tasks = tasks[:size]

        result = f"Found {total_tasks} tasks in project '{project_data.get('project', {}).get('name', project_id)}'"
        if total_tasks > size:
            result += f" (showing first {size})"
        result += ":\n\n"

        for i, task in enumerate(truncated_tasks, 1):
            result += f"Task {i}:\n" + format_task(task) + "\n"

        return result
    except Exception as e:
        logger.error(f"Error in get_project_tasks: {e}")
        return f"Error retrieving project tasks: {str(e)}"
```

**Step 4: Run test to verify it passes**

```bash
python -m pytest tests/test_size_parameter.py::test_get_project_tasks_with_size_parameter -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add ticktick_mcp/src/server.py tests/test_size_parameter.py
git commit -m "feat: add size parameter to get_project_tasks() tool"
```

---

## Task 3: Update `_get_project_tasks_by_filter()` Helper Function

**Files:**
- Modify: `ticktick_mcp/src/server.py:538-579`

**Step 1: Write the failing test**

Add to `tests/test_size_parameter.py`:

```python
@pytest.mark.asyncio
async def test_get_all_tasks_with_size_parameter():
    """Test that get_all_tasks accepts and respects size parameter."""
    mock_client = MagicMock()
    mock_projects = [{'id': 'proj_1', 'name': 'Project 1', 'closed': False}]
    mock_tasks = [{'id': f'task_{i}', 'title': f'Task {i}', 'projectId': 'proj_1'} for i in range(100)]
    mock_client.get_projects.return_value = mock_projects
    mock_client.get_project_with_data.return_value = {'project': {'name': 'Project 1'}, 'tasks': mock_tasks}

    with patch('server.ticktick', mock_client):
        result = await get_all_tasks(size=10)

    # Should indicate truncation
    assert "showing first" in result.lower() or "10" in result
```

**Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_size_parameter.py::test_get_all_tasks_with_size_parameter -v
```

Expected: FAIL

**Step 3: Update helper function and all filter-based tools**

Modify `ticktick_mcp/src/server.py` line 538-579:

```python
def _get_project_tasks_by_filter(projects: List[Dict], filter_func, filter_name: str, size: int = 50) -> str:
    """
    Helper function to filter tasks across all projects.

    Args:
        projects: List of project dictionaries
        filter_func: Function that takes a task and returns True if it matches the filter
        filter_name: Name of the filter for output formatting
        size: Maximum number of tasks to return (default: 50, max: 200)

    Returns:
        Formatted string of filtered tasks
    """
    # Validate size parameter
    if size < 1:
        size = 1
    if size > 200:
        size = 200

    if not projects:
        return "No projects found."

    result = f"Found {len(projects)} projects:\n\n"
    total_matched_tasks = 0
    all_filtered_tasks = []

    # First pass: collect all matching tasks
    for project in projects:
        if project.get('closed'):
            continue

        project_id = project.get('id', 'No ID')
        project_data = ticktick.get_project_with_data(project_id)
        tasks = project_data.get('tasks', [])

        # Filter tasks using the provided function
        for task in tasks:
            if filter_func(task):
                all_filtered_tasks.append((project, task))

    total_matched_tasks = len(all_filtered_tasks)

    # Apply size limit
    if total_matched_tasks > size:
        result = f"Found {total_matched_tasks} tasks matching '{filter_name}' (showing first {size}):\n\n"
        all_filtered_tasks = all_filtered_tasks[:size]
    else:
        result = f"Found {total_matched_tasks} tasks matching '{filter_name}':\n\n"

    # Group tasks by project for display
    current_project = None
    task_counter = 0

    for project, task in all_filtered_tasks:
        if project != current_project:
            current_project = project
            result += f"Project: {format_project(project)}\n"

        task_counter += 1
        result += f"Task {task_counter}:\n{format_task(task)}\n"

    return result
```

**Step 4: Update `get_all_tasks()` to accept size parameter**

Modify `ticktick_mcp/src/server.py` line 583-602:

```python
@mcp.tool()
async def get_all_tasks(size: int = 50) -> str:
    """
    Get all tasks from TickTick. Ignores closed projects.

    Args:
        size: Maximum number of tasks to return (default: 50, max: 200)
    """
    if not ticktick:
        if not initialize_client():
            return "Failed to initialize TickTick client. Please check your API credentials."

    # Validate size parameter
    if size < 1:
        return "Size must be at least 1."
    if size > 200:
        size = 200

    try:
        projects = ticktick.get_projects()
        if 'error' in projects:
            return f"Error fetching projects: {projects['error']}"

        def all_tasks_filter(task: Dict[str, Any]) -> bool:
            return True  # Include all tasks

        return _get_project_tasks_by_filter(projects, all_tasks_filter, "included", size)

    except Exception as e:
        logger.error(f"Error in get_all_tasks: {e}")
        return f"Error retrieving projects: {str(e)}"
```

**Step 5: Run test to verify it passes**

```bash
python -m pytest tests/test_size_parameter.py::test_get_all_tasks_with_size_parameter -v
```

Expected: PASS

**Step 6: Commit**

```bash
git add ticktick_mcp/src/server.py tests/test_size_parameter.py
git commit -m "feat: add size parameter to _get_project_tasks_by_filter helper and get_all_tasks()"
```

---

## Task 4: Add Size Parameter to All Filter-Based Task Tools

**Files:**
- Modify: `ticktick_mcp/src/server.py:604-785` (multiple tools)

**Step 1: Update `get_tasks_by_priority()`**

Modify `ticktick_mcp/src/server.py:604-632`:

```python
@mcp.tool()
async def get_tasks_by_priority(priority_id: int, size: int = 50) -> str:
    """
    Get all tasks from TickTick by priority. Ignores closed projects.

    Args:
        priority_id: Priority of tasks to retrieve {0: "None", 1: "Low", 3: "Medium", 5: "High"}
        size: Maximum number of tasks to return (default: 50, max: 200)
    """
    if not ticktick:
        if not initialize_client():
            return "Failed to initialize TickTick client. Please check your API credentials."

    if priority_id not in PRIORITY_MAP:
        return f"Invalid priority_id. Valid values: {list(PRIORITY_MAP.keys())}"

    # Validate size parameter
    if size < 1:
        return "Size must be at least 1."
    if size > 200:
        size = 200

    try:
        projects = ticktick.get_projects()
        if 'error' in projects:
            return f"Error fetching projects: {projects['error']}"

        def priority_filter(task: Dict[str, Any]) -> bool:
            return task.get('priority', 0) == priority_id

        priority_name = f"{PRIORITY_MAP[priority_id]} ({priority_id})"
        return _get_project_tasks_by_filter(projects, priority_filter, f"priority '{priority_name}'", size)

    except Exception as e:
        logger.error(f"Error in get_tasks_by_priority: {e}")
        return f"Error retrieving projects: {str(e)}"
```

**Step 2: Update `get_tasks_due_today()`**

Modify `ticktick_mcp/src/server.py:634-653`:

```python
@mcp.tool()
async def get_tasks_due_today(size: int = 50) -> str:
    """
    Get all tasks from TickTick that are due today. Ignores closed projects.

    Args:
        size: Maximum number of tasks to return (default: 50, max: 200)
    """
    if not ticktick:
        if not initialize_client():
            return "Failed to initialize TickTick client. Please check your API credentials."

    # Validate size parameter
    if size < 1:
        return "Size must be at least 1."
    if size > 200:
        size = 200

    try:
        projects = ticktick.get_projects()
        if 'error' in projects:
            return f"Error fetching projects: {projects['error']}"

        def today_filter(task: Dict[str, Any]) -> bool:
            return _is_task_due_today(task)

        return _get_project_tasks_by_filter(projects, today_filter, "due today", size)

    except Exception as e:
        logger.error(f"Error in get_tasks_due_today: {e}")
        return f"Error retrieving projects: {str(e)}"
```

**Step 3: Update `get_overdue_tasks()`**

Modify `ticktick_mcp/src/server.py:655-674`:

```python
@mcp.tool()
async def get_overdue_tasks(size: int = 50) -> str:
    """
    Get all overdue tasks from TickTick. Ignores closed projects.

    Args:
        size: Maximum number of tasks to return (default: 50, max: 200)
    """
    if not ticktick:
        if not initialize_client():
            return "Failed to initialize TickTick client. Please check your API credentials."

    # Validate size parameter
    if size < 1:
        return "Size must be at least 1."
    if size > 200:
        size = 200

    try:
        projects = ticktick.get_projects()
        if 'error' in projects:
            return f"Error fetching projects: {projects['error']}"

        def overdue_filter(task: Dict[str, Any]) -> bool:
            return _is_task_overdue(task)

        return _get_project_tasks_by_filter(projects, overdue_filter, "overdue", size)

    except Exception as e:
        logger.error(f"Error in get_overdue_tasks: {e}")
        return f"Error retrieving projects: {str(e)}"
```

**Step 4: Update `get_tasks_due_tomorrow()`**

Modify `ticktick_mcp/src/server.py:676-695`:

```python
@mcp.tool()
async def get_tasks_due_tomorrow(size: int = 50) -> str:
    """
    Get all tasks from TickTick that are due tomorrow. Ignores closed projects.

    Args:
        size: Maximum number of tasks to return (default: 50, max: 200)
    """
    if not ticktick:
        if not initialize_client():
            return "Failed to initialize TickTick client. Please check your API credentials."

    # Validate size parameter
    if size < 1:
        return "Size must be at least 1."
    if size > 200:
        size = 200

    try:
        projects = ticktick.get_projects()
        if 'error' in projects:
            return f"Error fetching projects: {projects['error']}"

        def tomorrow_filter(task: Dict[str, Any]) -> bool:
            return _is_task_due_in_days(task, 1)

        return _get_project_tasks_by_filter(projects, tomorrow_filter, "due tomorrow", size)

    except Exception as e:
        logger.error(f"Error in get_tasks_due_tomorrow: {e}")
        return f"Error retrieving projects: {str(e)}"
```

**Step 5: Update `get_tasks_due_in_days()`**

Modify `ticktick_mcp/src/server.py:697-726`:

```python
@mcp.tool()
async def get_tasks_due_in_days(days: int, size: int = 50) -> str:
    """
    Get all tasks from TickTick that are due in exactly X days. Ignores closed projects.

    Args:
        days: Number of days from today (0 = today, 1 = tomorrow, etc.)
        size: Maximum number of tasks to return (default: 50, max: 200)
    """
    if not ticktick:
        if not initialize_client():
            return "Failed to initialize TickTick client. Please check your API credentials."

    if days < 0:
        return "Days must be a non-negative integer."

    # Validate size parameter
    if size < 1:
        return "Size must be at least 1."
    if size > 200:
        size = 200

    try:
        projects = ticktick.get_projects()
        if 'error' in projects:
            return f"Error fetching projects: {projects['error']}"

        def days_filter(task: Dict[str, Any]) -> bool:
            return _is_task_due_in_days(task, days)

        day_description = "today" if days == 0 else f"in {days} day{'s' if days != 1 else ''}"
        return _get_project_tasks_by_filter(projects, days_filter, f"due {day_description}", size)

    except Exception as e:
        logger.error(f"Error in get_tasks_due_in_days: {e}")
        return f"Error retrieving projects: {str(e)}"
```

**Step 6: Update `get_tasks_due_this_week()`**

Modify `ticktick_mcp/src/server.py:728-757`:

```python
@mcp.tool()
async def get_tasks_due_this_week(size: int = 50) -> str:
    """
    Get all tasks from TickTick that are due within the next 7 days. Ignores closed projects.

    Args:
        size: Maximum number of tasks to return (default: 50, max: 200)
    """
    if not ticktick:
        if not initialize_client():
            return "Failed to initialize TickTick client. Please check your API credentials."

    # Validate size parameter
    if size < 1:
        return "Size must be at least 1."
    if size > 200:
        size = 200

    try:
        projects = ticktick.get_projects()
        if 'error' in projects:
            return f"Error fetching projects: {projects['error']}"

        def week_filter(task: Dict[str, Any]) -> bool:
            due_date = task.get('dueDate')
            if not due_date:
                return False

            try:
                task_due_date = datetime.strptime(due_date, "%Y-%m-%dT%H:%M:%S.%f%z").date()
                today = datetime.now(timezone.utc).date()
                week_from_today = today + timedelta(days=7)
                return today <= task_due_date <= week_from_today
            except (ValueError, TypeError):
                return False

        return _get_project_tasks_by_filter(projects, week_filter, "due this week", size)

    except Exception as e:
        logger.error(f"Error in get_tasks_due_this_week: {e}")
        return f"Error retrieving projects: {str(e)}"
```

**Step 7: Update `search_tasks()`**

Modify `ticktick_mcp/src/server.py:759-786`:

```python
@mcp.tool()
async def search_tasks(search_term: str, size: int = 50) -> str:
    """
    Search for tasks in TickTick by title, content, or subtask titles. Ignores closed projects.

    Args:
        search_term: Text to search for (case-insensitive)
        size: Maximum number of tasks to return (default: 50, max: 200)
    """
    if not ticktick:
        if not initialize_client():
            return "Failed to initialize TickTick client. Please check your API credentials."

    if not search_term.strip():
        return "Search term cannot be empty."

    # Validate size parameter
    if size < 1:
        return "Size must be at least 1."
    if size > 200:
        size = 200

    try:
        projects = ticktick.get_projects()
        if 'error' in projects:
            return f"Error fetching projects: {projects['error']}"

        def search_filter(task: Dict[str, Any]) -> bool:
            return _task_matches_search(task, search_term)

        return _get_project_tasks_by_filter(projects, search_filter, f"matching '{search_term}'", size)

    except Exception as e:
        logger.error(f"Error in search_tasks: {e}")
        return f"Error retrieving projects: {str(e)}"
```

**Step 8: Commit**

```bash
git add ticktick_mcp/src/server.py
git commit -m "feat: add size parameter to all filter-based task tools"
```

---

## Task 5: Add Size Parameter to GTD Tools

**Files:**
- Modify: `ticktick_mcp/src/server.py:888-939`

**Step 1: Update `get_engaged_tasks()`**

Modify `ticktick_mcp/src/server.py:888-914`:

```python
@mcp.tool()
async def get_engaged_tasks(size: int = 50) -> str:
    """
    Get all tasks from TickTick that are "Engaged".
    This includes tasks marked as high priority (5), due today or overdue.

    Args:
        size: Maximum number of tasks to return (default: 50, max: 200)
    """
    if not ticktick:
        if not initialize_client():
            return "Failed to initialize TickTick client. Please check your API credentials."

    # Validate size parameter
    if size < 1:
        return "Size must be at least 1."
    if size > 200:
        size = 200

    try:
        projects = ticktick.get_projects()
        if 'error' in projects:
            return f"Error fetching projects: {projects['error']}"

        def engaged_filter(task: Dict[str, Any]) -> bool:
            is_high_priority = task.get('priority', 0) == 5
            is_overdue = _is_task_overdue(task)
            is_today = _is_task_due_today(task)
            return is_high_priority or is_overdue or is_today

        return _get_project_tasks_by_filter(projects, engaged_filter, "engaged", size)

    except Exception as e:
        logger.error(f"Error in get_engaged_tasks: {e}")
        return f"Error retrieving projects: {str(e)}"
```

**Step 2: Update `get_next_tasks()`**

Modify `ticktick_mcp/src/server.py:916-939`:

```python
@mcp.tool()
async def get_next_tasks(size: int = 50) -> str:
    """
    Get all tasks from TickTick that are "Next".
    This includes tasks marked as medium priority (3) or due tomorrow.

    Args:
        size: Maximum number of tasks to return (default: 50, max: 200)
    """
    if not ticktick:
        if not initialize_client():
            return "Failed to initialize TickTick client. Please check your API credentials."

    # Validate size parameter
    if size < 1:
        return "Size must be at least 1."
    if size > 200:
        size = 200

    try:
        projects = ticktick.get_projects()
        if 'error' in projects:
            return f"Error fetching projects: {projects['error']}"

        def next_filter(task: Dict[str, Any]) -> bool:
            is_medium_priority = task.get('priority', 0) == 3
            is_due_tomorrow = _is_task_due_in_days(task, 1)
            return is_medium_priority or is_due_tomorrow

        return _get_project_tasks_by_filter(projects, next_filter, "next", size)

    except Exception as e:
        logger.error(f"Error in get_next_tasks: {e}")
        return f"Error retrieving projects: {str(e)}"
```

**Step 3: Run all tests**

```bash
python -m pytest tests/test_size_parameter.py -v
```

Expected: All tests PASS

**Step 4: Commit**

```bash
git add ticktick_mcp/src/server.py
git commit -m "feat: add size parameter to GTD tools (get_engaged_tasks, get_next_tasks)"
```

---

## Task 6: Run Full Test Suite and Verify

**Step 1: Run all existing tests to ensure no regressions**

```bash
python -m pytest tests/ -v --tb=short
```

Expected: All tests pass

**Step 2: Manual verification of the implementation**

Create a simple verification script `verify_size_param.py`:

```python
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
    status = "✅" if has_param else "❌"
    print(f"{status} {func}")
    if not has_param:
        all_ok = False

print("=" * 50)
if all_ok:
    print("All functions have size parameter!")
    sys.exit(0)
else:
    print("Some functions are missing size parameter!")
    sys.exit(1)
```

Run the verification:

```bash
python verify_size_param.py
```

Expected: All functions have size parameter

**Step 3: Final commit**

```bash
git add verify_size_param.py
git commit -m "chore: add size parameter verification script"
```

---

## Summary

All list-related MCP tools now have a `size` parameter:

| Tool | Default Size | Max Size |
|------|-------------|----------|
| `get_projects()` | 50 | 200 |
| `get_project_tasks()` | 50 | 200 |
| `get_all_tasks()` | 50 | 200 |
| `get_tasks_by_priority()` | 50 | 200 |
| `get_tasks_due_today()` | 50 | 200 |
| `get_tasks_due_tomorrow()` | 50 | 200 |
| `get_tasks_due_in_days()` | 50 | 200 |
| `get_tasks_due_this_week()` | 50 | 200 |
| `get_overdue_tasks()` | 50 | 200 |
| `search_tasks()` | 50 | 200 |
| `get_engaged_tasks()` | 50 | 200 |
| `get_next_tasks()` | 50 | 200 |

The implementation:
1. Validates the size parameter (min: 1, max: 200)
2. Truncates results when they exceed the size limit
3. Shows a message indicating when results were truncated
4. Is backward compatible (size defaults to 50)
