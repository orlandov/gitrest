#!python

import os, sys
sys.path.append('/home/orlando/projects/gr/lib')

from GitRest import GitRest

def application(environ, start_response):
    gr = GitRest(environ, start_response)
    return gr.serve()

def parse_fields(self):
    s = self.environ['wsgi.input'].read(int(self.environ['CONTENT_LENGTH']))
    return cgi.parse_qs(s)
