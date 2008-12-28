#!python

import unittest
from httplib import HTTPConnection
import random
import threading

import grwsgi
from wsgiref.simple_server import make_server

class TestRepos(unittest.TestCase):
    def setUp(self):
        self.server = 'localhost'
        self.base_path = ''
        self.start_server()

    def test_repo(self):
        self.http_get('/repos')
        self.assert_code(200)

    def test_invalid_path(self):
        self.http_get('/invalid')
        self.assert_code(404)

    def http_get(self, path):
        c = HTTPConnection(self.server, self.port)
        url = self.make_rest_url(path)
        print url
        c.request('GET', url)
        self._response = c.getresponse()
        print self._response.read()

    def assert_code(self, exp_code):
        self.assertEqual(self._response.status, exp_code)
        
    def make_rest_url(self, path):
        return "%s%s" % (
            self.base_path,
            path
        )

    def start_server(self):
        self.port = random.randint(1024,65000)
        self.httpd = make_server(self.server, self.port, grwsgi.application)
        self.thread = threading.Thread(target=self.httpd.serve_forever)
        self.thread.start()
