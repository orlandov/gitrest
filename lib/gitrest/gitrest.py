#!python

from simplejson import dumps, loads
import git
import sys
import traceback
from routes import request_config

from rest import application
import config
import controllers
import errors
import gitrest

class GitRest(application.Application):
    def init_controllers(self):
        self.controller_map = {
            'commits': controllers.CommitsController,
            'repos': controllers.ReposController,
            'branches': controllers.BranchesController,
            'root': controllers.RootController,
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
        controller_name = self.config.mapper_dict['controller']
        ControllerClass = self.controller_map[controller_name]

        try:
            ControllerClass(self).run()
        except Exception, e:
            self._output.truncate(0)
            if issubclass(e.__class__, errors.GitRestError):
                self.status(e.status)
                self.write(str(e))
            else:
                exc_string = traceback.format_exc()
                self.status('500 Server Error')
                self.write("""<html><head><title>Server Error</title></head><body><pre>%s</pre></body></html>""" % (exc_string))

    def set_repos(self, repos):
        self._repos = repos
