from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from pathlib import Path
import json
import os
from datetime import date
from store import initialize, read_trainees
from rules import needs_renewal

ROOT = Path(__file__).resolve().parent

def transform(rows):
    return [{**row, "renewal_soon": needs_renewal(row["expires_on"])} for row in rows]

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/':
            return self.respond((ROOT / 'web' / 'index.html').read_bytes(), 'text/html; charset=utf-8')
        if path == '/api/trainees':
            rows = read_trainees()
            rows = transform(rows)
            return self.respond(json.dumps({'as_of': date.today().isoformat(), 'trainees':rows}).encode(), 'application/json')
        if path == '/api/health':
            return self.respond(b'{"status":"ok","environment":"local_demo"}', 'application/json')
        return self.respond(b'{"error":"not_found"}', 'application/json',404)

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
