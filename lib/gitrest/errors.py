#!python

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
