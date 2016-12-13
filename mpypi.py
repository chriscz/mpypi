#!/usr/bin/python
"""
An extensible private pypi index.

NOTES ON PACKAGE NAMES
----------------------
MPyPi tries the following when it does not find a package 
with the given name in the index:
    - replaces all _ with - and
    - lowercases the package name
"""
from __future__ import print_function
import sys
import os
import cgi
import re

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from subprocess import Popen, PIPE

from contextlib import contextmanager
from collections import namedtuple

__version__ = "0.0.2"

# --- format strings
ENTRY_FMT = """<a href="{url}">{name}</a><br/>\n"""
PAGE_FMT = """<html><head><title>Simple MPyPi Index</title><meta name="api-version" value="2" /></head><body>\n"""
PKG_PAGE_FMT = """<!DOCTYPE html><html><head><title>Links for {name}</title></head><body><h1>Links for {name}</h1>\n"""

RunResult = namedtuple('RunResult', ['returncode', 'stdout', 'stderr'])

class PackageBase(object):
    """
    Base class used by all package implementations
    """

    """unique name string."""
    name = None
    def links(self): 
        """
        Return an interable of (name, url) pairs
        """
        raise NotImplementedError()

class URLPackage(PackageBase):
    """
    Implementation of a simple name --> links package mapping

    NOTES
    -----
        - #egg= will be added to all urls that start git/svn etc a git+, if
          it is NOT already present
    """
    EGG_FMT = "#egg={}"

    p_egg = re.compile("#egg=")
    # add #egg to urls that start on something like git+ or svn+
    p_starts = re.compile('^\w+\+')

    def __init__(self, name, links):
        """
        Arguments
        ---------
        name: str
            name of this package

        links: iterable of 2-tuples
            tuples are of the form (name: str, url: str)
        """
        self.name = name
        self.links = list(links)

        # update URLS using #egg={} 
        for i in xrange(len(links)):
            name, url = self.links[i]
            if self.p_starts.match(url) and not self.p_egg.find(url):
                url += self.EGG_FMT.format(name)
                self.links[i] = (name, url)


@contextmanager
def cd(directory):
    """
    Context manager that changes the working directory in the given context.

    Example
    -------

    with cd('/home/'):
        # do some stuff
    """
    old = os.getcwd()
    try:
        os.chdir(directory)
        yield
    finally:
        os.chdir(old)

def run(*args, **kwargs):
    """
    Runs a command on the underlying system. 

    Optional Keyword Arguments
    --------------------------
    input: string
        passed to the Popen.communicate call as input

    timeout: millisecond float
        specifies how long to wait before terminating the given command  
    """
    _patch_popen(Popen)
    assert len(args) > 0

    arguments = []

    input = kwargs.pop('input', None)

    if len(args) == 1:
        if isinstance(args[0], basestring):
            arguments = args[0].split()
    else:
        for i in args:
            if isinstance(i, (list, tuple)):
                for j in i:
                    arguments.append(j)
            else:
                arguments.append(i)

    def set_default_kwarg(key, default):    
        kwargs[key] = kwargs.get(key, default)

    set_default_kwarg('stdin', PIPE)
    set_default_kwarg('stdout', PIPE)
    set_default_kwarg('stderr', PIPE)


    proc = Popen(arguments, **kwargs)
    stdout, stderr = proc.communicate(input)

    return RunResult(proc.returncode, stdout, stderr)

# ------------------------------------------------------------------------------ 
# INTERNALLY USED FUNCTIONS
# ------------------------------------------------------------------------------ 
# --- page formatting functions
def page_index(packages):
    yield PAGE_FMT
    for p in packages:
        name = p.name
        url = name
        yield ENTRY_FMT.format(url=p.name, name=name)

def page_package(package):
    yield PKG_PAGE_FMT.format(name=package.name)
    for (name, link) in package.links:
        yield ENTRY_FMT.format(name=name, url=link)

def msg_404(pkg_name):
    return '<html><body> Package <b>{}</b> does not exist.</body></html>\n'.format(cgi.escape(pkg_name))



# --- private functions
def _patch_popen(Popen):
    """
    Patches Popen.communicate to take a timeout option that allows a process to
    be timed out. The timeput is a millisecond float
    """
    if hasattr(Popen.communicate, 'patched'):
        return

    from threading import Timer
    _communicate = Popen.communicate

    def communicate(self, *args, **kwargs):
        timeout = kwargs.pop('timeout', None)

        if timeout is not None:
            timeout /= 1000.0
            timer = Timer(timeout, self.kill)
            try:
                timer.start()
                return _communicate(self, *args, **kwargs)
            finally:
                timer.cancel()
        else:
            return _communicate(self, *args, **kwargs)

    Popen.communicate = communicate
    communicate.patched = True

def make_request_handler(index):
    """
    
    Arguments
    ---------
        index: dict-like
            - allows key lookups
            - has a values() function that returns a list of 
              package instances.
            - supports get
    """
    root_paths = {'', '/'}

    class PyPiRequestHandler(BaseHTTPRequestHandler):

        def get_package(self, package_name):
            package = index.get(package_name)
            if not package:
                package = index.get(package_name.lower().replace('_', '-'))
            return package

        def do_GET(self):
            print(self.path)
            if self.path in root_paths:
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()

                # serve index page
                for line in page_index(index.values()):
                    self.wfile.write(line)
            else:
                # follow pip standard of using lowercase names
                package_name = self.path.strip('/')
                print(package_name)
                package = self.get_package(package_name)   
                
                if not package:
                    self.send_response(404)
                    self.send_header('Content-type','text/html')
                    self.end_headers()
                    self.wfile.write(msg_404(package_name))
                    return
                # serve package page
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                
                # serve index page
                for line in page_package(package):
                    self.wfile.write(line)

    return PyPiRequestHandler 

def main(packages, index=None, host='', port=7890):
    # optionally create an index
    if index is None:
        index = {}
        for p in packages:
            index[p.name.lower()] = p
    try:
        server = HTTPServer((host, port), make_request_handler(index))
        print('Started mpypi on port {}'.format(port))
        server.serve_forever()
    except KeyboardInterrupt:
        print('^C received, shutting down the web server')
        server.socket.close()

if __name__ == '__main__':
    main([])
