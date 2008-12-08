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
        match = self.config.mapper_dict

        if not match:
            self._status = '404 Not found'
            self._output.write("Invalid Command")
        else:
            getattr(self, self.config.mapper_dict['controller'])(match)

        self._start_response(self._status, self._response_headers)
        return self._output.getvalue()
            
class GitRest(Rest):
    def init_controllers(self):
        self._mapper.resource(
            'branch', 'branches',
            parent_resource=dict(
                member_name='repo',
                collection_name='repos'
            )
        )
        self._mapper.resource('repo', 'repos')

        self._mapper.connect('', controller='root')

        self.config = request_config()
        self.config.mapper = self._mapper
        self.config.environ = self._environ

    def set_repos(self, repos):
        self._repos = repos

    def root(self, match):
        self._output.write("root controller\n")

    def repos(self, match):
        for repo in self._repos:
            self._output.write("%s\n" % (repo,))

    def branches(self, match):
        self._output.write("a branch\n%s" % (match,))

    def commits(self, match):
        self._output.write("1 2 3 commits\n")

