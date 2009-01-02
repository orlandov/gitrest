#!python

import sys
import traceback
from routes import Mapper, request_config, url_for
from cStringIO import StringIO
from simplejson import dumps, loads
from cgi import parse_qs

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


class GitRest(Rest):
    def init_controllers(self):
        self.controller_map = {
            'commits': CommitsController,
            'repos': ReposController,
            'branchs': BranchesController,
            'root': RootController,
        }

        self._mapper.resource('repo', 'repos')
        self._mapper.resource('branch', 'branches',
            path_prefix='/repos/:repo_id', name_prefix='branch_')

        # both branches and repos have commits
        self._mapper.resource('commit', 'commits',
            path_prefix='/repos/:repo_id', name_prefix='commit_')
        self._mapper.resource('commit', 'commits',
            path_prefix='/repos/:repo_id/branches/:branch_id',
            name_prefix='commit_')

        self.config = request_config()
        self.config.mapper = self._mapper
        self.config.environ = self._environ

    def run_controller(self):
        controller = self.config.mapper_dict['controller']
        ControllerClass = self.controller_map[controller]
        controller = ControllerClass(self)

        try:
            controller.run()
        except:
            exc_string = traceback.format_exc()
            self.status('500 Server Error')
            self._output.truncate(0)
            self._output.write("""<html><head><title>Server Error</title></head><body><pre>%s</pre></body></html>""" % (exc_string))

    def set_repos(self, repos):
        self._repos = repos


class Controller(object):
    def __init__(self, rest):
        self.rest = rest

    def run(self):
        self.set_content_type()
        action = self.rest.match['action']
        if action not in ['show', 'index']:
            self.rest.status('420 Invalid action')
            self.rest.write("Invalid action")

        call = getattr(self, action)
        call()

    def set_content_type(self):
        self.accepts = []
        self.accepts.extend(
            parse_qs(self.rest._environ['QUERY_STRING'])
            .get('accept', [''])[0]
            .split(',')
        )
        self.accepts.extend(
            self.rest._environ.get('HTTP_ACCEPT', 'text/html').split(',')
        )
        self.accept = self.accepts[0] if self.accepts else 'text/html'

        for mimetype in ['application/json', 'text/plain', 'text/html']:
            if mimetype == self.accept:
                self.rest.content_type(mimetype)
                break

    def show(self):
        if 'application/json' == self.accept:
            self.json_resource()
        elif 'text/plain' == self.accept:
            self.plain_resource()
        else:
            self.html_resource()

    def index(self):
        if 'text/html' in self.accept:
            self.html_collection()
        elif 'application/json' in self.accept:
            self.json_collection()
        elif 'text/plain' in self.accept:
            self.plain_collection()
        else:
            self.html_collection()

    def json_collection(self):
        self.rest.write(dumps(self.get_collection()))

    def html_collection(self):
        self.rest.write("<html><head><title></title></head><body>")
        self.rest.write("<br />".join([ self.member_link(c) for c in self.get_collection()]))
        self.rest.write("</body></html>")

    def plain_collection(self):
        self.rest.write("plain %s" % (self.get_collection()))

    def json_resource(self):
        self.rest.write(dumps(self.get_member(self.match['id'])))

    def html_resource(self):
        id = self.rest.match['id']
        self.rest.write("<html><head><title>Repository %s</title></head><body>" % (id,))
        self.rest.write("<table>")
        for k,v in self.get_member(id).items():
            self.rest.write("<tr><td>%s</td><td>%s</td></tr>" % (k, v));
        self.rest.write("</table>")
        self.rest.write("</body></html>")

    def plain_resource(self):
        self.rest.write("plain %s" % (self.get_collection()))

class ReposController(Controller):
    def member_link(self, collection):
        return "<a href='%s'>%s</a>" % (url_for(controller='repos', action='show', id=collection['id']), collection['id'])

    def get_collection(self):
        repos = self.rest._repos.keys()
        repos.sort()
        return [ self.get_member(repo_id) for repo_id in repos ]

    def get_member(self, repo_id):
        if repo_id not in self.rest._repos.keys():
            # XXX how should we propagate errors?
            self.rest.status('404 Repo not found')
            return { 'id': 'not found', 'description': 'doesnt exist' }

        repo = git.Repo('repos/%s.git' % (repo_id,))
        repo_dict = {
            'id': repo_id,
            'description': repo.description,
            'branches': [ b.name for b in repo.branches ],
            'tree': [ item[0] for item in repo.tree().items() ]
        } 
        return repo_dict


class RootController(Controller):
     def index(self):
         self.rest.write("awesome rest server index")
# 
#     def show(self):
#         #self.rest.write("awesome rest server show")
#         pass
#    pass

class LoadsRepoMixin(object):
    def load_repo(self):
        if hasattr(self, 'repo'): return
        self.repo_name = self.rest.match['repo_id']
        self.repo = git.Repo('repos/' + self.repo_name + '.git')

    def validate_repo(self):
        load_repo()


class CommitsController(Controller, LoadsRepoMixin):
    def member_link(self, collection):
        return "<a href='%s'>%s</a>" % (url_for(controller='commits',
            repo_id=self.rest.match['repo_id'], action='show',
            id=collection['id']), collection['id'])

    def get_collection(self):
        self.load_repo()
        return [
            { 'id': c.id, 'summary': c.summary }
            for c in self.repo.commits()
        ]

    def get_member(self, id):
        self.load_repo()
        c = self.repo.commit(id)
        return { 'message': c.message, 'actor': c.author.name}

class BranchesController(Controller, LoadsRepoMixin):
    pass
