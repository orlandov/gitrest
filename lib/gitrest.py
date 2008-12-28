#!python

from routes import Mapper, request_config
from cStringIO import StringIO
from simplejson import dumps, loads

import git

class Rest(object):
    def __init__(self, environ, start_response):
        self._environ = environ
        self._start_response = start_response
        self._status = '200 OK'
        self.response_headers = { 'Content-type': 'text/html' }
        self._headers = []
        self._mapper = Mapper()
        self._output = StringIO()
        self.init_controllers()

    def init_controllers():
        pass

    def content_type(self, type):
        self.response_headers['Content-type'] = type

    def serve(self):
        self.match = self.config.mapper_dict

        if not self.match:
            self.status('404 Not found')
            self.write("Invalid Command")
        else:
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


class GitRest(Rest):
    def init_controllers(self):
        self.routes_config = {
            '/': {
                'controller': 'root',
                'class': RootController,
            },
            '/repo/:repo': {
                'controller': 'repo',
                'class': RepoController,
            },
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

    def run_controller(self):
        controller = self.config.mapper_dict['controller']
        ControllerClass = self.controller_map[controller]
        controller = ControllerClass(self)
        controller.GET()

    def set_repos(self, repos):
        self._repos = repos


class Controller(object):
    def __init__(self, rest):
        self.rest = rest

    def GET(self):
         accept = self.rest._environ.get('HTTP_ACCEPT', 'text/html').split(',')
         if 'text/html' in accept:
             self.rest.content_type('text/html')
             self.GET_html()
         elif 'application/json' in accept:
             self.rest.content_type('application/json')
             self.GET_json()
         elif 'text/plain' in accept:
             self.rest.content_type('text/plain')
             self.GET_plain()
         else:
             self.rest.content_type('text/html')
             self.GET_html()

    def GET_json(self):
        try:
            self.rest.write(dumps(self.get_resource()))
        except:
            pass

    def GET_html(self):
        try:
            self.rest.write("<br />".join(self.get_resource()))
        except:
            pass

    def GET_plain(self):
        try:
            self.rest.write("plain %s" % (self.get_resource()))
        except:
            pass


class ReposController(Controller):
    def get_resource(self):
        repos = self.rest._repos.keys()
        repos.sort()
        return repos


class RootController(Controller):
    def get_resource(self):
        repos = self.rest._repos.keys()
        repos.sort()
        return repos


class RepoController(Controller):
    def get_resource(self):
        repo_name = self.rest.match['repo']
        repo = git.Repo('repos/' + self.rest.match['repo'] + '.git')

        return {
            'repo': repo_name,
            'description': repo.description,
            'branches': [ branch.name for branch in repo.branches ],
            'tree': [ item[0] for item in repo.tree().items() ]
        }

    @staticmethod
    def as_html(resource):
        repo = resource['repo']
        desc = resource['description']
        branches = resource['branches']
        return "<h1>%s</h1>Description: %s<br />Branches: %s" % (repo, desc, ", ".join(branches))

    def GET_html(self):
        try:
            self.rest.write(RepoController.as_html(self.get_resource()))
        except git.NoSuchPathError:
            self.rest.status('404 Repo not found')
            self.rest.write("No such repo")

    def GET_plain(self):
        self.rest.write('weak')
