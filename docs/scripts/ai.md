# ai

```
usage: ai.py [-h] [--debug] entry message

Process files with AI modifications

positional arguments:
  entry       Path to file or directory to process
  message     Instructions for changes to make to the file(s)

options:
  -h, --help  show this help message and exit
  --debug     Enable debug logging

examples:
  ai.py file.py "Add type hints to all functions"
  ai.py src/ "Update docstrings to Google style" --debug
  ai.py config.json "Add a new 'timeout' field set to 30"
```
