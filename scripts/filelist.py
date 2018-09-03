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
    # nothing special to be done for just files
    if os.path.exists("./"+self.path):
        print "OK", self.path
    else:
        print "NO", self.path
    return Handler.do_GET(self)

httpd = SocketServer.TCPServer(("", opt.port), MyHandler)

print "serving at port", opt.port
httpd.serve_forever()
