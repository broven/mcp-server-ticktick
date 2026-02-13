# TickTick MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server for TickTick that enables interacting with your TickTick task management system directly through Claude and other MCP clients.

## Features

- 📋 View all your TickTick projects and tasks
- ✏️ Create new projects and tasks through natural language
- 🔄 Update existing task details (title, content, dates, priority)
- ✅ Mark tasks as complete
- 🗑️ Delete tasks and projects
- 🔄 Full integration with TickTick's open API
- 🔌 Seamless integration with Claude and other MCP clients

## Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer and resolver
- TickTick account with API access
- TickTick API credentials (Client ID and Client Secret from [TickTick Developer Center](https://developer.ticktick.com/manage))

## Installation

1. Register your application at the [TickTick Developer Center](https://developer.ticktick.com/manage)
   - Set the redirect URI to `http://localhost:19280/callback`
   - Note your Client ID and Client Secret

2. Add the MCP server configuration with your credentials:
   ```json
   {
     "mcpServers": {
       "ticktick": {
         "command": "uvx",
         "args": ["mcp-server-ticktick"],
         "env": {
           "TICKTICK_CLIENT_ID": "your_client_id",
           "TICKTICK_CLIENT_SECRET": "your_client_secret"
         }
       }
     }
   }
   ```

3. Run authentication to obtain access tokens:
   ```bash
   uvx mcp-server-ticktick auth
   ```
   This will open a browser for OAuth authorization. Credentials and tokens are saved to `~/.ticktick/config.json`.

> **Note:** If you don't configure `TICKTICK_CLIENT_ID` / `TICKTICK_CLIENT_SECRET` in the MCP config, the `auth` command will prompt you to enter them interactively, and they will be saved to `~/.ticktick/config.json`.

### Authentication with Dida365

[滴答清单 - Dida365](https://dida365.com/home) is China version of TickTick, and the authentication process is similar to TickTick. Follow these steps to set up Dida365 authentication:

1. Register your application at the [Dida365 Developer Center](https://developer.dida365.com/manage)
   - Set the redirect URI to `http://localhost:19280/callback`
   - Note your Client ID and Client Secret
2. Add the following MCP server configuration with Dida365 environment variables:
   ```json
   {
     "mcpServers": {
       "ticktick": {
         "command": "uvx",
         "args": ["mcp-server-ticktick"],
         "env": {
           "TICKTICK_CLIENT_ID": "your_client_id",
           "TICKTICK_CLIENT_SECRET": "your_client_secret",
           "TICKTICK_BASE_URL": "https://api.dida365.com/open/v1",
           "TICKTICK_AUTH_URL": "https://dida365.com/oauth/authorize",
           "TICKTICK_TOKEN_URL": "https://dida365.com/oauth/token"
         }
       }
     }
   }
   ```

3. Follow the same authentication steps as for TickTick

### Environment Variables

All environment variables are optional and can be set in your MCP server config's `env` block. Credentials and tokens are primarily stored in `~/.ticktick/config.json`.

| Variable | Description | Default |
|----------|-------------|---------|
| `TICKTICK_CLIENT_ID` | OAuth client ID | `~/.ticktick/config.json` |
| `TICKTICK_CLIENT_SECRET` | OAuth client secret | `~/.ticktick/config.json` |
| `TICKTICK_ACCESS_TOKEN` | OAuth access token (fallback) | `~/.ticktick/config.json` |
| `TICKTICK_REFRESH_TOKEN` | OAuth refresh token (fallback) | `~/.ticktick/config.json` |
| `TICKTICK_BASE_URL` | API base URL | `https://api.ticktick.com/open/v1` |
| `TICKTICK_AUTH_URL` | OAuth authorization URL | `https://ticktick.com/oauth/authorize` |
| `TICKTICK_TOKEN_URL` | OAuth token URL | `https://ticktick.com/oauth/token` |


## Available MCP Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `get_projects` | List all your TickTick projects | `size` (optional, default: 50) |
| `get_project` | Get details about a specific project | `project_id` |
| `get_project_tasks` | List all tasks in a project | `project_id`, `size` (optional, default: 50) |
| `get_task` | Get details about a specific task | `project_id`, `task_id` |
| `create_task` | Create a new task | `title`, `project_id`, `content` (optional), `start_date` (optional), `due_date` (optional), `priority` (optional) |
| `update_task` | Update an existing task | `task_id`, `project_id`, `title` (optional), `content` (optional), `start_date` (optional), `due_date` (optional), `priority` (optional) |
| `complete_task` | Mark a task as complete | `project_id`, `task_id` |
| `delete_task` | Delete a task | `project_id`, `task_id` |
| `create_project` | Create a new project | `name`, `color` (optional), `view_mode` (optional) |
| `delete_project` | Delete a project | `project_id` |

## Task-specific MCP Tools

### Task Retrieval & Search
| Tool | Description | Parameters |
|------|-------------|------------|
| `get_all_tasks` | Get all tasks from all projects | `size` (optional, default: 50) |
| `get_tasks_by_priority` | Get tasks filtered by priority level | `priority_id` (0: None, 1: Low, 3: Medium, 5: High), `size` (optional, default: 50) |
| `search_tasks` | Search tasks by title, content, or subtasks | `search_term`, `size` (optional, default: 50) |

### Date-Based Task Retrieval
| Tool | Description | Parameters |
|------|-------------|------------|
| `get_tasks_due_today` | Get all tasks due today | `size` (optional, default: 50) |
| `get_tasks_due_tomorrow` | Get all tasks due tomorrow | `size` (optional, default: 50) |
| `get_tasks_due_in_days` | Get tasks due in exactly X days | `days` (0 = today, 1 = tomorrow, etc.), `size` (optional, default: 50) |
| `get_tasks_due_this_week` | Get tasks due within the next 7 days | `size` (optional, default: 50) |
| `get_overdue_tasks` | Get all overdue tasks | `size` (optional, default: 50) |

### Getting Things Done (GTD) Framework
| Tool | Description | Parameters |
|------|-------------|------------|
| `get_engaged_tasks` | Get "engaged" tasks (high priority or overdue) | `size` (optional, default: 50) |
| `get_next_tasks` | Get "next" tasks (medium priority or due tomorrow) | `size` (optional, default: 50) |
| `batch_create_tasks` | Create multiple tasks at once | `tasks` (list of task dictionaries) |

## Example Prompts for Claude

Here are some example prompts to use with Claude after connecting the TickTick MCP server:

### General

- "Show me all my TickTick projects"
- "Create a new task called 'Finish MCP server documentation' in my work project with high priority"
- "List all tasks in my personal project"
- "Mark the task 'Buy groceries' as complete"
- "Create a new project called 'Vacation Planning' with a blue color"
- "When is my next deadline in TickTick?"

### Task Filtering Queries

- "What tasks do I have due today?"
- "Show me everything that's overdue"
- "Show me all tasks due this week"
- "Search for tasks about 'project alpha'"
- "Show me all tasks with 'client' in the title or description"
- "Show me all my high priority tasks"

### GTD Workflow

Following David Allen's "Getting Things Done" framework, manage an Engaged and Next actions.

- Engaged will retrieve tasks of high priority, due today or overdue.
- Next will retrieve medium priority or due tomorrow.
- Break down complex actions into smaller actions with batch_creation

For example:

- "Time block the rest of my day from 2-8pm with items from my engaged list"
- "Walk me through my next actions and help my identify what I should focus on tomorrow?" 
- "Break down this project into 5 smaller actionable tasks"

## Development

### Project Structure

```
mcp-server-ticktick/
├── README.md              # Project documentation
├── requirements.txt       # Project dependencies
├── setup.py               # Package setup file
├── test_server.py         # Test script for server configuration
└── ticktick_mcp/          # Main package
    ├── __init__.py        # Package initialization
    ├── authenticate.py    # OAuth authentication utility
    ├── cli.py             # Command-line interface
    └── src/               # Source code
        ├── __init__.py    # Module initialization
        ├── auth.py        # OAuth authentication implementation
        ├── server.py      # MCP server implementation
        └── ticktick_client.py  # TickTick API client
```

### Authentication Flow

The project implements a complete OAuth 2.0 flow for TickTick:

1. **Credential Loading**: Client ID and Secret are loaded from env vars (MCP config) or `~/.ticktick/config.json`
2. **Browser Authorization**: User is redirected to TickTick to grant access
3. **Token Reception**: A local server receives the OAuth callback with the authorization code
4. **Token Exchange**: The code is exchanged for access and refresh tokens
5. **Config Storage**: All credentials and tokens are securely stored in `~/.ticktick/config.json` (mode `0600`)
6. **Token Refresh**: The client automatically refreshes the access token when it expires

**Config loading priority:**
- Credentials (`client_id`, `client_secret`): MCP env vars → `~/.ticktick/config.json`
- Tokens (`access_token`, `refresh_token`): `~/.ticktick/config.json` → env vars (fallback)

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
