# Coolify Manager — Agent Instructions

A single-file Python CLI for managing applications and services on a self-hosted [Coolify](https://coolify.io) instance via its REST API.

## Project layout

```
coolify-manager.py   # Entire application — one class + main()
requirements.txt     # Only dependency: requests>=2.31.0
.coolify_session.json  # Runtime-only; gitignored; stores URL + API token
```

## Run

```bash
pip install -r requirements.txt
python coolify-manager.py
```

No build step, no test suite, no package — it is a single executable script.

## Architecture

`CoolifyManager` (class) wraps all Coolify API calls:

| Method | Purpose |
|---|---|
| `fetch_resources()` | GET `/applications` + `/services`, merges into one list |
| `execute_action()` | Generic dispatcher for restart / stop / deploy / delete |
| `find_empty_projects()` | Walks projects → environments → resource counts |
| `delete_project()` | DELETE `/projects/{uuid}` |
| `stream_logs()` | Polls `/logs` every 2 s (not SSE) |
| `save_session()` / `load_session()` | Persist URL + token to `.coolify_session.json` |

`main()` is the interactive REPL loop: list resources → user picks indices or `all` → choose action → execute.

## Key conventions

- **Return style for API calls:** `(True, None)` on success, `(False, error_string)` on failure. Keep this pattern for any new API methods.
- **Pending deletions:** `self.pending_deletions` is a `set` of UUIDs deleted but not yet absent from the API. Always filter these out in `fetch_resources()`.
- **Destructive actions require a confirmation prompt** before executing — do not remove existing `input()` guards.
- **No external frameworks** — keep the dependency footprint at just `requests`.

## Pitfalls

- `.coolify_session.json` contains a plaintext API token. It must stay gitignored and must never be read or printed in full by agents.
- `stream_logs()` uses polling, not a real streaming response — latency is ~2 s per cycle by design.
- The Coolify API returns `200` *and* `204` for successful mutations; both must be treated as success (already handled in `execute_action`).
- Project resource counts must be fetched from the **environment detail** endpoint (`/projects/{uuid}/{env_name}`), not from the project list endpoint — the latter does not embed resource arrays.
