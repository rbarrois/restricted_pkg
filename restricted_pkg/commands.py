# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Raphaël Barrois.
# Distributed under the MIT License.

import os
import re
import sys

from distutils.errors import DistutilsOptionError, DistutilsSetupError
from distutils import log
import setuptools
from setuptools.command.install import install as base_install
from setuptools.command.easy_install import easy_install as base_easy_install
from setuptools.command.upload_docs import upload_docs as base_upload_docs


from .compat import urlparse


try:
    from distutils.command.upload import upload as base_upload
except ImportError:
    from setuptools.command.upload import upload as base_upload
try:
    from distutils.command.register import register as base_register
except ImportError:
    from setuptools.command.register import register as base_register

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


class install(base_install):
    """Overridden install which adds --disable-pypi and --pypirc options."""
    user_options = base_install.user_options + [
        ('disable-pypi', None, "Don't use PyPI package index"),
        ('pypirc=', None, "Path to .pypirc configuration file"),
    ]
    boolean_options = base_install.boolean_options + ['disable-pypi']

    def initialize_options(self):
        base_install.initialize_options(self)
        self.disable_pypi = None
        self.pypirc = None


class easy_install(base_easy_install):
    """Overridden easy_install which adds a url from private_repository.

    Also handles username/password prompting for that private_repository.
    """

    user_options = base_easy_install.user_options + [
        ('disable-pypi', None, "Don't use PyPI package index"),
        ('pypirc=', None, "Path to .pypirc configuration file"),
    ]
    boolean_options = base_easy_install.boolean_options + ['disable-pypi']

    def initialize_options(self):
        base_easy_install.initialize_options(self)
        self.disable_pypi = None
        self.pypirc = None

    def finalize_options(self):
        if self.distribution.private_repository is None:
            raise DistutilsSetupError(
                "The 'private_repository' argument to the setup() call is required."
            )
        self.pypirc = self.pypirc or DEFAULT_PYPI_RC

        repo_url = get_repo_url(self.pypirc, self.distribution.private_repository)

        # Retrieve disable_pypi from install
        self.set_undefined_options('install', ('disable_pypi', 'disable_pypi'))

        if self.disable_pypi:
            log.info("Replacing PyPI with private repository %s.",
                repo_url.base_url)
            # Replace PyPI
            self.index_url = repo_url.full_url
            # Disable find_links option inherited from packages
            self.no_find_links = True

        else:
            # Clean up self.find_links
            self.find_links = self.find_links or []
            self.ensure_string_list('find_links')

            # Add custom URL
            log.info("Adding private repository %s to searched repositories.",
                repo_url.base_url)
            self.find_links.append(repo_url.full_url)

        # Parent options
        base_easy_install.finalize_options(self)


class register(base_register):
    """Overridden register command restricting upload to the private repo."""

    user_options = base_register.user_options + [
        ('pypirc=', None, "Path to .pypirc configuration file"),
    ]

    def initialize_options(self):
        base_register.initialize_options(self)
        self.pypirc = None

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

        log.info("Switching to private repository at %s", package_repo.base_url)
        self.repository = repo_url.base_url
        self.username = repo_url.username
        self.password = repo_url.password

        base_register.finalize_options(self)


class upload(base_upload):
    """Overridden upload command restricting upload to the private repo."""

    user_options = base_upload.user_options + [
        ('pypirc=', None, "Path to .pypirc configuration file"),
    ]

    def initialize_options(self):
        base_upload.initialize_options(self)
        self.pypirc = None

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

        log.info("Switching to private repository at %s", package_repo.base_url)
        self.repository = repo_url.base_url
        self.username = repo_url.username
        self.password = repo_url.password

        base_upload.finalize_options(self)


class upload_docs(base_upload_docs):
    """Overridden upload_docs command restricting upload to the private repo."""

    user_options = base_upload_docs.user_options + [
        ('pypirc=', None, "Path to .pypirc configuration file"),
    ]

    def initialize_options(self):
        base_upload_docs.initialize_options(self)
        self.pypirc = None

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

        log.info("Switching to private repository at %s", package_repo.base_url)
        self.repository = repo_url.base_url
        self.username = repo_url.username
        self.password = repo_url.password

        base_upload_docs.finalize_options(self)


def setup(**kwargs):
    """Custom setup() function, inserting our custom classes."""

    cmdclass = kwargs.setdefault('cmdclass', {})
    cmdclass['easy_install'] = easy_install
    cmdclass['install'] = install
    cmdclass['register'] = register
    cmdclass['upload'] = upload
    cmdclass['upload_docs'] = upload_docs
    return setuptools.setup(**kwargs)
