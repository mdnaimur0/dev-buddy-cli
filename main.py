import argparse as ap
import sys
import os
import subprocess

from pathlib import Path


class Buddy:
    def __init__(self):
        self.bookmarks_file = Path.home() / ".dir_bookmarks.txt"

    def get_bookmarks(self) -> dict[str, str]:
        """Get all bookmarks as a dictionary."""
        bookmarks = {}
        if self.bookmarks_file.exists():
            try:
                with open(self.bookmarks_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and "=" in line:
                            name, path = line.split("=", 1)
                            bookmarks[name] = path
            except Exception:
                pass
        return bookmarks

    def resolve_path(self, path_or_name: str) -> Path:
        """Resolve a path or bookmark name to a Path object."""
        # First try as a direct path
        path = Path(path_or_name)
        if path.exists():
            return path.resolve()

        # Try to resolve as a bookmark
        bookmarks = self.get_bookmarks()
        if path_or_name in bookmarks:
            return Path(bookmarks[path_or_name])

        # Return as-is if not found (let the calling function handle errors)
        return path

    def get_directories(self, path: Path) -> list[Path]:
        """List all directories in the given path and return them."""
        if not path.exists():
            print(f"Path '{path}' does not exist.")
            return []

        if not path.is_dir():
            print(f"Path '{path}' is not a directory.")
            return []

        directories = []
        for item in sorted(path.iterdir()):
            if item.is_dir():
                directories.append(item)

        return directories

    def take_input_and_return_bm_or_dir(self, path: Path) -> Path | None:
        """Take user input to select a directory or bookmark."""
        bookmarks = self.get_bookmarks()
        directories = self.get_directories(path)

        if not directories and not bookmarks:
            print("No directories or bookmarks available.")
            return None

        message = ""

        # Display bookmarks first
        if bookmarks:
            message += "Bookmarks:\n"
            for i, (bm_name, bm_path) in enumerate(bookmarks.items(), 1):
                message += f"{i:2d}. {bm_name} -> {bm_path}\n"

        # Display directories
        if directories:
            message += "Directories:\n"
            start_index = len(bookmarks) + 1
            for i, directory in enumerate(directories, start_index):
                message += f"{i:2d}. {directory.name}\n"

        print(message, flush=True, file=sys.stderr)
        print("Enter your choice: ", end="", flush=True, file=sys.stderr)

        try:
            choice = sys.stdin.readline().strip()
            if not choice:
                print("No selection made.")
                return None

            choice_index = int(choice) - 1

            if choice_index < len(bookmarks):
                # It's a bookmark
                bm_name, bm_path = list(bookmarks.items())[choice_index]
                print(f"Selected bookmark: {bm_name} -> {bm_path}")
                return Path(bm_path)
            elif choice_index < len(bookmarks) + len(directories):
                # It's a directory
                directory = directories[choice_index - len(bookmarks)]
                print(f"Selected directory: {directory}")
                return directory
            else:
                print("Invalid selection.")
                return None
        except ValueError:
            print("Invalid input. Please enter a number.")
            return None

    def navigate_to_dir(self, path: Path) -> None:
        """Navigate to the specified directory by writing a batch file."""
        if not path.exists():
            print(f"Directory '{path}' does not exist.")
            return

        if not path.is_dir():
            print(f"Path '{path}' is not a directory.")
            return

        try:
            resolved_path = path.resolve()
            if not resolved_path.exists():
                print(f"Resolved path '{resolved_path}' does not exist.")
                return
            if not resolved_path.is_dir():
                print(f"Resolved path '{resolved_path}' is not a directory.")
                return
            print(f"GOTO: {resolved_path}")
        except Exception as e:
            print(f"Failed to prepare directory change: {e}")

    def open_dir_in_explorer(self, path: Path) -> None:
        """Open the specified directory in the file explorer."""
        if not path.exists():
            print(f"Directory '{path}' does not exist.")
            return

        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.run(["open", str(path)], check=True)
            else:
                subprocess.run(["xdg-open", str(path)], check=True)
        except Exception as e:
            print(f"Failed to open directory: {e}")

    def open_dir_in_vs_code(self, path: Path) -> None:
        """Open the specified directory in Visual Studio Code."""
        if not path.exists():
            print(f"Directory '{path}' does not exist.")
            return

        # Try different VS Code command variations
        vscode_commands = ["code", "code.exe", "code.cmd"]

        for cmd in vscode_commands:
            try:
                subprocess.run([cmd, str(path)], check=True)
                return
            except FileNotFoundError:
                continue
            except subprocess.CalledProcessError as e:
                print(f"VS Code command '{cmd}' failed with exit code {e.returncode}")
                continue
            except Exception as e:
                print(f"Error with command '{cmd}': {e}")
                continue

        print("Visual Studio Code is not installed or not in PATH.")
        print(
            "Please ensure VS Code is installed and 'code' command is available in PATH."
        )

    def bookmark_dir(self, short_name: str, path: Path) -> None:
        """Bookmark a directory with a short name."""
        if not path.exists():
            print(f"Directory '{path}' does not exist.")
            return

        if not path.is_dir():
            print(f"Path '{path}' is not a directory.")
            return

        # Check if bookmark already exists
        bookmarks = self.get_bookmarks()
        if short_name in bookmarks:
            print(f"'{short_name}' already exists. Points to: {bookmarks[short_name]}")
            return

        try:
            with open(self.bookmarks_file, "a") as f:
                f.write(f"{short_name}={path.resolve()}\n")
            print(f"Bookmarked '{path}' as '{short_name}'.")
        except Exception as e:
            print(f"Failed to bookmark directory: {e}")

    def list_bookmarks(self) -> None:
        """List all bookmarked directories."""
        bookmarks = self.get_bookmarks()
        if not bookmarks:
            print("No bookmarks found.")
            return

        print("Bookmarks:")
        for name, path in sorted(bookmarks.items()):
            status = "" if Path(path).exists() else "! "
            print(f" {status} {name}: {path}")

    def remove_bookmark(self, short_name: str) -> None:
        """Remove a bookmarked directory by its short name."""
        bookmarks = self.get_bookmarks()
        if not bookmarks:
            print("No bookmarks found.")
            return

        if short_name not in bookmarks:
            print(f"Bookmark '{short_name}' does not exist.")
            return

        try:
            # Rewrite the file without the specified bookmark
            with open(self.bookmarks_file, "w") as f:
                for name, path in bookmarks.items():
                    if name != short_name:
                        f.write(f"{name}={path}\n")

            print(f"Removed bookmark '{short_name}'.")
        except Exception as e:
            print(f"Failed to remove bookmark: {e}")

    def remove_all_bookmarks(self) -> None:
        """Remove all bookmarked directories."""
        if not self.bookmarks_file.exists():
            print("No bookmarks found.")
            return

        try:
            self.bookmarks_file.unlink()
            print("Removed all bookmarks.")
        except Exception as e:
            print(f"Failed to remove all bookmarks: {e}")


def parse_args() -> ap.Namespace:
    parser = ap.ArgumentParser(description="Dev Buddy CLI", prog='buddy')
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Bookmarks command (for listing bookmarks)
    bookmarks_parser = subparsers.add_parser("bookmarks", help="List all bookmarks")

    # Bookmark command
    bookmark_parser = subparsers.add_parser("bookmark", help="Bookmark a directory")
    bookmark_parser.add_argument("name", help="Short name for the bookmark")
    bookmark_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to bookmark (default: current directory)",
    )

    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove a bookmark")
    remove_parser.add_argument("name", nargs="?", help="Name of the bookmark to remove")
    remove_parser.add_argument(
        "--all", action="store_true", help="Remove all bookmarks"
    )

    # Go command (navigate like cd)
    go_parser = subparsers.add_parser("go", help="Navigate to a directory or bookmark")
    go_parser.add_argument(
        "path_or_name", nargs="?", help="Path, bookmark name to navigate to"
    )

    # Open command (open in explorer)
    open_parser = subparsers.add_parser("open", help="Open directory in file explorer")
    open_parser.add_argument(
        "path_or_name", nargs="?", help="Path or bookmark name to open"
    )

    # Code command (open in VS Code)
    code_parser = subparsers.add_parser("code", help="Open directory in VS Code")
    code_parser.add_argument(
        "path_or_name", nargs="?", help="Path or bookmark name to open in VS Code"
    )

    return parser.parse_args()


def main() -> None:
    buddy = Buddy()
    args = parse_args()

    if not args.command:
        print("No command specified. Use --help for usage information.")
        return

    try:
        if args.command == "bookmarks":
            buddy.list_bookmarks()

        elif args.command == "bookmark":
            path = buddy.resolve_path(args.path)
            buddy.bookmark_dir(args.name, path)

        elif args.command == "remove":
            if args.all:
                buddy.remove_all_bookmarks()
            elif args.name:
                buddy.remove_bookmark(args.name)
            else:
                print("Specify a bookmark name or use --all to remove all bookmarks.")

        elif args.command == "go":
            if args.path_or_name:
                path = buddy.resolve_path(args.path_or_name)
                buddy.navigate_to_dir(path)
            else:
                path = buddy.take_input_and_return_bm_or_dir(Path.cwd())
                if path:
                    buddy.navigate_to_dir(path)

        elif args.command == "open":
            if args.path_or_name:
                path = buddy.resolve_path(args.path_or_name)
                buddy.open_dir_in_explorer(path)
            else:
                path = buddy.take_input_and_return_bm_or_dir(Path.cwd())
                if path:
                    buddy.open_dir_in_explorer(path)

        elif args.command == "code":
            if args.path_or_name:
                path = buddy.resolve_path(args.path_or_name)
                buddy.open_dir_in_vs_code(path)
            else:
                path = buddy.take_input_and_return_bm_or_dir(Path.cwd())
                if path:
                    buddy.open_dir_in_vs_code(path)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
