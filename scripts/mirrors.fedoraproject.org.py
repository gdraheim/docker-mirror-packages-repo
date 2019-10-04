#! /usr/bin/python

import SimpleHTTPServer
import SocketServer
import optparse
import os

URL="https://mirrors.fedoraproject.org"
SSL=""
PORT=80

ext = optparse.OptionParser("%prog [options]")
ext.add_option("-d", "--data", default=".",
    help="change to data directory before")
ext.add_option("-p", "--port", default=PORT,
    help="serve on that port for http")
ext.add_option("-u", "--url", default=URL,
    help="url prefix (%default)")
ext.add_option("-s", "--ssl", default=SSL,
    help="ssl server (%default)")

opt, args = ext.parse_args()
URL = opt.url
SSL = opt.ssl

if opt.data and opt.data != ".":
    os.chdir(opt.data)

Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
class MyHandler(Handler):
  def do_GET(self):
    if self.path.startswith("/metalink?"):
       values = {}
       for param in self.path[self.path.find("?")+1:].split("&"):
          if "=" in param:
              name, value = param.split("=")
              values[name] = value
       release = values.get("release", "0")
       arch = values.get("arch","x86_64")
       repo = values.get("repo", "os")
       infra = values.get("infra", "")
       if infra in ["container"]:
           infra = "os"
       if repo in ["epel-7"]:
           text = "%s/%s/%s/\n" % (URL, "7", arch)
       else:
           text = "%s/%s/%s/\n" % (URL, repo, arch)
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

import urlparse
server = urlparse.urlparse(SSL or URL)

if not SSL:
    httpd = SocketServer.TCPServer(("", opt.port), MyHandler)
    print "serving at port", opt.port
    httpd.serve_forever()
else:
    port = server.port
    if not port:
        port = int(opt.port)
        if port < 100: port = 443
    import ssl
    import subprocess
    hostname = server.hostname
    cc = hostname.split(".")[-1]
    og = hostname.split(".")[-2]
    if len(cc) > 2: cc = "US"
    cmd = "openssl req -x509 -newkey rsa:4096 -sha256 -days 3650 -nodes"
    cmd += " -keyout /tmp/{hostname}.key -out /tmp/{hostname}.crt -subj /C={cc}/L={og}/CN={hostname}".format(**locals())
    print cmd
    subprocess.call(cmd, shell=True)
    cmd = "cat /tmp/{hostname}.key /tmp/{hostname}.crt > /tmp/{hostname}.pem".format(**locals())
    subprocess.call(cmd, shell=True)
    httpd = SocketServer.TCPServer(("", port), MyHandler)
    httpd.socket = ssl.wrap_socket(httpd.socket, certfile='/tmp/%s.pem' % hostname, server_side=True)
    print "serving at port", port, "for", SSL
    httpd.serve_forever()
