#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="conda-workspace",
    description="tools for building conda packages",
    scripts=[
        'bin/conda-workspace',
        'bin/wsgui',
        'bin/activatews',
    ],
    packages = ['conda_workspace'],
    install_requires=['conda'],
)
