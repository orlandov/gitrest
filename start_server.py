#!/usr/bin/python
import sys
from wsgiref.simple_server import make_server

sys.path.append('lib')

import gitrest
import grwsgi

def reload_application(*args):
    reload(gitrest)
    return grwsgi.application(*args)

port = int(sys.argv[1])
httpd = make_server('', port, reload_application)
httpd.serve_forever()
