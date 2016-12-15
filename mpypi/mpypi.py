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
from __future__ import unicode_literals
import cgi

from .util import PY2, PY3

if PY2:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
else:
    from http.server import BaseHTTPRequestHandler, HTTPServer

# --- format strings
ENTRY_FMT = """<a href="{url}">{name}</a><br/>\n"""
PAGE_FMT = """<html><head><title>Simple MPyPi Index</title><meta name="api-version" value="2" /></head><body>\n"""
PKG_PAGE_FMT = """<!DOCTYPE html><html><head><title>Links for {name}</title></head><body><h1>Links for {name}</h1>\n"""


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

        def write_unicode(self, text):
            self.wfile.write(bytearray(text, encoding='utf-8'))

        def do_GET(self):
            print(self.path)
            if self.path in root_paths:
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()

                # serve index page
                for line in page_index(index.values()):
                    self.write_unicode(line)
            else:
                # follow pip standard of using lowercase names
                package_name = self.path.strip('/')
                print(package_name)
                package = self.get_package(package_name)

                if not package:
                    self.send_response(404)
                    self.send_header('Content-type','text/html')
                    self.end_headers()
                    self.write_unicode(msg_404(package_name))
                    return
                # serve package page
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()

                # serve index page
                for line in page_package(package):
                    self.write_unicode(line)

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
