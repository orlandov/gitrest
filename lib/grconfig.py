#!python

import os
import os.path
import re
import git

class Settings(object):
    repos_dir = '/home/orlando/projects/gr/tests/repos'
    repos = {}

def repo(repo_name):
    return git.Repo("%s/%s.git" % (Settings.repos_dir, repo_name))

def setup():
    r = re.compile('([^/]+)\\.git$')
    Settings.repos = {}
    repos_dir = Settings.repos_dir

    for d in os.listdir(repos_dir):
        m = r.match(d)
        repo_name = m.groups()[0]
        path = "%s/%s.git" % (repos_dir, repo_name)
        if m and os.path.isdir(path):
            Settings.repos[repo_name] = path
