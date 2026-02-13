# Manual OAuth Flow for VPS/Remote Environments

## Problem

Current OAuth flow requires a local browser and a reachable `localhost:19280` callback server. On VPS/remote environments, neither is available, making authentication impossible without manual token configuration.

## Solution

Add `--manual` option to skip browser auto-open and local HTTP server. User authorizes in their own browser, copies the callback URL back, and the CLI parses it to complete the token exchange.

## Design

### 1. Core: `TickTickAuth` changes (`auth.py`)

**`start_auth_flow(self, scopes=None, manual=False)`**

When `manual=True`:
1. Generate auth URL with state parameter (CSRF protection)
2. Print URL to terminal (skip `webbrowser.open()`)
3. Prompt user to paste the callback URL (skip local HTTP server)
4. Parse code + validate state via `_parse_callback_url()`
5. Call `exchange_code_for_token()` as usual

**New method: `_parse_callback_url(self, url: str, expected_state: str) -> str`**
- Parse URL query parameters
- Extract `code` parameter (raise error if missing)
- Validate `state` matches `expected_state` (raise error if mismatch)
- Return the authorization code

### 2. MCP Server: AI Agent guided auth (`server.py`)

Two new MCP tools for in-conversation auth:

**`ticktick_auth_start() -> str`**
- Check for existing client_id/secret (config or env)
- If missing, return instructions to configure credentials
- Generate auth URL + state, cache state in module-level variable
- Return auth URL + instructions for the AI to relay to user

**`ticktick_auth_complete(callback_url: str) -> str`**
- Parse callback URL, extract code, validate cached state
- Exchange code for token
- Save to config, re-initialize `ticktick` client
- Return success/failure message

**Agent-guided flow:**
```
User: "show my tasks"
Tool: get_tasks → auth error
Tool: ticktick_auth_start() → returns auth URL
AI: "Open this link, authorize, paste the callback URL back"
User: "http://localhost:19280/callback?code=xxx&state=yyy"
Tool: ticktick_auth_complete(url) → success
Tool: get_tasks → returns data
```

### 3. CLI entry points

**`auth.py` — `setup_auth_cli()`**
- Add `--manual` argparse argument
- Pass to `auth.start_auth_flow(manual=args.manual)`

**`authenticate.py` — `main()`**
- Add `--manual` flag support
- Pass to `auth.start_auth_flow(manual=True)`

**Terminal interaction in manual mode:**
```
$ ticktick-auth --manual

Please open the following URL in your browser to authorize:
https://ticktick.com/oauth/authorize?client_id=xxx&...

After authorization, the browser will redirect to a page that won't load.
Copy the full URL from the address bar and paste it here:
> http://localhost:19280/callback?code=abc123&state=xyz

Authentication successful! Config saved to ~/.ticktick/config.json
```

## Files to modify

| File | Change |
|------|--------|
| `ticktick_mcp/src/auth.py` | Add `manual` param to `start_auth_flow`, add `_parse_callback_url` method |
| `ticktick_mcp/src/server.py` | Add `ticktick_auth_start` and `ticktick_auth_complete` MCP tools |
| `ticktick_mcp/authenticate.py` | Add `--manual` CLI flag |
