#!python

import random
import simplejson
import threading
from httplib import HTTPConnection
from wsgiref.simple_server import make_server

import grwsgi

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

    def assert_equal(self, got, exp):
        self.assertEqual(got, exp, 'got %s, exp %s' % (repr(got), repr(exp)))

    def GET(self, path, headers={'Accept': 'text/html'}):
        c = HTTPConnection(self.server, self.port)
        url = self.make_rest_url(path)
        c.request('GET', url, None, headers)
        self._response = c.getresponse()
        self.response_body = self._response.read()

    def GET_json(self, path):
        headers = { 'Accept': 'application/json' }
        self.GET(path, headers)

    def assert_header(self, header, exp_value):
        self.assert_equal(self._response.getheader(header), exp_value)

    def assert_code(self, exp_code):
        self.assert_equal(self._response.status, exp_code)

    def assert_json(self, exp_obj):
        s = self.response_body
        obj = simplejson.loads(s)
        self.assert_equal(obj, exp_obj)

    def assert_body_like(self, exp_body):
        self.assertTrue(exp_body in self.response_body, "%s -- %s" % (self.response_body, exp_body))
