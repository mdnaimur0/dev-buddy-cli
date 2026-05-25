#!/bin/sh
# =============================================================================
#  buddy.sh - Dev Buddy CLI wrapper for bash / zsh / POSIX sh
#
#  This script defines a shell function 'buddy' that wraps main.py.
#  Because 'cd' in a child process cannot affect the parent shell, this
#  script MUST be sourced — exactly like how nvm, conda, and rvm work.
#
#  ┌─────────────────────────────────────────────────────────────────────┐
#  │  QUICK START                                                        │
#  │                                                                     │
#  │  One-time use:                                                      │
#  │    . ./buddy.sh              # source to load the 'buddy' function  │
#  │    buddy go <path>           # now use it                           │
#  │                                                                     │
#  │  Permanent setup — add to ~/.bashrc or ~/.zshrc:                    │
#  │    source /full/path/to/buddy.sh                                    │
#  │  Then just use:                                                     │
#  │    buddy go <path>                                                  │
#  │    buddy bookmarks                                                  │
#  │    buddy bookmark <name> [path]                                     │
#  │    buddy remove <name> | --all                                      │
#  │    buddy open [path]                                                │
#  │    buddy code [path]                                                │
#  └─────────────────────────────────────────────────────────────────────┘
#
#  Why can't this be a regular script?
#    In PowerShell, .\buddy.ps1 runs in the same process, so Set-Location
#    persists.  In Unix shells, ./buddy.sh spawns a child process — any 'cd'
#    inside it is lost when the child exits.  A shell function runs in
#    the current process, so 'cd' sticks.  This is the standard Unix
#    pattern used by nvm, conda, rvm, etc.
# =============================================================================

# --- Guard: abort if executed directly (bash detection) ----------------------
if [ -n "${BASH_SOURCE+x}" ] && [ "${BASH_SOURCE[0]}" = "$0" ]; then
    printf '\033[1;31mError:\033[0m This script must be sourced, not executed directly.\n\n' >&2
    printf '  \033[1mQuick start:\033[0m\n' >&2
    printf '    source %s\n' "$0" >&2
    printf '    buddy go <path>\n\n' >&2
    printf '  \033[1mPermanent setup\033[0m — add to ~/.bashrc:\n' >&2
    printf '    source %s/%s\n\n' "$(cd "$(dirname "$0")" && pwd)" "$(basename "$0")" >&2
    exit 1
fi

# --- Resolve the directory containing this script (and main.py) --------------
if [ -n "${BASH_SOURCE+x}" ]; then
    # bash: BASH_SOURCE is reliable when sourced
    # shellcheck disable=SC3054
    _BUDDY_INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
elif [ -n "${ZSH_VERSION+x}" ]; then
    # zsh: ${(%):-%x} expands to the current file path
    # shellcheck disable=SC3054
    _BUDDY_INSTALL_DIR="$(cd "$(dirname "${(%):-%x}")" && pwd)"
elif [ -f "$0" ]; then
    _BUDDY_INSTALL_DIR="$(cd "$(dirname "$0")" && pwd)"
else
    _BUDDY_INSTALL_DIR="$(pwd)"
fi

# --- Define the 'buddy' function ------------------------------------------------
buddy() {
    # Create a temp file for capturing stdout only.
    # stderr flows to the terminal so interactive menus are visible.
    _buddy_tmpfile="$(mktemp "${TMPDIR:-/tmp}/buddy_output.XXXXXX")"

    python -u "${_BUDDY_INSTALL_DIR}/main.py" "$@" > "${_buddy_tmpfile}"

    _buddy_last_line="$(tail -n 1 "${_buddy_tmpfile}")"

    case "${_buddy_last_line}" in
        GOTO:*)
            # Strip "GOTO:" prefix and trim whitespace
            _buddy_target="${_buddy_last_line#GOTO:}"
            _buddy_target="$(printf '%s' "${_buddy_target}" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"

            rm -f "${_buddy_tmpfile}"

            if [ -d "${_buddy_target}" ]; then
                cd "${_buddy_target}" || {
                    echo "Failed to change directory to: ${_buddy_target}" >&2
                    unset _buddy_tmpfile _buddy_last_line _buddy_target
                    return 1
                }
                echo "Changed directory to: ${_buddy_target}"
            else
                echo "Directory does not exist: ${_buddy_target}" >&2
                unset _buddy_tmpfile _buddy_last_line _buddy_target
                return 1
            fi
            ;;
        *)
            # No GOTO directive — print all captured stdout
            cat "${_buddy_tmpfile}"
            rm -f "${_buddy_tmpfile}"
            ;;
    esac

    unset _buddy_tmpfile _buddy_last_line _buddy_target
}
