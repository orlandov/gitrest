#!/usr/bin/python
import sys
from wsgiref.simple_server import make_server

sys.path.append('lib')

import gitrest
import grwsgi

def reload_application(*args):
    reload(gitrest)
    return grwsgi.application(*args)

try:
    port = int(sys.argv[1])
except IndexError:
    port = 9000

httpd = make_server('', port, reload_application)
httpd.serve_forever()
