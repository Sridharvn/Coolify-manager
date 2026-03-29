# Coolify Manager

A lightweight, interactive command-line tool for managing applications and services on a [Coolify](https://coolify.io) instance via its REST API. No dashboard required — list, restart, stop, deploy, delete resources, and clean up empty projects directly from your terminal.

---

## What It Does

- **Lists** all your Coolify applications and services in a single table with their current status
- **Selects** one, multiple (comma-separated), or all resources at once
- **Performs actions** — Restart, Stop, Deploy, Delete — on selected resources
- **Streams logs** for any resource directly in the terminal
- **Cleans up** empty Coolify projects (projects with no apps, services, or databases)
- **Saves your session** (URL + API token) so you don't have to re-enter credentials on every run

---

## Before You Run

### 1. Get Your Coolify URL

**Self-hosted Coolify:**
Your Coolify URL is the domain or IP address you used when setting it up, e.g.:
- `https://coolify.yourdomain.com`
- `http://192.168.1.100:8000`

**Coolify Cloud:**
Use `https://app.coolify.io`

### 2. Create an API Token

1. Log in to your Coolify dashboard
2. Click your **profile icon** → **Security** (or navigate to `/security/api-tokens`)
3. Click **"Create New Token"**
4. Give it a descriptive name (e.g., `coolify-manager-cli`)
5. Copy the token immediately — it will not be shown again

> **Security note:** The token is stored in `.coolify_session.json` in plaintext. This file is gitignored. Never commit it, share it, or print its contents.

---

## Setup & Run

**Requirements:** Python 3.8+ and `pip`

```bash
# Clone the repo
git clone https://github.com/Sridharvn/Coolify-manager.git
cd Coolify-manager

# Install dependencies
pip install -r requirements.txt

# Run
python coolify-manager.py
```

On first run you will be prompted for your Coolify URL and API token. You can choose to save them for future sessions.

---

## Usage

```
ID   | TYPE         | NAME                      | STATUS
--------------------------------------------------------------------
[0 ] | APPLICATIONS | my-web-app                | running
[1 ] | APPLICATIONS | api-server                | stopped
[2 ] | SERVICES     | postgres-db               | running

Commands: [numbers] Select | [all] Select All | [clean] Remove empty projects | [q] Quit
Input: _
```

### Selecting Resources

| Input | What it does |
|---|---|
| `0` | Select resource at index 0 |
| `0,2` | Select resources at indices 0 and 2 |
| `all` | Select every listed resource |

### Available Actions

After selecting resources, you will be prompted to choose an action:

| Key | Action | Notes |
|---|---|---|
| `r` | **Restart** | Restarts the selected resource(s) |
| `s` | **Stop** | Stops the selected resource(s) |
| `d` | **Deploy** | Triggers a fresh deployment |
| `l` | **Logs** | Streams live logs for the first selected resource |
| `rm` | **Delete** | Permanently deletes resource(s) — requires confirmation |

### Special Commands

| Command | What it does |
|---|---|
| `clean` | Scans all projects, finds ones with zero resources, and offers to delete them |
| `q` | Quit the application |

---

## Project Structure

```
coolify-manager.py     # Entire application — single file
requirements.txt       # Only dependency: requests>=2.31.0
.coolify_session.json  # Runtime-only session file (gitignored)
```

---

## Features

- Single-file, zero-framework CLI — easy to read, modify, and deploy anywhere
- Unified resource list merging applications and services into one view
- Bulk actions: apply restart/stop/deploy/delete to multiple resources in one step
- Session persistence — credentials saved locally, re-used on next run
- Intelligent pending-deletion tracking — deleted resources are immediately hidden even before Coolify's async deletion completes
- Empty project cleanup to remove stale Coolify projects

---

## Possible Features to Add

Contributions and ideas are welcome. Some directions worth exploring:

- **Real-time log streaming** via SSE instead of 2-second polling
- **Colorized output** using `colorama` or ANSI codes for status indicators
- **Filtering & search** — filter the resource list by name, type, or status
- **Non-interactive / scripted mode** — accept action flags via CLI arguments for automation
- **Start action** — complement Stop with a direct Start (currently not in the Coolify API's generic path)
- **Environment variable viewer/editor** — inspect or update env vars for a resource
- **Deployment history** — list past deployments for an app and redeploy a specific one
- **Database management** — start/stop/backup databases (PostgreSQL, MySQL, Redis, etc.)
- **Domain management** — list or add custom domains to applications
- **Multiple saved profiles** — switch between different Coolify instances easily
- **Output as JSON** — machine-readable output mode for piping into other tools

---

## Reporting Issues

Found a bug or want to request a feature? Please [open an issue](https://github.com/Sridharvn/Coolify-manager/issues) with the following information:

**For bugs:**
- Your Python version (`python --version`)
- The exact error message or unexpected behaviour
- Steps to reproduce
- Coolify version (visible in your dashboard footer)

**For feature requests:**
- Describe the problem you are trying to solve
- Describe the expected behaviour
- Any relevant Coolify API endpoints you know of (see [Coolify API docs](https://coolify.io/docs/api-reference/get-confirmation))

---

## License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2025 Sridhar V Nampoothiripad

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```
