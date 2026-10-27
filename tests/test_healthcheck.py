import io
import socket
import threading
import unittest
from contextlib import redirect_stdout
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from unittest import mock
from scripts import api_healthcheck
from helpers import TempServer

def run_healthcheck(base_url):
    """Run the script's main() and return (exit code, printed text)."""
    out = io.StringIO()
    with redirect_stdout(out):
        code = api_healthcheck.main([base_url])
    return code, out.getvalue()

class RealServerTests(TempServer):
    """The real CourseFlow API on a test server, using the temporary database."""
    def base_url(self):
        return f'http://127.0.0.1:{self.httpd.server_address[1]}'

    def test_running_server_is_all_good(self):
        self.assertEqual(run_healthcheck(self.base_url()), (0, 'all good\n'))

    def test_wrong_path_reports_404_for_each_endpoint(self):
        code, out = run_healthcheck(self.base_url() + '/wrong')
        self.assertEqual(code, 1)
        self.assertIn('GET /api/health failed: HTTP 404', out)
        self.assertIn('GET /api/trainees failed: HTTP 404', out)
        self.assertIn(f'Server URL: {self.base_url()}/wrong', out)

class NoServerTests(unittest.TestCase):
    def test_no_server_reports_both_endpoints_and_the_url(self):
        with socket.socket() as sock:  # borrow a free port, then close it so nothing listens there
            sock.bind(('127.0.0.1', 0))
            url = f'http://127.0.0.1:{sock.getsockname()[1]}'
        code, out = run_healthcheck(url)
        self.assertEqual(code, 1)
        self.assertIn('GET /api/health failed: could not connect', out)
        self.assertIn('GET /api/trainees failed: could not connect', out)
        self.assertIn(f'Server URL: {url}', out)

class FakeApiHandler(BaseHTTPRequestHandler):
    """Answers 200 with whatever body the test chose, to imitate a broken API."""
    def do_GET(self):
        body = self.server.replies[self.path]
        self.send_response(200)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass  # keep test output readable

class BrokenApiTests(unittest.TestCase):
    def start_fake_api(self, health, trainees):
        httpd = ThreadingHTTPServer(('127.0.0.1', 0), FakeApiHandler)
        httpd.replies = {'/api/health': health, '/api/trainees': trainees}
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        self.addCleanup(httpd.server_close)
        self.addCleanup(httpd.shutdown)
        return f'http://127.0.0.1:{httpd.server_address[1]}'

    def test_reply_that_is_not_json_is_reported(self):
        code, out = run_healthcheck(self.start_fake_api(b'hello', b'<html></html>'))
        self.assertEqual(code, 1)
        self.assertIn('GET /api/health failed: response is not valid JSON', out)
        self.assertIn('GET /api/trainees failed: response is not valid JSON', out)

    def test_health_status_not_ok_is_reported_alone(self):
        code, out = run_healthcheck(self.start_fake_api(b'{"status": "down"}', b'{"trainees": []}'))
        self.assertEqual(code, 1)
        self.assertIn("GET /api/health failed: response status is not 'ok'", out)
        self.assertNotIn('/api/trainees', out)

    def test_trainees_without_list_is_reported_alone(self):
        code, out = run_healthcheck(self.start_fake_api(b'{"status": "ok"}', b'{"x": 1}'))
        self.assertEqual(code, 1)
        self.assertIn("GET /api/trainees failed: response has no 'trainees' list", out)
        self.assertNotIn('/api/health', out)

class MockedResponseTests(unittest.TestCase):
    """No server at all: urlopen is replaced by a fake that returns a chosen reply."""
    def test_health_reply_with_status_down_is_reported(self):
        fake = mock.MagicMock()
        fake.__enter__.return_value.read.return_value = b'{"status": "down"}'
        with mock.patch('scripts.api_healthcheck.urlopen', return_value=fake) as urlopen:
            problem = api_healthcheck.check_endpoint('http://x', '/api/health')
        self.assertEqual(problem, "response status is not 'ok'")
        urlopen.assert_called_once_with('http://x/api/health', timeout=api_healthcheck.TIMEOUT_SECONDS)

if __name__ == '__main__':
    unittest.main()
