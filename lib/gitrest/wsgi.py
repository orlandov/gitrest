#!python

import os
import sys
sys.path.append('/home/orlando/projects/gr/lib')

import config
from gitrest import GitRest

def application(environ, start_response):
    gr = GitRest(environ, start_response)
    config.setup()
    gr.set_repos(config.Settings.repos)
    return gr.serve()
