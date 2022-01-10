from typing import Optional

class DockerScripts:
    def __init__(self, dockerdir: Optional[str] =None) -> None: ...
    def create(self, dockerfile: Optional[str] =None) -> str: ...
class DockerDir:
    def __init__(self, topdir: str =".") -> None: ...
    def run(self, dockerfile: Optional[str]=None, targetdir: Optional[str]=None) -> int: ...
    def create(self, dockerfile: Optional[str]=None, targetdir: Optional[str]=None) -> str: ...
def run(dockerfile: Optional[str], targetdir : Optional[str], build: bool =False) -> int: ...
