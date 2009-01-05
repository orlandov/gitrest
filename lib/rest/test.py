#!python

import random
import simplejson
import threading
from httplib import HTTPConnection
from wsgiref.simple_server import make_server

import gitrest.wsgi

class Test(object):
    def start_server(self, server='localhost', base_path=''):
        self.server = server
        self.base_path = base_path
        self.port = random.randint(1024, 65000)
        self.httpd = make_server(self.server, self.port, gitrest.wsgi.application)
        self.thread = threading.Thread(target=self.httpd.serve_forever)
        self.thread.start()

    def make_rest_url(self, path):
        return "%s%s" % (self.base_path, path)

    def assert_equal(self, got, exp, msg=""):
        self.assertEqual(got, exp, 'got %s, exp %s - %s' % (repr(got), repr(exp), msg))

    def GET(self, path, headers={'Accept': 'text/html'}):
        c = HTTPConnection(self.server, self.port)
        url = self.make_rest_url(path)
        c.request('GET', url, None, headers)
        self._response = c.getresponse()
        self.response_body = self._response.read()

    def GET_json(self, path):
        headers = { 'Accept': 'application/json' }
        self.GET(path, headers)
        try:
            self.json_object = simplejson.loads(self.response_body)
        except:
            print "Invalid JSON ", self.response_body
            raise

    def assert_header(self, header, exp_value):
        self.assert_equal(self._response.getheader(header), exp_value)

    def assert_content_type(self, ct):
        self.assert_header('Content-type', ct)

    def assert_code(self, exp_code):
        self.assert_equal(self._response.status, exp_code, "response body was '%s'" % (self.response_body))

    def assert_json(self, exp_obj):
        s = self.response_body
        try:
            obj = simplejson.loads(s)
        except:
            print "Invalid JSON ", s
            raise

        self.assert_equal(obj, exp_obj)

    def assert_body_like(self, exp_body):
        self.assertTrue(exp_body in self.response_body, "%s -- %s" % (self.response_body, exp_body))
