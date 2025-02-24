# gemini

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

examples:
  gemini.py "Write a Python script that prints hello world" --response-type file
  gemini.py "Create directories data/{in,out,temp}" -rt cmd
  gemini.py "Create a Python project structure" -rt files --debug
  gemini.py --debug "Generate test data"
```
