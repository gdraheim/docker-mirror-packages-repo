#! /usr/bin/python3

from __future__ import print_function

__copyright__ = "(C) 2018-2024 Guido Draheim"
__contact__ = "https://github.com/gdraheim/docker-mirror-packages-repo"
__license__ = "CC0 Creative Commons Zero (Public Domain)"
__version__ = "1.7.6261"

import optparse
import os

try:
    from http.server import SimpleHTTPRequestHandler
except:  # py2
    from SimpleHTTPServer import SimpleHTTPRequestHandler  # type: ignore
try:
    from socketserver import TCPServer
except:  # py2
    from SocketServer import TCPServer  # type: ignore

PORT = 80

ext = optparse.OptionParser("%prog [options]")
ext.add_option("-d", "--data", default=".",
               help="change to data directory before")
ext.add_option("-p", "--port", default=PORT,
               help="serve on that port for http")

opt, args = ext.parse_args()

if opt.data and opt.data != ".":
    os.chdir(opt.data)

class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # nothing special to be done for just files
        if os.path.exists("./" + self.path):
            print("OK", self.path)
        else:
            print("NO", self.path)
        return SimpleHTTPRequestHandler.do_GET(self)

httpd = TCPServer(("", opt.port), MyHandler)

print("serving at port", opt.port)
httpd.serve_forever()
