#!/usr/bin/env python3.13

from pathlib import Path
import argparse
import logging
import os
import textwrap
import shutil
import subprocess

from gemini import GeminiClient, ResponseType


def is_git_tracked(file_path: Path) -> bool:
    try:
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", str(file_path)],
            capture_output=True,
            text=True,
            cwd=file_path.parent,
            check=False
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False  # git not installed
    except Exception:
        return False  # error while checking git status


def has_git_changes(file_path: Path) -> bool:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", str(file_path)],
            capture_output=True,
            text=True,
            cwd=file_path.parent,
            check=False
        )
        return bool(result.stdout.strip())
    except FileNotFoundError:
        return False  # git not installed
    except Exception:
        return False  # error while checking git status


def process_file(client: GeminiClient, file_path: Path, message: str) -> bool:
    if not file_path.is_file() or not os.access(file_path, os.R_OK):
        logging.error(f"Cannot read file: {file_path}")
        return False

    backup_path = file_path.with_suffix(file_path.suffix + ".bak")

    if not is_git_tracked(file_path) or has_git_changes(file_path):
        if backup_path.exists():
            logging.warning(f"Backup file already exists, skipping backup: {backup_path}")
        else:
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

        result = client.generate(prompt, ResponseType.RAW_FILE)
        file_path.write_text(result)

        logging.info(f"Successfully processed: {file_path}")
        return True

    except Exception as e:
        logging.error(f"Failed to process file: {file_path} - {e}")
        return False


def ai_action(path: str | Path, message: str) -> bool:
    path = Path(path)

    try:
        client = GeminiClient(
            api_key=os.environ["GEMINI_API_KEY"],
            debug=logging.getLogger().level == logging.DEBUG
        )

        if path.is_file():
            return process_file(client, path, message)

        elif path.is_dir():
            files = list(path.rglob("*"))
            if len(files) > 10:
                logging.error(f"Directory contains more than 10 files ({len(files)} files found). Aborting.")
                return False

            return all(process_file(client, f, message) for f in files if f.is_file())

        else:
            logging.error(f"Path does not exist or is neither a file nor directory: {path}")
            return False

    except Exception as e:
        logging.error(f"Error during processing: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Process files with AI modifications")
    parser.add_argument("path", help="Path to file or directory to process")
    parser.add_argument("message", help="Instructions for changes to make to the file(s)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format='%(message)s'
    )

    success = ai_action(args.path, args.message)
    exit(0 if success else 1)


if __name__ == "__main__":
    main()