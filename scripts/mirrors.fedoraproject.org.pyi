#! /usr/bin/python3

def boot_time() -> int: ...
def os_path_md5(path: str) -> str: ...
def os_path_sha256(path: str) -> str: ...
def os_path_sha512(path: str) -> str: ...
def fix_mtime_repomd_xml(path: str) -> None: ...

class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self) -> None: ...
