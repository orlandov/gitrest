#!python

from cgi import parse_qs
from routes import Mapper, request_config, url_for
from simplejson import dumps, loads
import git
import sys
import traceback

import config
import gitrest

import rest.application

class GitRest(rest.application.Application):
    def init_controllers(self):
        self.controller_map = {
            'commits': CommitsController,
            'repos': ReposController,
            'branches': BranchesController,
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
        except Exception, e:
            self._output.truncate(0)
            if issubclass(e.__class__, GitRestError):
                self.status(e.status)
                self.write(str(e))
            else:
                exc_string = traceback.format_exc()
                self.status('500 Server Error')
                self.write("""<html><head><title>Server Error</title></head><body><pre>%s</pre></body></html>""" % (exc_string))

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
        query_string = self.rest._environ['QUERY_STRING']
        accept_header = self.rest._environ.get('HTTP_ACCEPT')

        self.accepts = []

        # extend accepts with the query string parameter
        qs_accept = parse_qs(query_string).get('accept', [''])
        self.accepts.extend(
            qs_accept[0].split(',') if len(qs_accept) > 0 and qs_accept[0] else []
        )
        # extend accepts with the header values
        self.accepts.extend(
            accept_header.split(',')
        )
        self.accept = self.accepts[0]

        for mimetype in ['application/json', 'text/plain', 'text/html']:
            if mimetype == self.accept:
                self.rest.content_type(mimetype)
                break

    def show(self):
        self.id = self.rest.match['id']
        mime_functions = {
            'application/json': self.json_resource,
            'text/html': self.html_resource,
            'text/plain': self.plain_resource,
            '*/*': self.html_resource
        }
        mime_functions.get(self.accept, mime_functions['*/*'])()

    def index(self):
        mime_functions = {
            'application/json': self.json_collection,
            'text/html': self.html_collection,
            'text/plain': self.plain_collection,
            '*/*': self.html_collection
        }
        mime_functions.get(self.accept, mime_functions['*/*'])()

    def json_resource(self):
        self.rest.write(dumps(self.get_member(self.id)))

    def json_collection(self):
        self.rest.write(dumps(self.get_collection()))

    def html_resource(self):
        self.rest.write("<html><head><title>Repository %s</title></head><body>" % (self.id,))
        self.rest.write("<table>")
        for k,v in self.get_member(self.id).items():
            self.rest.write("<tr><td>%s</td><td>%s</td></tr>" % (k, v));
        self.rest.write("</table>")
        self.rest.write("</body></html>")

    def html_collection(self):
        self.rest.write("<html><head><title></title></head><body>")
        self.rest.write("<br />".join([ self.member_link(c) for c in self.get_collection()]))
        self.rest.write("</body></html>")

    def plain_resource(self):
        self.rest.write("plain %s" % (self.get_member(self.id)))

    def plain_collection(self):
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

        repo = gitrest.config.repo(repo_id)
        repo_dict = {
            'id': repo_id,
            'description': repo.description,
            'branches': [ b.name for b in repo.branches ],
            'tree': [ item[0] for item in repo.tree().items() ]
        } 
        return repo_dict

class GitRestError(Exception):
    pass


class InvalidRepoError(GitRestError):
    def __init__(self, **kwargs):
        self.repo_id = kwargs['repo_id']
        self.status='404 Invalid repo'

    def __str__(self):
        return "Invalid repo, '%s'" % (self.repo_id,)


class InvalidBranchError(GitRestError):
    def __init__(self, **kwargs):
        self.branch_id = kwargs['branch_id']
        self.status='404 Invalid branch'

    def __str__(self):
        return "Invalid branch, '%s'" % (self.branch_id,)


class RootController(Controller):
     def index(self):
         self.rest.write("awesome rest server index")


class LoadsRepoMixin(object):
    def load_repo(self):
        if hasattr(self, 'repo'): return
        self.repo_id = self.rest.match['repo_id']
        try:
            self.repo = gitrest.config.repo(self.repo_id)
        except git.errors.NoSuchPathError:
            raise InvalidRepoError(repo_id=self.repo_id)


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
    def member_link(self, collection):
        pass

    def get_collection(self):
        self.load_repo()
        return [
            { 'commit_id': b.commit.id, 'branch_id': b.name }
            for b in self.repo.branches
        ]

    def get_member(self, id):
        self.load_repo()
        for b in self.repo.branches:
            if b.name == id:
                return { 'commit_id': b.commit.id, 'branch_id': b.name } 
        raise InvalidBranchError(branch_id=id)
