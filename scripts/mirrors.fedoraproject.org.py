#! /usr/bin/python3

from __future__ import print_function

__copyright__ = "(C) 2018-2024 Guido Draheim"
__contact__ = "https://github.com/gdraheim/docker-mirror-packages-repo"
__license__ = "CC0 Creative Commons Zero (Public Domain)"
__version__ = "1.7.6261"

import optparse
import os
import os.path
import re
import time
import hashlib

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


URL = "http://mirrors.fedoraproject.org"
SSL = ""
PORT = 80

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

def boot_time():
    return int(open('/proc/stat').read().split('btime ')[1].split()[0])
def os_path_md5(path):
    m = hashlib.md5()
    m.update(open(path, "rb").read())
    return m.hexdigest()
def os_path_sha256(path):
    m = hashlib.sha256()
    m.update(open(path, "rb").read())
    return m.hexdigest()
def os_path_sha512(path):
    m = hashlib.sha512()
    m.update(open(path, "rb").read())
    return m.hexdigest()
def fix_mtime_repomd_xml(path):
    timestamp = 0
    for line in open(path):
        m = re.match(".*<timestamp>(\\d+)</timestamp>.*", line)
        if m:
            ts = int(m.group(1))
            if ts > timestamp:
                timestamp = ts
    if timestamp:
        now = time.time()
        old = os.path.getmtime(path)
        if int(old) != int(timestamp):
            print("FIXED", path, timestamp, "(old", old, ")")
            os.utime(path, (now, timestamp))

if opt.data and opt.data != ".":
    os.chdir(opt.data)

class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/metalink?"):
            metalink = True  # epel/fedora format as long as we know
            values = {}
            for param in self.path[self.path.find("?") + 1:].split("&"):
                if "=" in param:
                    name, value = param.split("=")
                    values[name] = value
            release = values.get("release", "0")
            arch = values.get("arch", "x86_64")
            repo = values.get("repo", "os")
            infra = values.get("infra", "")
            if infra in ["container"]:
                infra = "os"
            if repo in ["epel-7"]:
                use = "%s/%s/" % ("7", arch)
            elif repo in ["epel-8"]:
                use = "%s/%s/" % ("8/Everything", arch)
            elif repo in ["epel-modular-8"]:
                use = "%s/%s/" % ("8/Modular", arch)
            elif repo in ["epel-9"]:
                use = "%s/%s/" % ("9/Everything", arch)
            else:
                use = "%s/%s/" % (repo, arch)
            url = "%s/%s" % (SSL or URL, use)
            print("SERVE", self.path)
            print("   AS", url)
            if metalink:
                repomd_xml = use.rstrip("/") + "/repodata/repomd.xml"
                repomd_url = url.rstrip("/") + "/repodata/repomd.xml"
                if not os.path.exists(repomd_xml):
                    text = "did not find " + repomd_xml
                    data = text.encode("utf-8")
                    self.send_response(404)
                    self.send_header("Content-Type", "text/plain")
                    self.send_header("Content-Length", str(len(data)))
                    self.send_header("X-Filepath", repomd_xml)
                    self.end_headers()
                    self.wfile.write(data)
                    return
                fix_mtime_repomd_xml(repomd_xml)
                generator = "http://github/gdraheim/docker-mirror-packages-repo"
                ns = "http://www.metalinker.org/"
                mm = "http://fedorahosted.org/mirrormanager"
                ts = int(os.path.getmtime(repomd_xml))
                sz = os.path.getsize(repomd_xml)
                md5 = os_path_md5(repomd_xml)
                sha256 = os_path_sha256(repomd_xml)
                sha512 = os_path_sha512(repomd_xml)
                http = url.split(":")[0]
                xml = """<?xml version="1.0" encoding="utf-8"?>
             <metalink version="3.0" xmlns="{ns}" xmlns:mm="{mm}" generator="{generator}">
              <files>
               <file name="repomd.xml">
                <mm:timestamp>{ts}</mm:timestamp>
                <size>{sz}</size>
                <verification>
                  <hash type="md5">{md5}</hash>
                  <hash type="sha256">{sha256}</hash>
                  <hash type="sha512">{sha512}</hash>
                </verification>
                <resources maxconnections="1">
                 <url protocol="{http}" type="{http}" preference="100">{repomd_url}</url>
                </resources>
               </file>
              </files>
             </metalink>""".format(**locals())
                data = xml.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/metalink+xml")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            else:
                data = (url + "\r\n").encode("utf-8")
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
