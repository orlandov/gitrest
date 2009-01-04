#!python

import os
import sys
sys.path.append('/home/orlando/projects/gr.git/lib')

import grconfig
from gitrest import GitRest

def application(environ, start_response):
    gr = GitRest(environ, start_response)
    grconfig.setup()
    gr.set_repos(grconfig.Settings.repos)
    return gr.serve()
