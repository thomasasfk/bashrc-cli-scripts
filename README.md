# Description

A collection of utility scripts and bash files that are executed by bashrc to make various tools and commands available across systems. The project serves as a central location for personal command-line tools and utilities.

[//]: # (START_HELP)

## Available Commands

### gemini

```
usage: gemini.py [-h] [-rt {file,files,cmd}] [--debug] prompt [prompt ...]

Gemini API Client

positional arguments:
  prompt                The prompt to send to Gemini

options:
  -h, --help            show this help message and exit
  -rt, --response-type {file,files,cmd}
                        Response format type
  --debug               Enable debug logging
```

### ai

```
usage: ai.py [-h] [--debug] path message

Process files with AI modifications

positional arguments:
  path        Path to file or directory to process
  message     Instructions for changes to make to the file(s)

options:
  -h, --help  show this help message and exit
  --debug     Enable debug logging
```

### tailpal

```
usage: tailpal.py [-h] [--interval INTERVAL] [--persona PERSONA] [--debug] log_file

positional arguments:
  log_file             Path to the log file to monitor

options:
  -h, --help           show this help message and exit
  --interval INTERVAL  Interval in seconds between log summaries
  --persona PERSONA    Persona to use for the log summary
  --debug              Enable debug logging
```

[//]: # (END_HELP)

## Setup

These scripts are automatically loaded and made available through your bashrc configuration. If you're setting up on a new system, ensure the repository is cloned and properly referenced in your `.bashrc` file.

## Requirements

- For AI-related commands: `GEMINI_API_KEY` environment variable must be set