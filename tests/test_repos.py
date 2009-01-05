#!python

import unittest
import os
import os.path

from resttest import RestTest
import grconfig
import grwsgi

# class TestRoot(unittest.TestCase, RestTest):
#     def setUp(self):
#         self.start_server()
# 
#     def test_repos(self):
#         self.GET_json('/')
#         self.assert_code(200)
#         self.assert_json([u'a', u'b'])
# 
#     def test_invalid_path(self):
#         self.GET('/invalid')
#         self.assert_code(404)

def setup_repos():
    if not os.path.isdir('repos'):
        os.system("cd tests; tar zxf repos.tgz")
        grconfig.Settings.repos_dir = 'tests/repos'

class TestContentType(unittest.TestCase, RestTest):
    def setUp(self):
        self.start_server()
        setup_repos()

    def test_json_header(self):
        self.GET('/repos', { 'Accept': 'application/json, text/html' })
        self.assert_code(200)
        self.assert_content_type('application/json')
        self.GET_json('/repos')
        self.assert_code(200)
        self.assert_content_type('application/json')

    def test_json_qs(self):
        self.GET('/repos?accept=application/json')
        self.assert_code(200)
        self.assert_content_type('application/json')

    def test_json_qs_override_header(self):
        self.GET('/repos?accept=application/json', { 'Accept': 'text/html' })
        self.assert_code(200)
        self.assert_content_type('application/json')

    def test_html_header(self):
        self.GET('/repos', { 'Accept': 'text/html, application/json' })
        self.assert_code(200)
        self.assert_content_type('text/html')

    def test_html_qs(self):
        self.GET('/repos?accept=text/html')
        self.assert_code(200)
        self.assert_content_type('text/html')

    def test_html_qs_override_header(self):
        self.GET('/repos?accept=text/html', { 'Accept': 'application/json' })
        self.assert_code(200)
        self.assert_content_type('text/html')

    def test_html_unsupported_accept_qs(self):
        self.GET('/repos?accept=cats/manecoon')
        self.assert_code(200)
        self.assert_content_type('text/html')

    def test_unsupported_accept_header(self):
        self.GET('/repos', { 'Accept': 'cats/manecoon' })
        self.assert_code(200)
        self.assert_content_type('text/html')

class TestRepos(unittest.TestCase, RestTest):
    def setUp(self):
        self.start_server()
        setup_repos()

    def test_repos(self):
        self.GET_json('/repos')
        self.assert_code(200)
        self.assertTrue(self.json_object is not [], "make sure we got some values back")
        for r in self.json_object:
            self.assertTrue(r.has_key('tree'))
            self.assertTrue(r.has_key('branches'))
            self.assertTrue(r.has_key('description'))
            self.assertTrue(r.has_key('id'))

    def test_invalid_repo(self):
        self.GET('/repos/fake')
        self.assert_code(404)

    def test_repo_description(self):
        self.GET_json('/repos/a')
        self.assert_code(200)
        self.assertTrue(self.json_object.has_key('tree'))
        self.assertTrue(self.json_object.has_key('branches'))
        self.assertTrue(self.json_object.has_key('description'))
        self.assertTrue(self.json_object.has_key('id'))
