# -*- coding: utf-8 -*-
# Copyright (c) 2012 Raphaël Barrois.
# Distributed under the MIT License.


"""Handle repository-related logic."""

import ConfigParser
import getpass
import urlparse


class RepositoryURL(object):
    """Representation of a repository URL.

    Also handles auth.

    Attributes:
        scheme, netloc, path, params, query, fragment: usual URL components
        with_auth (bool): whether the URL requires auth
        username (str): Username to use for the URL
        password (str): password to use for the URL
    """

    def __init__(self, url):
        scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
        self.scheme = scheme

        self.with_auth = False
        self.username = self.password = ''

        if '@' in netloc:
            self.with_auth = True
            ident, self.netloc = netloc.rsplit('@', 1)
            if ':' in ident:
                self.username, self.password = ident.split(':', 1)
        else:
            self.netloc = netloc

        self.path = path
        self.params = params
        self.query = query
        self.fragment = fragment

    def __contains__(self, other):
        """Another url is 'contained' if it shares scheme, host, path prefix."""
        if not isinstance(other, RepositoryURL):
            return NotImplemented

        return (self.scheme == other.scheme
            and self.netloc == other.netloc
            and other.path.startswith(self.path)
        )

    @property
    def needs_auth(self):
        """Whether this server needs auth."""
        return bool(self.with_auth or self.username or self.password)

    @property
    def base_url(self):
        """The base, unauthenticated URL for the repository."""
        return urlparse.urlunparse((
            self.scheme,
            self.netloc,
            self.path,
            self.params,
            self.query,
            self.fragment,
        ))

    @property
    def full_url(self):
        """The full URL, including username/password."""
        if self.needs_auth:
            netloc = '%s:%s@%s' % (self.username, self.password, self.netloc)
        else:
            netloc = self.netloc
        return urlparse.urlunparse((
            self.scheme,
            netloc,
            self.path,
            self.params,
            self.query,
            self.fragment,
        ))

    def __str__(self):
        return self.full_url


class RepositoryConfig(object):
    """Holds data about a .pypirc repository entry.

    Attributes:
        name (str): 'realm', alias for the repository
        url (RepositoryURL): the URL of the repository
        username (str): username to connect to the repository
        password (str): password to connect to the repository
    """

    def __init__(self, name):
        self.name = name
        self.url = None
        self.username = ''
        self.password = ''

    def fill(self, config, section):
        """Fill data from a given configuration section.

        Args:
            config (ConfigParser): the configuration file
            section (str): the section to use
        """
        if config.has_section(section):
            self.url = RepositoryURL(config.get(section, 'repository', ''))
            self.username = config.get(section, 'username', '')
            self.password = config.get(section, 'password', '')

    def prompt_auth(self):
        """Prompt the user for login/pass, if needed."""
        if self.username and self.password:
            return
        sys.stdout.write("Please insert your credentials for %s\n" % self.repo_url)
        while not self.username:
            self.username = raw_input("Username [%s]: " % getpass.getuser())

        while not self.password:
            self.password = getpass.getpass("Password: ")

    @property
    def needs_auth(self):
        """Whether this repository needs authentication."""
        return self.username or self.password or self.url.needs_auth

    def get_clean_url(self):
        """Retrieve the clean, full URL - including username/password."""
        if self.needs_auth:
            self.prompt_auth()
        url = RepositoryURL(self.url.full_url)
        url.username = self.username
        url.password = self.password
        return url


class PyPIConfig(object):
    """Representation of a .pypirc config file.

    Attributes:
        path (str): path to the .pypirc file
        repositories (RepositoryConfig list): configured repositories
    """
    def __init__(self, path):
        self.path = path
        self.repositories = []
        self._read_config()

    def _read_config(self):
        """Read the configuration file."""
        config = ConfigParser.ConfigParser(self.path)
        if config.has_section('distutils'):
            servers = [server.strip() for server in config.get('distutils', 'index-servers', '')]
            servers = [server for server in servers if server]

            for server in servers:
                repo_config = RepositoryConfig(server)
                repo_config.fill(config, server)
                self.repositories.append(repo_config)

        repo_config = RepositoryConfig('default')
        repo_config.fill(config, 'server-login')

    def get_repo_config(self, repo='default'):
        """Retrieve configuration for a given repository.

        Args:
            repo (str): a repository "realm" (alias) or its URL

        Returns:
            RepositoryConfig: if there is configuration for that repository
            None: otherwise
        """
        for repo_config in self.repositories:
            if repo_config.name == repo or repo_config.url in RepositoryURL(repo):
                return repo_config

        return None
