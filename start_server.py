#!/usr/bin/python
import sys
from wsgiref.simple_server import make_server

sys.path.append('lib')
import grwsgi

port = int(sys.argv[1])
httpd = make_server('', port, grwsgi.application)
httpd.serve_forever()
