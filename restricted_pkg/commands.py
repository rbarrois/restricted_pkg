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
from setuptools.command.register import register as setuptools_register
from setuptools.command.upload_docs import upload_docs as setuptools_upload_docs

from . import base


DEFAULT_PYPI_RC = '~/.pypirc'


def get_repo_url(pypirc, repository):
    """Fetch the RepositoryURL for a given repository, reading info from pypirc.

    Will try to find the repository in the .pypirc, including username/password.

    Args:
        pypirc (str): path to the .pypirc config file
        repository (str): URL or alias for the repository

    Returns:
        base.RepositoryURL for the repository
    """
    pypirc = os.path.abspath(os.path.expanduser(pypirc))
    pypi_config = base.PyPIConfig(pypirc)
    repo_config = pypi_config.get_repo_config(repository)
    if repo_config:
        return repo_config.get_clean_url()
    else:
        return base.RepositoryURL(repository)


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

        repo_url = get_repo_url(self.pypirc, self.distribution.private_repository)

        if self.disable_pypi:
            self._clean_find_links()
            self.find_links.append(repo_url)
        else:
            self.index_url = repo_url

        setuptools_easy_install.finalize_options(self)


class register(setuptools_register):
    user_options = setuptools_register.user_options + [
        ('pypirc', None, "Path to .pypirc configuration file"),
    ]

    def initialize_options(self):
        setuptools_register.initialize_options(self)
        self.pypirc = None

    def get_repository_config(self, repository):
        pypi_config = base.PyPIConfig(self.pypirc)
        return pypi_config.get_repo_config(repository)

    def finalize_options(self):
        if self.distribution.private_repository is None:
            raise DistutilsSetupError(
                "The 'private_repository' argument to the setup() call is required."
            )

        self.pypirc = self.pypirc or DEFAULT_PYPI_RC
        package_repo = base.RepositoryURL(self.distribution.private_repository)
        repo_url = get_repo_url(self.pypirc, self.repository or package_repo.base_url)

        if self.repository and repo_url not in package_repo:
            raise DistutilsOptionError(
                "The --repository option of private packages must match the "
                "configured private repository, %s." % package_repo.base_url
            )

        self.repository = repo_url.base_url
        self.username = repo_url.username
        self.password = repo_url.password

        setuptools_register.finalize_options(self)


class upload(setuptools_upload):
    user_options = setuptools_upload.user_options + [
        ('pypirc', None, "Path to .pypirc configuration file"),
    ]

    def initialize_options(self):
        setuptools_upload.initialize_options(self)
        self.pypirc = None

    def get_repository_config(self, repository):
        pypi_config = base.PyPIConfig(self.pypirc)
        return pypi_config.get_repo_config(repository)

    def finalize_options(self):
        if self.distribution.private_repository is None:
            raise DistutilsSetupError(
                "The 'private_repository' argument to the setup() call is required."
            )

        self.pypirc = self.pypirc or DEFAULT_PYPI_RC
        package_repo = base.RepositoryURL(self.distribution.private_repository)
        repo_url = get_repo_url(self.pypirc, self.repository or package_repo.base_url)

        if self.repository and repo_url not in package_repo:
            raise DistutilsOptionError(
                "The --repository option of private packages must match the "
                "configured private repository, %s." % package_repo.base_url
            )

        self.repository = repo_url.base_url
        self.username = repo_url.username
        self.password = repo_url.password

        setuptools_upload.finalize_options(self)


class upload_docs(setuptools_upload_docs):
    user_options = setuptools_upload_docs.user_options + [
        ('pypirc', None, "Path to .pypirc configuration file"),
    ]

    def initialize_options(self):
        setuptools_upload_docs.initialize_options(self)
        self.pypirc = None

    def get_repository_config(self, repository):
        pypi_config = base.PyPIConfig(self.pypirc)
        return pypi_config.get_repo_config(repository)

    def finalize_options(self):
        if self.distribution.private_repository is None:
            raise DistutilsSetupError(
                "The 'private_repository' argument to the setup() call is required."
            )

        self.pypirc = self.pypirc or DEFAULT_PYPI_RC
        package_repo = base.RepositoryURL(self.distribution.private_repository)
        repo_url = get_repo_url(self.pypirc, self.repository or package_repo.base_url)

        if self.repository and repo_url not in package_repo:
            raise DistutilsOptionError(
                "The --repository option of private packages must match the "
                "configured private repository, %s." % package_repo.base_url
            )

        self.repository = repo_url.base_url
        self.username = repo_url.username
        self.password = repo_url.password

        setuptools_upload_docs.finalize_options(self)


def setup(**kwargs):
    """Custom setup() function, inserting our custom classes."""

    cmdclass = kwargs.setdefault('cmdclass', {})
    cmdclass['easy_install'] = easy_install
    cmdclass['register'] = register
    cmdclass['upload'] = upload
    cmdclass['upload_docs'] = upload_docs
    return setuptools.setup(**kwargs)
