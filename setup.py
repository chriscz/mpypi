from __future__ import with_statement
from setuptools import setup, find_packages

import mpypi

long_description = ""

setup(
    name="mpypi",
    version=mpypi.__version__,
    author="Chris Coetzee",
    author_email="chriscz93@gmail.com",
    url="https://github.com/chriscz/mpypi",
    packages=find_packages(),
    #py_modules=["mpypi"]
    description="Extensible private pypi index",
    long_description=long_description,
    license="Apache License 2.0",
    extras_require=dict(
        bitbucket=['pybitbucket']
    )
)
