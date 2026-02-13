import pytest
from unittest.mock import patch, MagicMock
from ticktick_mcp.src.server import (
    get_projects,
    get_project_tasks,
    get_all_tasks,
    get_tasks_by_priority,
    get_tasks_due_today,
    get_overdue_tasks
)

@pytest.mark.asyncio
async def test_get_projects_pagination():
    """Test get_projects pagination logic."""
    mock_client = MagicMock()
    # Create 25 projects
    mock_projects = [{'id': f'proj_{i}', 'name': f'Project {i}'} for i in range(25)]
    mock_client.get_projects.return_value = mock_projects

    with patch('ticktick_mcp.src.server.ticktick', mock_client):
        # Test Page 1 (size 10) -> Should get 0-9
        result_p1 = await get_projects(size=10, page=1)
        assert "Found 25 projects" in result_p1
        assert "page 1/3" in result_p1
        assert "showing 1-10" in result_p1
        assert "Project 1:" in result_p1
        assert "Project 10:" in result_p1
        assert "Project 11:" not in result_p1
        assert "Use page=2 to see next page" in result_p1

        # Test Page 2 (size 10) -> Should get 10-19
        result_p2 = await get_projects(size=10, page=2)
        assert "page 2/3" in result_p2
        assert "showing 11-20" in result_p2
        assert "Project 11:" in result_p2
        assert "Project 20:" in result_p2
        assert "Use page=3 to see next page" in result_p2

        # Test Page 3 (size 10) -> Should get 20-24
        result_p3 = await get_projects(size=10, page=3)
        assert "page 3/3" in result_p3
        assert "showing 21-25" in result_p3
        assert "Project 21:" in result_p3
        assert "Project 25:" in result_p3
        assert "Use page=" not in result_p3  # No next page

        # Test Page Out of Range
        result_p4 = await get_projects(size=10, page=4)
        assert "Page 4 exceeds available pages (total: 3)" in result_p4

@pytest.mark.asyncio
async def test_get_project_tasks_pagination():
    """Test get_project_tasks pagination logic."""
    mock_client = MagicMock()
    # Create 15 tasks
    mock_tasks = [{'id': f'task_{i}', 'title': f'Task {i}', 'projectId': 'p1'} for i in range(15)]
    mock_client.get_project_with_data.return_value = {
        'project': {'name': 'Test Proj'},
        'tasks': mock_tasks
    }

    with patch('ticktick_mcp.src.server.ticktick', mock_client):
        # Page 1, Size 5 -> 1-5
        result = await get_project_tasks('p1', size=5, page=1)
        assert "Found 15 tasks" in result
        assert "page 1/3" in result
        assert "showing 1-5" in result
        assert "Task 1:" in result

        # Page 2, Size 5 -> 6-10
        result = await get_project_tasks('p1', size=5, page=2)
        assert "page 2/3" in result
        assert "showing 6-10" in result
        assert "Task 6:" in result

@pytest.mark.asyncio
async def test_filtered_tasks_pagination():
    """Test pagination in helper function via get_all_tasks."""
    mock_client = MagicMock()
    mock_projects = [{'id': 'p1', 'name': 'P1'}]
    # Create 12 tasks
    mock_tasks = [{'id': f't{i}', 'title': f'Task {i}', 'projectId': 'p1'} for i in range(12)]

    mock_client.get_projects.return_value = mock_projects
    mock_client.get_project_with_data.return_value = {
        'project': {'name': 'P1'},
        'tasks': mock_tasks
    }

    with patch('ticktick_mcp.src.server.ticktick', mock_client):
        # Test get_all_tasks with pagination
        # Page 1, size 5 -> 1-5
        res1 = await get_all_tasks(size=5, page=1)
        assert "Found 12 tasks" in res1
        assert "page 1/3" in res1
        assert "showing 1-5" in res1

        # Page 3, size 5 -> 11-12
        res3 = await get_all_tasks(size=5, page=3)
        assert "page 3/3" in res3
        assert "showing 11-12" in res3
        assert "Task 11:" in res3
        assert "Task 12:" in res3

@pytest.mark.asyncio
async def test_empty_results_pagination():
    """Test pagination with empty results."""
    mock_client = MagicMock()
    mock_client.get_projects.return_value = []

    with patch('ticktick_mcp.src.server.ticktick', mock_client):
        res = await get_projects(page=1)
        assert "No projects found" in res

@pytest.mark.asyncio
async def test_invalid_params():
    """Test invalid page/size parameters."""
    with patch('ticktick_mcp.src.server.ticktick', MagicMock()):
        assert await get_projects(page=0) == "Page must be at least 1."
        assert await get_projects(size=0) == "Size must be at least 1."
