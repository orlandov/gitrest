#!python

import unittest
from httplib import HTTPConnection

class TestRepos(unittest.TestCase):
    def setUp(self):
        self.server = 'localhost'
        self.base_path = '/gr'

    def test_repo(self):
        self.http_get('/repos')
        self.assert_code(200)

    def test_invalid_path(self):
        self.http_get('/invalid')
        self.assert_code(404)

    def http_get(self, path):
        c = HTTPConnection(self.server)
        c.request('GET', self.make_rest_url(path))
        self._response = c.getresponse()
        print self._response.read()

    def assert_code(self, exp_code):
        self.assertEqual(self._response.status, exp_code)
        
    def make_rest_url(self, path):
        return "%s%s" % (self.base_path, path)
