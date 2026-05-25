# Dev Buddy CLI

A small CLI to manage directory bookmarks and navigate quickly from the shell.

Files:
- [main.py](main.py): Primary Python CLI implementing bookmarks and navigation.
- [buddy.ps1](buddy.ps1): PowerShell wrapper that runs `main.py` and changes the PowerShell working directory when the script outputs a `GOTO: <path>` line.

Prerequisites
- Python 3.8+ on PATH (invoked as `python`).
- On Windows, PowerShell to use `buddy.ps1` for live directory changes.
- Optional: Visual Studio Code (`code` in PATH) for the `code` command.

Quick install
- Place the repository somewhere on your machine and ensure `python` is available.
- (Optional) Add the repository folder to your PATH or create shortcuts to `buddy.ps1`.

Usage
Run the CLI directly with Python:

```
python main.py <command> [args]
```

Or use the PowerShell wrapper (recommended on Windows) to let the script change your PowerShell session directory:

```
.\buddy.ps1 go <bookmark-or-path>
.\buddy.ps1 bookmarks
.\buddy.ps1 bookmark <name> [path]
.\buddy.ps1 remove <name>
.\buddy.ps1 remove --all
.\buddy.ps1 open <bookmark-or-path>
.\buddy.ps1 code <bookmark-or-path>
```

Commands (short)
- `bookmarks` — list saved bookmarks.
- `bookmark <name> [path]` — save a bookmark (default path is current directory).
- `remove <name>` — remove a bookmark. Use `--all` to remove all.
- `go [path|bookmark]` — print a `GOTO: <path>` line (PowerShell wrapper will change directory). If omitted, opens an interactive chooser.
- `open [path|bookmark]` — open the directory in the system file explorer.
- `code [path|bookmark]` — open the directory in VS Code (tries `code`, `code.exe`, `code.cmd`).

Interactive mode
- For commands that accept an optional path, omitting the argument presents an interactive selection of bookmarks and directories.

Bookmarks storage
- Bookmarks are stored in `~/.dir_bookmarks.txt` as `name=path` lines. See [main.py](main.py) for details.

How `buddy.ps1` works
- `buddy.ps1` runs `python -u main.py` forwarding arguments. If the last line printed by `main.py` starts with `GOTO:`, `buddy.ps1` extracts the path and runs PowerShell `Set-Location` to change the current shell directory.

Troubleshooting
- If the working directory doesn't change, ensure you run the PowerShell script from PowerShell (not `cmd`) and that script execution is allowed by your policy.
- Ensure `python` and optionally `code` are in your PATH.
- If `code` fails, open VS Code manually or add the `code` CLI via VS Code Command Palette → "Shell Command: Install 'code' command in PATH".

