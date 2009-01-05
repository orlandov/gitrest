#!python

from cgi import parse_qs
from simplejson import dumps, loads

class Controller(object):
    def __init__(self, rest):
        self.rest = rest

    def run(self):
        self.set_content_type()
        action = self.rest.match['action']
        if action not in ['show', 'index']:
            self.rest.status('420 Invalid action')
            self.rest.write("Invalid action")

        call = getattr(self, action)
        call()

    def set_content_type(self):
        query_string = self.rest._environ['QUERY_STRING']
        accept_header = self.rest._environ.get('HTTP_ACCEPT')

        self.accepts = []

        # extend accepts with the query string parameter
        qs_accept = parse_qs(query_string).get('accept', [''])
        self.accepts.extend(
            qs_accept[0].split(',') if len(qs_accept) > 0 and qs_accept[0] else []
        )
        # extend accepts with the header values
        self.accepts.extend(
            accept_header.split(',')
        )
        self.accept = self.accepts[0]

        for mimetype in ['application/json', 'text/plain', 'text/html']:
            if mimetype == self.accept:
                self.rest.content_type(mimetype)
                break

    def show(self):
        self.id = self.rest.match['id']
        mime_functions = {
            'application/json': self.json_resource,
            'text/html': self.html_resource,
            'text/plain': self.plain_resource,
            '*/*': self.html_resource
        }
        mime_functions.get(self.accept, mime_functions['*/*'])()

    def index(self):
        mime_functions = {
            'application/json': self.json_collection,
            'text/html': self.html_collection,
            'text/plain': self.plain_collection,
            '*/*': self.html_collection
        }
        mime_functions.get(self.accept, mime_functions['*/*'])()

    def json_resource(self):
        self.rest.write(dumps(self.get_member(self.id)))

    def json_collection(self):
        self.rest.write(dumps(self.get_collection()))

    def html_resource(self):
        self.rest.write("<html><head><title>Repository %s</title></head><body>" % (self.id,))
        self.rest.write("<table>")
        for k,v in self.get_member(self.id).items():
            self.rest.write("<tr><td>%s</td><td>%s</td></tr>" % (k, v));
        self.rest.write("</table>")
        self.rest.write("</body></html>")

    def html_collection(self):
        self.rest.write("<html><head><title></title></head><body>")
        self.rest.write("<br />".join([ self.member_link(c) for c in self.get_collection()]))
        self.rest.write("</body></html>")

    def plain_resource(self):
        self.rest.write("plain %s" % (self.get_member(self.id)))

    def plain_collection(self):
        self.rest.write("plain %s" % (self.get_collection()))
