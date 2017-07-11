import SimpleHTTPServer
import SocketServer
import optparse
import os

PORT = 80

ext = optparse.OptionParser("%prog [options]")
ext.add_option("-d", "--data", default=".",
    help="change to data directory before")
ext.add_option("-p", "--port", default=PORT,
    help="serve on that port for http")

opt, args = ext.parse_args()

if opt.data and opt.data != ".":
    os.chdir(opt.data)

Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
class MyHandler(Handler):
  def do_GET(self):
    if self.path.startswith("/?"):
       values = {}
       for param in self.path[2:].split("&"):
          name, value = param.split("=")
          values[name] = value
       release = values.get("release", "0")
       arch = values.get("arch","x86_64")
       repo = values.get("repo", "os")
       text = "http://mirrorlist.centos.org/%s/%s/%s/\n" % (release, repo, arch)
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
