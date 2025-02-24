# tailpal

```
usage: tailpal.py [-h] [-i INTERVAL] [-p PERSONA] [--debug] log_file

AI-powered log monitoring with personality

positional arguments:
  log_file              Path to the log file to monitor

options:
  -h, --help            show this help message and exit
  -i, --interval INTERVAL
                        Interval in seconds between log summaries
  -p, --persona PERSONA
                        Persona to use for the log summary
  --debug               Enable debug logging

examples:
  tailpal.py /var/log/syslog
  tailpal.py /var/log/auth.log -i 10 --persona "paranoid cybersecurity pirate"
  tailpal.py /var/log/nginx/access.log -i 30 -p "caffeine-powered DevOps wizard" --debug
  tailpal.py /var/log/apache2/error.log -i 15 -p "grumpy BOFH from 1999"
```
