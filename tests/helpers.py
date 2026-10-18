"""Shared test setup (not a test file itself): a temporary database and a local test server."""
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import server
import store

class TempDatabase(unittest.TestCase):
    """Each test gets a fresh temporary database with the 5 fake trainees."""
    def setUp(self):
        folder = TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        patcher = patch.object(store, 'DB', Path(folder.name) / 'test.sqlite3')
        patcher.start()
        self.addCleanup(patcher.stop)
        store.initialize()

class QuietHandler(server.Handler):
    def log_message(self, fmt, *args):
        pass  # keep test output readable

class TempServer(TempDatabase):
    """Also starts a real HTTP server on a free port that uses the temporary database."""
    def setUp(self):
        super().setUp()
        self.httpd = ThreadingHTTPServer(('127.0.0.1', 0), QuietHandler)
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        self.addCleanup(self.httpd.server_close)
        self.addCleanup(self.httpd.shutdown)

    def request(self, path, method='GET', body=None):
        """Send a request and return (status, parsed JSON), including 4xx replies."""
        port = self.httpd.server_address[1]
        req = Request(f'http://127.0.0.1:{port}{path}', data=body, method=method, headers={'Content-Type': 'application/json'})
        try:
            with urlopen(req) as res:
                return res.status, json.loads(res.read())
        except HTTPError as err:
            with err:
                return err.code, json.loads(err.read())
