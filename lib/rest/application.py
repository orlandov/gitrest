#!python

from routes import Mapper, request_config, url_for
from cStringIO import StringIO

class Application(object):
    def __init__(self, environ, start_response):
        self._environ = environ
        self._start_response = start_response
        self._status = '200 OK'
        self.response_headers = { 'Content-type': 'text/html' }
        self._headers = []
        self._mapper = Mapper()
        self._output = StringIO()
        self.init_controllers()

    def content_type(self, type=None):
        if type: self.response_headers['Content-type'] = type
        return self.response_headers['Content-type']

    def serve(self):
        self.match = self.config.mapper_dict

        if not self.match:
            self.status('404 Not found')
            self.write("Invalid Command")
            self._make_response_headers()
            self._start_response(self._status, self._headers)
            return self.body()

        self.run_controller()

        self._make_response_headers()
        self._start_response(self._status, self._headers)
        return self.body()

    # return the full contents of the body
    def body(self):
        return self._output.getvalue()

    # write to the body, appends
    def write(self, s):
        self._output.write(s)

    def status(self, s):
        self._status = s

    def _make_response_headers(self):
        self._headers = []
        for header in self.response_headers.keys():
            self._headers.append((header, self.response_headers[header]))
