#!/usr/bin/env python3.13

from dataclasses import dataclass
from enum import StrEnum, auto
import argparse
import logging
import os
import textwrap
from typing import Any

import requests


class ResponseType(StrEnum):
    FILE = auto()
    FILES = auto()
    CMD = auto()


@dataclass
class GeminiClient:
    api_key: str
    debug: bool = False
    endpoint: str = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

    def __post_init__(self):
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        logging.basicConfig(
            level=logging.DEBUG if self.debug else logging.INFO,
            format='[%(levelname)s] %(message)s'
        )

    def _prepare_prompt(self, prompt: str, response_type: ResponseType | None = None) -> str:
        match response_type:
            case ResponseType.FILE:
                instructions = textwrap.dedent(
                    """
                    IMPORTANT: Respond with ONLY raw file contents.
                    No markdown, code blocks, or language indicators.
                    No explanatory text, headers, or footers.
                    Start and end directly with file contents.
                """
                ).strip()
                return f"{prompt}\n\n{instructions}"

            case ResponseType.FILES:
                instructions = textwrap.dedent(
                    """
                    IMPORTANT: Respond with a bash script creating files:
                    1. Start with #!/bin/bash
                    2. For each file, use:
                    mkdir -p "$(dirname "path/to/filename")" 2>/dev/null; cat << "EOF" > path/to/filename
                    [file contents]
                    EOF
                    No markdown, code blocks, or additional text.
                """
                ).strip()
                return f"{prompt}\n\n{instructions}"

            case ResponseType.CMD:
                instructions = textwrap.dedent(
                    """
                    IMPORTANT: Respond with ONLY a single line of executable bash code.
                    No explanation, no markdown, no comments.
                    The command should achieve the described task efficiently.
                    Must be safe to pipe directly to bash.
                """
                ).strip()
                return f"{prompt}\n\n{instructions}"

            case _:
                return prompt

    def _parse_response(self, response: dict[str, Any]) -> str:
        content = response["candidates"][0]["content"]["parts"][0]["text"]

        if not content:
            raise ValueError("Empty response from API")

        lines = content.split('\n')
        if lines[0].startswith('```') and lines[-1].startswith('```'):
            content = '\n'.join(lines[1:-1])

        return content.strip()

    def generate(self, prompt: str, response_type: ResponseType | None = None) -> str:
        prepared_prompt = self._prepare_prompt(prompt, response_type)
        payload = {"contents": [{"parts": [{"text": prepared_prompt}]}]}

        logging.debug("Calling Gemini API")
        response = requests.post(
            self.endpoint,
            headers={"Content-Type": "application/json"},
            params={"key": self.api_key},
            json=payload
        )
        response.raise_for_status()

        return self._parse_response(response.json())


def main():
    parser = argparse.ArgumentParser(description="Gemini API Client")
    parser.add_argument("prompt", nargs="+", help="The prompt to send to Gemini")
    parser.add_argument(
        "-rt", "--response-type",
        choices=[t.name.lower() for t in ResponseType],
        help="Response format type"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    try:
        client = GeminiClient(
            api_key=os.environ["GEMINI_API_KEY"],
            debug=args.debug
        )

        prompt = " ".join(args.prompt)
        response_type = ResponseType[args.response_type.upper()] if args.response_type else None

        result = client.generate(prompt, response_type)
        print(result)
        exit(0)

    except KeyError:
        logging.error("GEMINI_API_KEY environment variable not set")
        exit(1)
    except requests.RequestException as e:
        logging.error(f"API call failed: {e}")
        exit(1)
    except Exception as e:
        logging.error(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()