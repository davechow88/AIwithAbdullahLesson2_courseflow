"""Check that a running CourseFlow server answers GET /api/health and GET /api/trainees.

Start the server first (python server.py), then in another window:
    python scripts/api_healthcheck.py                          checks the default URL
    python scripts/api_healthcheck.py http://localhost:9000    checks another URL
Prints "all good" and exits with 0, or prints each error and the server URL and exits with 1.
"""
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
import json
import sys

# the address server.py listens on; "localhost" works too, but on Windows it first tries IPv6 and waits ~2s per request
DEFAULT_URL = 'http://127.0.0.1:8765'
TIMEOUT_SECONDS = 5
PATHS = ['/api/health', '/api/trainees']

def check_endpoint(base_url, path):
    """Return None when GET path gives the expected JSON, otherwise a short reason."""
    try:
        with urlopen(base_url + path, timeout=TIMEOUT_SECONDS) as res:
            body = res.read()
    except HTTPError as err:  # the server answered, but with an error status such as 404
        with err:
            return f'HTTP {err.code} {err.reason}'
    except URLError as err:  # nothing answered, e.g. the server is not running
        return f'could not connect ({err.reason})'
    except (OSError, HTTPException) as err:  # e.g. no reply in time, or a reply that is not HTTP
        return f'connection error ({err})'
    try:
        data = json.loads(body)
    except ValueError:
        return 'response is not valid JSON'
    if path == '/api/health' and not (isinstance(data, dict) and data.get('status') == 'ok'):
        return "response status is not 'ok'"
    if path == '/api/trainees' and not (isinstance(data, dict) and isinstance(data.get('trainees'), list)):
        return "response has no 'trainees' list"
    return None

def main(args):
    base_url = (args[0] if args else DEFAULT_URL).rstrip('/')
    failed = False
    for path in PATHS:
        problem = check_endpoint(base_url, path)
        if problem:
            print(f'GET {path} failed: {problem}')
            failed = True
    if failed:
        print(f'Server URL: {base_url}')
        return 1
    print('all good')
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
