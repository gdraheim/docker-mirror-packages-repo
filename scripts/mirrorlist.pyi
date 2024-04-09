#! /usr/bin/python3
from http.server import SimpleHTTPRequestHandler

class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self) -> None: ...
