#! /usr/bin/python

from __future__ import print_function

__copyright__ = "(C) 2018-2020 Guido Draheim"
__contact__ = "https://github.com/gdraheim/docker-mirror-packages-repo"
__license__ = "CC0 Creative Commons Zero (Public Domain)"
__version__ = "1.6.2501"

import optparse
import os

try:
    from http.server import SimpleHTTPRequestHandler
except: #py2
    from SimpleHTTPServer import SimpleHTTPRequestHandler # type: ignore
try:
    from socketserver import TCPServer
except: #py2
    from SocketServer import TCPServer # type: ignore

PORT = 80
URL="http://mirrorlist.centos.org"

ext = optparse.OptionParser("%prog [options]")
ext.add_option("-d", "--data", default=".",
    help="change to data directory before")
ext.add_option("-p", "--port", default=PORT,
    help="serve on that port for http")
ext.add_option("-u", "--url", default=URL,
    help="url prefix (%default)")

opt, args = ext.parse_args()
URL = opt.url

if opt.data and opt.data != ".":
    os.chdir(opt.data)

class MyHandler(SimpleHTTPRequestHandler):
  def do_GET(self):
    if self.path.startswith("/?"):
       values = {}
       for param in self.path[2:].split("&"):
          if "=" in param:
              name, value = param.split("=")
              values[name] = value
       release = values.get("release", "0")
       arch = values.get("arch","x86_64")
       repo = values.get("repo", "os")
       infra = values.get("infra", "")
       if infra in ["container"]:
           infra = "os"
       if release in ["8"]:
           text = "%s/%s/%s/%s/%s/\n" % (URL, release, repo, arch, infra)
       else:
           text = "%s/%s/%s/%s/\n" % (URL, release, repo, arch)
       print("SERVE", self.path)
       print("   AS", text.strip())
       data = text.encode("utf-8")
       self.send_response(200)
       self.send_header("Content-Type", "text/plain")
       self.send_header("Content-Length", str(len(data)))
       self.end_headers()
       self.wfile.write(data)
       return
    print("CHECK", self.path)
    return SimpleHTTPRequestHandler.do_GET(self)

httpd = TCPServer(("", opt.port), MyHandler)

print("serving at port", opt.port)
httpd.serve_forever()
