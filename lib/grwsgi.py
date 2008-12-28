#!python

import os
import sys
import re
sys.path.append('/home/orlando/projects/gr.git/lib')

from gitrest import GitRest

repos = {
}

for dir in os.listdir('repos'):
    match = re.match('([^/]+)\\.git$', dir)
    if match:
        repos[match.groups()[0]] = dir

def application(environ, start_response):
    gr = GitRest(environ, start_response)
    gr.set_repos(repos)
    return gr.serve()
