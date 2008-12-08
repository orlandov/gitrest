#!python

from routes import Mapper, request_config
from cStringIO import StringIO

class Rest(object):
    def __init__(self, environ, start_response):
        self._environ = environ
        self._start_response = start_response
        self._status = '200 OK'
        self._response_headers = [('Content-type','text/plain')]
        self._mapper = Mapper()
        self._output = StringIO()
        self.init_controllers()

    def init_controllers():
        pass

    def serve(self):
        if not self.config.mapper_dict:
            self._status = '404 Not found'
            self._output.write("Invalid Command")
        else:
            getattr(self, self.config.mapper_dict['controller'])()

        self._start_response(self._status, self._response_headers)
        return self._output.getvalue()
            
class GitRest(Rest):
    def __init__(self, *args, **kwargs):
        Rest.__init__(self, *args, **kwargs)

    def init_controllers(self):
        self._mapper.connect('/repos', controller='repos')
        self._mapper.connect('', controller='root')

        self.config = request_config()
        self.config.mapper = self._mapper
        self.config.environ = self._environ

    def root(self):
        self._output.write("root controller\n")

    def repos(self):
        self._output.write("repo 1\nrepo 2\n")

    def commits(self):
        self._output.write("1 2 3 commits\n")

