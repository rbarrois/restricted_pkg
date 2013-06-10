# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Raphaël Barrois.
# Distributed under the MIT License.


import unittest


from restricted_pkg import base


class RepositoryURLTestCase(unittest.TestCase):
    def test_unauthenticated_simple_url(self):
        u = base.RepositoryURL('http://example.com/')
        self.assertFalse(u.needs_auth)
        self.assertEqual('http://example.com/', u.base_url)
        self.assertEqual('http://example.com/', u.full_url)
        self.assertEqual('http://example.com/', str(u))

    def test_unauthenticated_complex_url(self):
        u = base.RepositoryURL('http://example.com:42/foo/?bar=42#13')
        self.assertFalse(u.needs_auth)
        self.assertEqual('http://example.com:42/foo/?bar=42#13', u.base_url)
        self.assertEqual('http://example.com:42/foo/?bar=42#13', u.full_url)
        self.assertEqual('http://example.com:42/foo/?bar=42#13', str(u))

    def test_fully_authenticated_simple_url(self):
        u = base.RepositoryURL('http://john:doe@example.com/')
        self.assertTrue(u.needs_auth)
        self.assertEqual('http://example.com/', u.base_url)
        self.assertEqual('http://john:doe@example.com/', u.full_url)
        self.assertEqual('http://john:doe@example.com/', str(u))

    def test_fully_authenticated_complex_url(self):
        u = base.RepositoryURL('http://john:doe@example.com:42/foo/?bar=42#13')
        self.assertTrue(u.needs_auth)
        self.assertEqual('http://example.com:42/foo/?bar=42#13', u.base_url)
        self.assertEqual('http://john:doe@example.com:42/foo/?bar=42#13', u.full_url)
        self.assertEqual('http://john:doe@example.com:42/foo/?bar=42#13', str(u))

    def test_partially_authenticated_simple_url(self):
        u = base.RepositoryURL('http://@example.com/')
        self.assertTrue(u.needs_auth)
        self.assertEqual('http://example.com/', u.base_url)
        self.assertEqual('http://:@example.com/', u.full_url)
        self.assertEqual('http://:@example.com/', str(u))

    def test_partially_authenticated_complex_url(self):
        u = base.RepositoryURL('http://@example.com:42/foo/?bar=42#13')
        self.assertTrue(u.needs_auth)
        self.assertEqual('http://example.com:42/foo/?bar=42#13', u.base_url)
        self.assertEqual('http://:@example.com:42/foo/?bar=42#13', u.full_url)
        self.assertEqual('http://:@example.com:42/foo/?bar=42#13', str(u))
