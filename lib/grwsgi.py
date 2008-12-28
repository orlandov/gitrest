#!python

import os, sys
sys.path.append('/home/orlando/projects/gr.git/lib')

from gitrest import GitRest

repos = {
    'sample.git': '/home/orlando/projects/sample.git',
    'gr.git': '/home/orlando/projects/gr.git',
    'sudobangbang.git': '/home/orlando/projects/sudobangbang.git'        
}

def application(environ, start_response):
    gr = GitRest(environ, start_response)
    gr.set_repos(repos)
    return gr.serve()
