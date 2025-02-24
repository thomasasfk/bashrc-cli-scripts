#!/usr/bin/env python3.13

from pathlib import Path
import argparse
import logging
import os
import time
from contextlib import contextmanager
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from gemini import GeminiClient

console = Console()


class LogMonitor:
    def __init__(self, log_path: Path, interval: int, persona: str, debug: bool = False):
        self.log_path = log_path
        self.interval = interval
        self.persona = persona
        self.client = GeminiClient(api_key=os.environ["GEMINI_API_KEY"], debug=debug)
        self.new_logs = []
        self.last_summary_time = 0

    def generate_summary(self) -> str | None:
        if not self.new_logs:
            return None

        prompt = f"""
        You are acting as {self.persona}. Analyze these new log entries and provide a summary:

        {"\n".join(self.new_logs)}

        Respond conversationally in character as {self.persona}, but keep it brief (1-2 sentences).
        Focus only on new activity, errors, or patterns seen in these specific log lines.
        """

        try:
            return self.client.generate(prompt)
        except Exception as e:
            logging.error(f"Failed to generate summary: {e}")
            return None

    def monitor(self):
        with self.log_path.open('r', encoding='utf-8', errors='replace') as file:
            file.seek(0, 2)  # Seek to end

            with Live(Panel("Initializing...", title="Log Monitor"), refresh_per_second=10) as live:
                while True:
                    line = file.readline()
                    if line:
                        self.new_logs.append(line.strip())

                    current_time = time.time()
                    if (current_time - self.last_summary_time >= self.interval) and self.new_logs:
                        summary = self.generate_summary()
                        if summary:
                            timestamp = time.strftime('%H:%M:%S')
                            content = Text.assemble(
                                (f"[{timestamp}] ", "cyan"),
                                summary
                            )
                            live.update(Panel(content, title="Log Monitor"))

                        self.new_logs = []
                        self.last_summary_time = current_time

                    time.sleep(0.1)


@contextmanager
def handle_shutdown():
    try:
        yield
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down...[/]")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("log_file", type=Path, help="Path to the log file to monitor")
    parser.add_argument("--interval", type=int, default=5, help="Interval in seconds between log summaries")
    parser.add_argument("--persona", type=str, default="a concise systems analyst", help="Persona to use for the log summary")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    if not args.log_file.exists():
        console.print(f"[red]Error:[/] Log file does not exist: {args.log_file}")
        return 1

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format='%(message)s'
    )

    monitor = LogMonitor(args.log_file, args.interval, args.persona, args.debug)

    with handle_shutdown():
        monitor.monitor()


if __name__ == "__main__":
    main()