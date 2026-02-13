# Design: Pagination Support for List APIs

## Overview

Add pagination (`page`) support to all 12 list-type MCP tools to allow AI agents to navigate large datasets efficiently. Currently, these tools only support a `size` parameter which truncates results, making it impossible to access data beyond the first "page".

## Goals

1.  Enable full data access via pagination for all list endpoints.
2.  Maintain backward compatibility (default `page=1`).
3.  Provide clear navigation hints to the AI (e.g., "Use page=2 to see next page").
4.  Handle out-of-bounds page requests gracefully.

## Architecture

Since the TickTick Open API does **not** support server-side pagination (it returns full lists), pagination will be implemented client-side within the MCP server.

**Data Flow:**
1.  MCP Tool receives `size` and `page` arguments.
2.  Fetch **all** data from TickTick API.
3.  Calculate pagination metadata (total items, total pages).
4.  Slice the data list in Python: `start = (page-1) * size`, `end = start + size`.
5.  Format the result string with metadata and navigation hints.

## API Changes

All 12 list-type tools will be updated.

**New Parameter:**
-   `page: int = 1` (Default: 1, Min: 1)

**Affected Tools:**
1.  `get_projects`
2.  `get_project_tasks`
3.  `get_all_tasks`
4.  `get_tasks_by_priority`
5.  `get_tasks_due_today`
6.  `get_tasks_due_tomorrow`
7.  `get_tasks_due_in_days`
8.  `get_tasks_due_this_week`
9.  `get_overdue_tasks`
10. `search_tasks`
11. `get_engaged_tasks`
12. `get_next_tasks`

## Response Format

**Success (Page 1 of multiple):**
```text
Found 156 tasks in project 'Work' (page 1/4, showing 1-50):

Task 1:
...
Task 50:
...

Use page=2 to see next page.
```

**Success (Last Page):**
```text
Found 156 tasks in project 'Work' (page 4/4, showing 151-156):

Task 151:
...
Task 156:
...
```

**Error (Page out of range):**
```text
Page 5 exceeds available pages (total: 4). Use page=1 to page=4.
```

## Implementation Details

### Helper Function Update
The shared helper `_get_project_tasks_by_filter` will be updated to handle pagination logic centrally for the 10 task-filtering tools.

```python
def _get_project_tasks_by_filter(..., size: int = 50, page: int = 1) -> str:
    # ... fetch and filter ...
    total_pages = max(1, math.ceil(total_matched / size))

    if page > total_pages:
        return f"Page {page} exceeds available pages..."

    # Slice
    paginated = all_tasks[(page-1)*size : page*size]

    # Format
    # ...
```

### Validation
-   `size < 1` -> Error "Size must be at least 1."
-   `page < 1` -> Error "Page must be at least 1."

## Testing Strategy
-   Unit tests mocking TickTick client.
-   Verify default behavior (page=1).
-   Verify pagination slicing (page 1 vs page 2).
-   Verify out-of-bounds handling.
-   Verify "Next page" hint generation.
