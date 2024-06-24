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
try:
    from urllib.parse import urlparse
except:  # py2
    from urlparse import urlparse  # type: ignore

PORT = 80
SSL = ""
URL = "http://mirrorlist.centos.org"

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

DEFAULT_REL1 = "9"
DEFAULT_ARCH = "x86_64"
DEFAULT_REPO = "os"

if opt.data and opt.data != ".":
    os.chdir(opt.data)

class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/?") or self.path.startswith("/mirrorlist?") or self.path.startswith("/mirrorlist/?"):
            mirrorlist, parameters = self.path.split("?", 1)
            values = {}
            for param in parameters.split("&"):
                if "=" in param:
                    name, value = param.split("=")
                    values[name] = value
            release = values.get("release", "") or DEFAULT_REL1
            arch = values.get("arch", "") or DEFAULT_ARCH
            repo = values.get("repo", "") or DEFAULT_REPO
            infra = values.get("infra", "")
            if infra in ["container"]:
                infra = "os"
            if release in ["8", "9"]:
                text = "%s/%s/%s/%s/%s/\n" % (SSL or URL, release, repo, arch, infra)
            else:
                text = "%s/%s/%s/%s/\n" % (SSL or URL, release, repo, arch)
            print("SERVE", self.path)
            print("   AS", text.strip())
            data = text.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        if self.path.startswith("/mirrorlist/"):
            if "?" in self.path:
                mirrorlist, parameters = self.path.split("?", 1)
            else:
                mirrorlist, parameters = self.path, ""
            parts = mirrorlist.split("/")
            if parts[1] == "mirrorlist":
                parts = parts[1:]
            mirrorlist = parts[0]
            if len(parts) >= 2:
                release = parts[1] or DEFAULT_REL1
            else:
                release = DEFAULT_REL1
            if len(parts) >= 3:
                repo = parts[2] or DEFAULT_REPO
            else:
                repo = DEFAULT_REPO
            mapped = {"appstream": "AppStream", "baseos": "BaseOS", "crb": "CRB"}
            if repo in mapped:
                repo = mapped[repo]
            arch = "$basearch"  # generic :)
            infra = "os"  # almalinux does not care
            text = "%s/%s/%s/%s/%s/\n" % (SSL or URL, release, repo, arch, infra)
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

server = urlparse(SSL or URL)

if not SSL:
    httpd = TCPServer(("", opt.port), MyHandler)
    print("serving at port", opt.port)
    httpd.serve_forever()
else:
    port = server.port
    if not port:
        port = int(opt.port)
        if port < 100: port = 443
    import ssl
    import subprocess
    hostname = server.hostname
    if not hostname:
        hostname = "localhost"
    cc = hostname.split(".")[-1]
    og = hostname.split(".")[-2]
    if len(cc) > 2: cc = "US"
    cmd = "openssl req -x509 -newkey rsa:4096 -sha256 -days 3650 -nodes"
    cmd += " -keyout /tmp/{hostname}.key -out /tmp/{hostname}.crt -subj /C={cc}/L={og}/CN={hostname}".format(**locals())
    print(cmd)
    subprocess.call(cmd, shell=True)
    cmd = "cat /tmp/{hostname}.key /tmp/{hostname}.crt > /tmp/{hostname}.pem".format(**locals())
    subprocess.call(cmd, shell=True)
    httpd = TCPServer(("", port), MyHandler)
    httpd.socket = ssl.wrap_socket(httpd.socket, certfile='/tmp/%s.pem' % hostname, server_side=True)
    print("serving at port", port, "for", SSL)
    httpd.serve_forever()
