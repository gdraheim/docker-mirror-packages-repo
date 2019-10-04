#! /usr/bin/python

import SimpleHTTPServer
import SocketServer
import optparse
import os

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

Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
class MyHandler(Handler):
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
       print "SERVE", self.path
       print "   AS", text.strip()
       self.send_response(200)
       self.send_header("Content-Type", "text/plain")
       self.send_header("Content-Length", len(text))
       self.end_headers()
       self.wfile.write(text)
       return
    print "CHECK", self.path
    return Handler.do_GET(self)

httpd = SocketServer.TCPServer(("", opt.port), MyHandler)

print "serving at port", opt.port
httpd.serve_forever()
