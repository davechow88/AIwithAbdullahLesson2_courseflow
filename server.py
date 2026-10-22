from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path
import json
import os
from datetime import date
from store import initialize, read_trainees, read_courses, add_trainee
from rules import needs_renewal, validate_trainee, matches_search

ROOT = Path(__file__).resolve().parent
MAX_BODY_BYTES = 10_000

def transform(rows):
    return [{**row, "renewal_soon": needs_renewal(row["expires_on"])} for row in rows]

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        path = url.path
        if path == '/':
            return self.respond((ROOT / 'web' / 'index.html').read_bytes(), 'text/html; charset=utf-8')
        if path == '/api/trainees':
            query = parse_qs(url.query)
            course = query.get('course', [''])[0]
            q = query.get('q', [''])[0]  # searches every column the table shows
            rows = read_trainees(course)
            rows = transform(rows)
            # filtered after transform() so the status words come from the same renewal rule as the badge
            rows = [row for row in rows if matches_search(row, q)]
            return self.respond(json.dumps({'as_of': date.today().isoformat(), 'trainees':rows}).encode(), 'application/json')
        if path == '/api/courses':
            return self.send_json({'courses': read_courses()})
        if path == '/api/health':
            return self.respond(b'{"status":"ok","environment":"local_demo"}', 'application/json')
        return self.respond(b'{"error":"not_found"}', 'application/json',404)

    def do_POST(self):
        if urlparse(self.path).path != '/api/trainees':
            return self.send_json({'error': 'not_found'}, 404)
        try:
            length = int(self.headers.get('Content-Length', 0))
        except ValueError:
            length = -1
        if length < 0:
            return self.send_json({'error': 'invalid_json'}, 400)
        if length > MAX_BODY_BYTES:
            return self.send_json({'error': 'too_large'}, 413)
        try:
            data = json.loads(self.rfile.read(length))
        except (ValueError, RecursionError):  # bad JSON or bad text encoding, or absurdly deep nesting
            return self.send_json({'error': 'invalid_json'}, 400)
        if not isinstance(data, dict):
            return self.send_json({'error': 'invalid_json'}, 400)
        clean, errors = validate_trainee(data, courses=read_courses())
        if errors:
            return self.send_json({'error': 'invalid_fields', 'fields': errors}, 400)
        row = add_trainee(clean['name'], clean['course'], clean['expires_on'])
        return self.send_json(transform([row])[0], 201)

    def send_json(self, obj, status=200):
        return self.respond(json.dumps(obj).encode(), 'application/json', status)

    def respond(self, data, media_type, status=200):
        self.send_response(status)
        self.send_header('Content-Type', media_type)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        print('%s  %s' % (self.address_string(), fmt%args))

if __name__ == '__main__':
    initialize()
    port = int(os.environ.get('PORT','8765'))
    print(f'CourseFlow LOCAL demo: http://localhost:{port}')
    print(f'API response: http://localhost:{port}/api/trainees')
    print('Press Ctrl+C to stop. Fake data only; not for deployment.')
    ThreadingHTTPServer(('127.0.0.1',port), Handler).serve_forever()
