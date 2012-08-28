# -*- coding: utf-8 -*-
# Copyright (c) 2012 Raphaël Barrois.
# Distributed under the MIT License.


"""Handle repository-related logic."""


class RepositoryURL(object):

    def __init__(self, url):
        scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
        self.scheme = scheme

        self.with_auth = '@' in netloc
        ident, self.netloc = netloc.rsplit('@', 1)
        if ':' in ident:
            self.username, self.password = ident.split(':', 1)
        else:
            self.username = self.password = ''

        self.path = path
        self.params = params
        self.query = query
        self.fragment = fragment

    def __contains__(self, other):
        if not isinstance(other, RepositoryURL):
            return NotImplemented

        return (self.scheme = other.scheme
            and self.netloc = other.netloc
            and other.path.startswith(self.path)
        )

    @property
    def needs_auth(self):
        return bool(self.with_auth or self.username or self.password)

    @property
    def base_url(self):
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
        if self.with_auth:
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
    def __init__(self, name):
        self.name = name
        self.url = None
        self.username = ''
        self.password = ''

    def fill(self, config, section):
        if config.has_section(section):
            self.url = RepositoryURL(config.get(section, 'repository', ''))
            self.username = config.get(section, 'username', '')
            self.password = config.get(section, 'password', '')

    def prompt_auth(self):
        if self.username and self.password:
            return
        sys.stdout.write("Please insert your credentials for %s\n" % self.repo_url)
        while not self.username:
            self.username = raw_input("Username [%s]: " % getpass.getuser())

        while not self.password:
            self.password = getpass.getpass("Password: ")

    @property
    def needs_auth(self):
        return self.username or self.password or self.url.needs_auth

    def get_clean_url(self):
        if self.needs_auth:
            self.prompt_auth()
        url = RepositoryURL(self.url.full_url)
        url.username = self.username
        url.password = self.password
        return url


class PyPIConfig(object):
    def __init__(self, path):
        self.path = path
        self.repositories = []

    def _read_config(self):
        config = ConfigParser.ConfigParser(self.path)
        if config.has_section('distutils'):
            servers = [server.strip() for server in config.get('distutils', 'index-servers', '')]
            servers = [server for server in servers if server]

            for server in servers:
                repo_config = RepositoryConfig(server)
                repo_config.fill(config, server)
                self.repositories.append(repo_config)

        repo_config = RepositoryConfig('default')
        repo_config.fill(config, 'server-login')

    def get_repo_config(self, repo='default'):
        for repo_config in self.repositories():
            if repo_config.name == repo or repo_config.url in RepositoryURL(repo):
                return repo_config
