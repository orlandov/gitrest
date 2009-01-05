#!python

from cgi import parse_qs
from routes import Mapper, request_config, url_for
import git

from rest import controller
import config
import errors

class RootController(controller.Controller):
     def index(self):
         self.rest.write("awesome rest server index")


class LoadsRepoMixin(object):
    def load_repo(self):
        if hasattr(self, 'repo'): return
        self.repo_id = self.rest.match['repo_id']
        try:
            self.repo = config.repo(self.repo_id)
        except git.errors.NoSuchPathError:
            raise errors.InvalidRepoError(repo_id=self.repo_id)


class ReposController(controller.Controller):
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

        repo = config.repo(repo_id)
        repo_dict = {
            'id': repo_id,
            'description': repo.description,
            'branches': [ b.name for b in repo.branches ],
            'tree': [ item[0] for item in repo.tree().items() ]
        } 
        return repo_dict


class CommitsController(controller.Controller, LoadsRepoMixin):
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


class BranchesController(controller.Controller, LoadsRepoMixin):
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
        raise errors.InvalidBranchError(branch_id=id)
