#! /usr/bin/python3

from http.server import SimpleHTTPRequestHandler

class MyHandler(SimpleHTTPRequestHandler): # type: ignore[return]
    def do_GET(self) -> None: ...
