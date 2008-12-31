#!python

import unittest

from resttest import RestTest
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


class TestRepos(unittest.TestCase, RestTest):
    def setUp(self):
        self.start_server()

    def test_repos(self):
        self.GET_json('/repos')
        self.assert_code(200)
        self.assert_json([u'a', u'b'])

class TestRepo(unittest.TestCase, RestTest):
    def setUp(self):
        self.start_server()

    def test_invalid_repo(self):
        self.GET('/repos/fake')
        self.assert_code(404)

    def test_repo_description(self):
        self.GET_json('/repos/a')
        self.assert_code(200)

    def test_repo_description_json(self):
        self.GET_json('/repos/a')
        self.assert_code(200)
        self.assert_json({
            'repo': 'a',
            'description': 'This is the description of a.git',
            'branches' : ['master'],
            'tree': ['lib', 'LICENSE', 'doc', 'MANIFEST.in', '.gitignore', 
            'test', 'VERSION', 'AUTHORS', 'README', 'ez_setup.py',
            'setup.py', 'CHANGES'],
        })
