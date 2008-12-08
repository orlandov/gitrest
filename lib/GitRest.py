#!python

from routes import Mapper, request_config

def Rest(object):
    def __init__(self, environ, start_response):
        self._environ = environ
        self._start_response = start_response
        self._response_headers = [('Content-type','text/plain')]
        self._mapper = Mapper()
        self.init_controllers()

    def init_controllers():
        pass

    def serve(self):
        match = self._mapper.match(self._environ['REQUEST_URI'])

        if not match:
            return "couldn't find it"
            
def GitRest(Rest):
    def init_controllers(self):
        self._mapper = Mapper()
        self._mapper.connect('/repos', controller='repo')
        self._mapper.connect('', controller='root')

        config = request_config()
        config.environ = self._environ

        self._controllers = dict(
            root = self.root,
            repos = self.repos,
            commits = self.commits
        )

    def root(self):
        return "root controller"

    def repos(self):
        return "repo 1\nrepo 2\n"

    def commits(self):
        return "1 2 3 commits"

