#!/usr/bin/env python
# coding: utf-8

from setuptools import find_packages
from restricted_pkg import setup
import os
import re

root_dir = os.path.abspath(os.path.dirname(__file__))


def get_version(package_name):
    version_re = re.compile(r"^__version__ = [\"']([\w_.-]+)[\"']$")
    package_components = package_name.split('.')
    path_components = package_components + ['__init__.py']
    with open(os.path.join(root_dir, *path_components)) as f:
        for line in f:
            match = version_re.match(line[:-1])
            if match:
                return match.groups()[0]
    return '0.1.0'


PACKAGE = 'example'


setup(
    name="example_restricted_pkg",
    private_repository="https://@pypi.private.example.com/",
    version=get_version(PACKAGE),
    author="Raphaël Barrois",
    author_email="raphael.barrois@polytechnique.org",
    description="A simple example of a private package",
    license="Public domain",
    keywords=['pypi', 'private', 'repository'],
    url="http://github.com/rbarrois/restricted_pkg",
    download_url="http://pypi.python.org/pypi/restricted_pkg/",
    packages=find_packages(),
    install_requires=[
        'distribute',
        'restricted_pkg',
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: Public Domain",
        "Topic :: Software Development :: Libraries :: Python Modules",
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
