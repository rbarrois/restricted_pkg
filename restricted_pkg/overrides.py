# -*- coding: utf-8 -*-
# Copyright (c) 2012 Raphaël Barrois.
# Distributed under the MIT License.

from urllib2 import urlparse
import re
import sys

from distutils.errors import DistutilsOptionError, DistutilsSetupError

import setuptools
from setuptools.command.easy_install import easy_install as setuptools_easy_install
from setuptools.command.upload import upload as setuptools_upload


DEFAULT_PYPI_RC = '~/.pypirc'


class URLCleaner(object):
    def __init__(self, repo_url):
        self.repo_url = repo_url
        self.need_auth = False

        self.url_credentials = ('', '')
        self.config_credentials = ('', '')
        self.prompted_credentials = ('', '')

        self.split_url(self.repo_url)

    def split_url(self, url):
        scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
        if '@' in netloc:
            self.need_auth = True
            ident, netloc = netloc.rsplit('@', 1)
            if ':' in ident:
                username, password = ident.split(':', 1)
            else:
                username = ident
                password = ''
            self.url_credentials = (username, password)

        self.url_components = (scheme, netloc, path, params, query, fragment)

    def fill(self, config_file):
        if not self.need_auth:
            return

        if self.has_credentials():
            return

        self.fill_from_file(config_file)

        while not self.has_credentials():
            self.fill_from_prompt()

        if self.prompted_credentials:
            self.write_to_file(config_file)

    def fill_from_file(self, path):
        config = ConfigParser(path)
        self.config_credentials = (
            config.get(self.repo_url, 'username', ''),
            config.get(self.repo_url, 'password', ''),
        )

    def fill_from_prompt(self):
        sys.stdout.write("Please insert your credentials for %s\n" % self.repo_url)
        username = raw_input("Username [%s]: ")
        password = getpass.getpass("Password: ")

        self.prompted_credentials = (username, password)

    def write_to_file(self, path):
        config = ConfigParser(path)
        if not config.has_section(repository):
            config.add_section(repository)
        
        username, password = self.credentials
        config.set(self.repo_url, 'username', username)
        config.set(self.repo_url, 'password', password)

        config.save()

    @property
    def credentials(self):
        return (self.prompted_credentials
            or self.url_credentials
            or self.config_credentials)

    def has_credentials(self):
        username, password = self.credentials
        return bool(username and password)

    def get_full_url(self):
        scheme, netloc, path, params, query, fragment = self.url_components
        if self.need_auth:
            auth = '%s:%s' % self.credentials
            netloc = '%s@%s' % (auth, netloc)

        return urlparse.urlunparse(
            (scheme, netloc, path, params, query, fragment))


class easy_install(setuptools_easy_install):

    user_options = setuptools_easy_install.user_options + [
        ('disable-pypi', None, "Don't use PyPI package index"),
        ('pypirc', None, "Path to .pypirc configuration file"),
    ]

    def initialize_options(self):
        setuptools_easy_install.initialize_options(self)
        self.disable_pypi = False
        self.pypirc = None

    def _clean_find_links(self):
        if self.find_links is not None:
            if isinstance(self.find_links, str):
                self.find_links = self.find_links.split()
        else:
            self.find_links = []

    def finalize_options(self):
        if self.distribution.private_repository is None:
            raise DistutilsSetupError(
                "The 'private_repository' argument to the setup() call is required."
            )
        self.pypirc = self.pypirc or DEFAULT_PYPI_RC

        repo = self.distribution.private_repository
        cleaner = URLCleaner(repo)

        cleaner.fill(self.pypirc)
        repo = cleaner.get_full_url()

        if self.disable_pypi:
            self._clean_find_links()
            self.find_links.append(repo)
        else:
            self.index_url = repo

        setuptools_easy_install.finalize_options(self)


class upload(setuptools_upload):
    user_options = setuptools_upload.user_options + [
        ('pypirc', None, "Path to .pypirc configuration file"),
    ]

    def initialize_options(self):
        setuptools_upload.initialize_options(self)
        self.pypirc = None

    def finalize_options(self):
        if self.distribution.private_repository is None:
            raise DistutilsSetupError(
                "The 'private_repository' argument to the setup() call is required."
            )

        self.pypirc = self.pypirc or DEFAULT_PYPI_RC
        repo = self.distribution.private_repository

        if self.repository and self.repository != repo:
            raise DistutilsOptionError(
                "The --repository option of private packages must match the "
                "configured private repository, %s." % repo
            )
        self.repository = self.distribution.private_repository

        setuptools_upload.finalize_options(self)


def setup(**kwargs):
    cmdclass = kwargs.setdefault('cmdclass', {})
    cmdclass['easy_install'] = easy_install
    cmdclass['upload'] = upload
    return setuptools.setup(**kwargs)
