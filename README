restricted_pkg
==============

This python package provide a simple wrapper around `Distribute <http://packages.python.org/distribute/>`_ to handle
private projects.
It is mostly intended for use in a package's ``setup.py`` script.

It provides the following features:

- Using a private package index when fetching package dependencies during ``python setup.py install``
- Restricting the ``register`` and ``upload`` commands to a private package index, or to disable them completely
- Easy support for authenticated URLs when accessing the index.


Compatibility
-------------

The ``restricted_pkg`` package requires Distribute, and supports Python 2.6 and later (including Python3).


Usage
-----

In your ``setup.py`` script, ensure you have the following lines::

    from setuptools import find_packages
    from restricted_pkg import setup

    setup(
        ...,
        private_repository="https://@myrepo.example.tld/path/to/repo",
        install_requires=[
            "distribute",
            "restricted_pkg",
        ],
    )

.. vim: ft=rst
