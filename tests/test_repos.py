#!python

import unittest
from httplib import HTTPConnection
import random
import threading
import simplejson

import grwsgi
from wsgiref.simple_server import make_server

class RestTest(object):
    def start_server(self, server='localhost', base_path=''):
        self.server = server
        self.base_path = base_path
        self.port = random.randint(1024, 65000)
        self.httpd = make_server(self.server, self.port, grwsgi.application)
        self.thread = threading.Thread(target=self.httpd.serve_forever)
        self.thread.start()

    def make_rest_url(self, path):
        return "%s%s" % (self.base_path, path)

    def GET(self, path, headers={}):
        c = HTTPConnection(self.server, self.port)
        url = self.make_rest_url(path)
        c.request('GET', url, None, headers)
        self._response = c.getresponse()
        self.response_body = self._response.read()

    def GET_json(self, path):
        headers = { 'Accept': 'application/json' }
        self.GET(path, headers)

    def assert_code(self, exp_code):
        self.assertEqual(self._response.status, exp_code)

    def assert_json(self, exp_obj):
        s = self.response_body
        obj = simplejson.loads(s)
        self.assertEqual(obj, exp_obj)

    def assert_body_like(self, exp_body):
        self.assertTrue(exp_body in self.response_body, "%s -- %s" % (self.response_body, exp_body))


class TestRoot(unittest.TestCase, RestTest):
    def setUp(self):
        self.start_server()

    def test_repos(self):
        self.GET_json('/')
        self.assert_code(200)
        self.assert_json([u'a', u'b'])


class TestRepos(unittest.TestCase, RestTest):
    def setUp(self):
        self.start_server()

    def test_repos(self):
        self.GET_json('/repos')
        self.assert_code(200)
        self.assert_json([u'a', u'b'])

    def test_html(self):
        self.GET('/repos', headers={ 'Accept': 'text/html' })
        self.assert_body_like(u'a<br />b')

    def test_invalid_path(self):
        self.GET('/invalid')
        self.assert_code(404)
