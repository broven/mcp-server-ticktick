import pytest
from unittest.mock import patch, MagicMock

from ticktick_mcp.src.server import get_projects, get_project_tasks, get_all_tasks, initialize_client


@pytest.mark.asyncio
async def test_get_projects_with_size_parameter():
    """Test that get_projects accepts and respects size parameter."""
    mock_client = MagicMock()
    mock_projects = [{'id': f'proj_{i}', 'name': f'Project {i}'} for i in range(100)]
    mock_client.get_projects.return_value = mock_projects

    with patch('ticktick_mcp.src.server.ticktick', mock_client):
        result = await get_projects(size=10)

    # Should indicate truncation and show only 10 projects
    assert "100 projects" in result
    assert "showing 1-10" in result


@pytest.mark.asyncio
async def test_get_projects_default_size():
    """Test that get_projects uses default size of 50."""
    mock_client = MagicMock()
    mock_projects = [{'id': f'proj_{i}', 'name': f'Project {i}'} for i in range(100)]
    mock_client.get_projects.return_value = mock_projects

    with patch('ticktick_mcp.src.server.ticktick', mock_client):
        result = await get_projects()

    # Should show default 50 and indicate truncation
    assert "100 projects" in result
    assert "showing 1-50" in result


@pytest.mark.asyncio
async def test_get_project_tasks_with_size_parameter():
    """Test that get_project_tasks accepts and respects size parameter."""
    mock_client = MagicMock()
    mock_tasks = [{'id': f'task_{i}', 'title': f'Task {i}', 'projectId': 'proj_1'} for i in range(100)]
    mock_client.get_project_with_data.return_value = {'project': {'name': 'Test Project'}, 'tasks': mock_tasks}

    with patch('ticktick_mcp.src.server.ticktick', mock_client):
        result = await get_project_tasks(project_id='proj_1', size=10)

    # Should indicate truncation
    assert "100 tasks" in result
    assert "showing 1-10" in result


@pytest.mark.asyncio
async def test_get_all_tasks_with_size_parameter():
    """Test that get_all_tasks accepts and respects size parameter."""
    mock_client = MagicMock()
    mock_projects = [{'id': 'proj_1', 'name': 'Project 1', 'closed': False}]
    mock_tasks = [{'id': f'task_{i}', 'title': f'Task {i}', 'projectId': 'proj_1'} for i in range(100)]
    mock_client.get_projects.return_value = mock_projects
    mock_client.get_project_with_data.return_value = {'project': {'name': 'Project 1'}, 'tasks': mock_tasks}

    with patch('ticktick_mcp.src.server.ticktick', mock_client):
        result = await get_all_tasks(size=10)

    # Should indicate truncation
    assert "showing 1-10" in result
