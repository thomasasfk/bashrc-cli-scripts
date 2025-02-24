#!/usr/bin/env python3.13

from pathlib import Path
import argparse
import logging
import os
import textwrap
import shutil
import subprocess
import time

from gemini import GeminiClient


def _git_command(file_path: Path, command: list[str]) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=file_path.parent,
            check=False
        )
        return result.returncode == 0, result.stdout.strip()
    except FileNotFoundError:
        logging.debug(f"Git not found when checking {file_path}")
        return False, ""
    except Exception as e:
        logging.debug(f"Error checking git for {file_path}: {e}")
        return False, ""


def is_git_tracked(file_path: Path) -> bool:
    is_tracked, _ = _git_command(file_path, ["git", "ls-files", "--error-unmatch", str(file_path)])
    logging.debug(f"File {file_path} is git tracked: {is_tracked}")
    return is_tracked


def has_git_changes(file_path: Path) -> bool:
    success, output = _git_command(file_path, ["git", "status", "--porcelain", str(file_path)])
    has_changes = bool(output)  # True if there's any output, False if empty
    logging.debug(f"File {file_path} has git changes: {has_changes}")
    return has_changes


def process_file(client: GeminiClient, file_path: Path, message: str) -> bool:
    if not file_path.is_file() or not os.access(file_path, os.R_OK):
        logging.error(f"Cannot read file: {file_path}")
        return False

    backup_path = file_path.with_suffix(f"{file_path.suffix}.{time.strftime("%Y%m%d%H%M%S")}.bak")
    if not is_git_tracked(file_path) or has_git_changes(file_path):
        try:
            shutil.copy2(file_path, backup_path)
            logging.info(f"Created backup: {backup_path}")
        except Exception as e:
            logging.error(f"Failed to create backup for {file_path}: {e}")
            return False

    try:
        content = file_path.read_text()
        prompt = textwrap.dedent(
            f"""
            You are tasked with modifying the content of a file based on specific instructions.

            Here is the current content of the file:
            ```
            {content}
            ```

            Instructions: {message}

            Your goal is to apply the instructions precisely and make only the necessary changes.
            Avoid making any unrelated modifications or stylistic changes that are not explicitly requested.
            Preserve the overall structure and formatting of the original file as much as possible.
            Focus on fulfilling the instructions efficiently and accurately.
        """
        ).strip()

        result = client.generate(prompt, "file")
        file_path.write_text(result)

        logging.info(f"Successfully processed: {file_path}")
        return True

    except Exception as e:
        logging.error(f"Failed to process file: {file_path} - {e}")
        return False


def ai_action(entry: Path, message: str) -> bool:
    client = GeminiClient(
        api_key=os.environ["GEMINI_API_KEY"],
        debug=logging.getLogger().level == logging.DEBUG
    )

    if entry.is_file():
        return process_file(client, entry, message)

    elif entry.is_dir():
        files = list(entry.rglob("*"))
        if len(files) > 10:
            logging.error(f"Directory contains more than 10 files ({len(files)} files found). Aborting.")
            return False

        return all(process_file(client, f, message) for f in files if f.is_file())

    logging.error(f"Path does not exist or is neither a file nor directory: {entry}")
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Process files with AI modifications",
        epilog=textwrap.dedent("""
            examples:
              %(prog)s file.py "Add type hints to all functions"
              %(prog)s src/ "Update docstrings to Google style" --debug
              %(prog)s config.json "Add a new 'timeout' field set to 30"
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("entry", help="Path to file or directory to process")
    parser.add_argument("message", help="Instructions for changes to make to the file(s)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format='%(message)s'
    )

    success = ai_action(Path(args.entry), args.message)
    exit(0 if success else 1)


if __name__ == "__main__":
    main()