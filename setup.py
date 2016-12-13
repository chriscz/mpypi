from __future__ import with_statement

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import mpypi

long_description = ""

setup(name="mpypi",
      version=mpypi.__version__,
      author="Chris Coetzee",
      author_email="chriscz93@gmail.com",
      url="",
      py_modules=["mpypi"],
      description="Extensible private pypi index",
      long_description=long_description,
      license="Apache License 2.0",
)
