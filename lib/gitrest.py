#!python

from routes import Mapper, request_config
from cStringIO import StringIO
from simplejson import dumps, loads

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
            self.run_controller(match)

        self._start_response(self._status, self._response_headers)
        return self._output.getvalue()


class GitRest(Rest):
    def init_controllers(self):
        self.routes_config = {
            '/': {
                'controller': 'root',
                'class': RootController,
            },
#             '/repo': {
#                 'controller': 'repo',
#                 'class': RepoController,
#             },
             '/repos': {
                 'controller': 'repos',
                 'class': ReposController,
             },
#             '/repo/:repo/commits': {
#                 'controller': 'repo_commits',
#                 'class': RepoCommitsController,
#             },
        }

        routes = self.routes_config.keys()
        routes.sort(None, None, True) # sort in reverse
        self.controller_map = {}
        for route in routes:
            route_config = self.routes_config[route]
            controller = route_config['controller']
            self.controller_map[controller] = route_config['class']
            del route_config['class']
            self._mapper.connect(route, **route_config)

        self.config = request_config()
        self.config.mapper = self._mapper
        self.config.environ = self._environ

    def run_controller(self, match):
        controller = self.config.mapper_dict['controller']
        ControllerClass = self.controller_map[controller]
        controller = ControllerClass(self)
        controller.GET()

    def set_repos(self, repos):
        self._repos = repos

    def write(self, s):
        self._output.write(s)


class Controller(object):
    def __init__(self, rest):
        self.rest = rest

    def set_match(self, match):
        self.match = match

    def GET(self):
         accept = self.rest._environ.get('HTTP_ACCEPT', 'text/html').split(',')
         if 'text/html' in accept:
             self.GET_html()
         elif 'application/json' in accept:
             self.GET_json()
         elif 'text/plain' in accept:
             self.GET_plain()
         else:
             self.GET_html()

    def GET_json(self):
        self.rest.write(dumps(self.get_resource()))

    def GET_html(self):
        self.rest.write("html %s" % (self.get_resource()))

    def GET_plain(self):
        self.rest.write("plain %s" % (self.get_resource()))


class ReposController(Controller):
    def GET(self):
        return 'repos controller'

    def GET_resource(self):
        return self.repos.keys().sort()


class RootController(Controller):
    def get_resource(self):
        repos = self.rest._repos.keys()
        repos.sort()
        return repos
