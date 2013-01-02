# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Raphaël Barrois.
# Distributed under the MIT License.


"""Hooks for distribute extra setup_keywords validation."""


from distutils.errors import DistutilsSetupError


def validate_private_repo(distribution, attr, value):
    if not value:
        raise DistutilsSetupError("The %s value cannot be empty." % attr)
