# Dev Buddy CLI

Dev Buddy is a small bookmark-and-navigation CLI that helps you jump to saved directories, open them in your file manager, or launch them in VS Code.

## What’s Included

- [main.py](main.py): the Python CLI that stores bookmarks and prints `GOTO: <path>` for shell wrappers.
- [buddy.ps1](buddy.ps1): PowerShell wrapper for Windows PowerShell and PowerShell 7.
- [buddy.bat](buddy.bat): Windows CMD wrapper.
- [buddy.sh](buddy.sh): bash, zsh, and POSIX shell wrapper.

## Requirements

- Python 3.8+ available as `python`.
- Optional: VS Code if you want to use the `code` command.
- Windows users can use either CMD (`buddy.bat`) or PowerShell (`buddy.ps1`).
- Unix-like shells should source `buddy.sh` so the `cd` action affects the current shell.

## Setup

### Windows CMD

Run commands from the repository folder:

```
buddy.bat bookmarks
buddy.bat bookmark work C:\Projects\Work
buddy.bat go work
```

If you add the repository folder to your PATH, you can run `buddy` directly from CMD instead of typing `buddy.bat`.

### Windows PowerShell

Use the PowerShell wrapper from the repository folder:

```
.\buddy.ps1 bookmarks
.\buddy.ps1 bookmark work C:\Projects\Work
.\buddy.ps1 go work
```

The script prints `GOTO: <path>` from `main.py` and then changes the current PowerShell directory with `Set-Location`.

If the repository folder is on your PATH, you can also call `buddy` directly instead of `.\buddy.ps1`.

### bash / zsh / POSIX sh

Source the shell wrapper once per session, or add it to your shell profile:

```
. ./buddy.sh
buddy bookmarks
buddy bookmark work ~/Projects/Work
buddy go work
```

For permanent setup, add a line like this to `~/.bashrc`, `~/.zshrc`, or your shell profile:

```
source /full/path/to/dev_buddy_cli/buddy.sh
```

If the repository folder is on your PATH, sourcing `buddy.sh` once gives you a plain `buddy` command in that shell session.

## Commands

- `bookmarks` - list saved bookmarks.
- `bookmark <name> [path]` - save the given path or current directory under a short name.
- `remove <name>` - remove one bookmark, or `remove --all` to delete them all.
- `go [path|bookmark]` - navigate to a path or bookmark. If omitted, an interactive chooser appears.
- `open [path|bookmark]` - open the directory in your system file explorer.
- `code [path|bookmark]` - open the directory in VS Code.

## Behavior Notes

- Bookmarks are stored in `~/.dir_bookmarks.txt` as `name=path` entries.
- `main.py` resolves either direct paths or bookmark names.
- If a command is run without a path, the CLI shows bookmarked entries and child directories so you can pick one interactively.

## Troubleshooting

- If directory changes do not persist, make sure you are using the shell-specific wrapper for your shell.
- If VS Code cannot open, confirm that `code` is installed and on PATH.
- If Windows script execution is restricted, allow PowerShell scripts for your session or policy.

