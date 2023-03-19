#! /usr/bin/python3
from typing import Optional, Union, Tuple, Dict, List

def decodes(text: Optional[str]) -> Optional[str]: ...
def decodes_(text: Union[str,bytes]) -> str: ...
def output3(cmd: Union[str, List[str]], shell: bool = True, debug: bool = True) -> Tuple[str, str, int]: ...
def major(version: str) -> str: ...
def onlyversion(image: str) -> str: ...

class DockerMirror:
    def __init__(self, cname: str, image: str, hosts: List[str]) -> None: ...

class DockerMirrorPackagesRepo:
    def __init__(self, image: Optional[str] = None) -> None:
        self._image: Optional[str]
    def host_system_image(self) -> str: ...
    def detect_etc_image(self, etc: str) -> Tuple[str, str]: ...
    def detect_base_image(self, image: str) -> str: ...
    def detect_base_image_from(self, cname: str, tempdir: str) -> Tuple[str, str]: ...
    def get_docker_latest_image(self, image: str) -> str: ...
    def get_docker_latest_version(self, image: str) -> str: ...
    def get_docker_mirror(self, image: str) -> Optional[DockerMirror]: ...
    def get_docker_mirrors(self, image: str) -> List[DockerMirror]:
        mirrors: List[DockerMirror]
    def get_ubuntu_latest(self, image: str, default: Optional[str] = None) -> str: ...
    def get_ubuntu_latest_version(self, version: str) -> str: ...
    def get_ubuntu_docker_mirror(self, image: str) -> DockerMirror: ...
    def get_ubuntu_docker_mirrors(self, image: str) -> List[DockerMirror]: ...
    def get_centos_latest(self, image: str, default: Optional[str] = None) -> str: ...
    def get_centos_latest_version(self, version: str) -> str: ...
    def get_centos_docker_mirror(self, image: str) -> DockerMirror: ...
    def get_centos_docker_mirrors(self, image: str) -> List[DockerMirror]: ...
    def get_opensuse_latest(self, image: str, default: Optional[str] = None) -> str: ...
    def get_opensuse_latest_version(self, version: str) -> str: ...
    def get_opensuse_docker_mirror(self, image: str) -> DockerMirror: ...
    def get_opensuse_docker_mirrors(self, image: str) -> List[DockerMirror]: ...
    def docker_mirror(self, rmi: str, rep: str, ver: str, *hosts: str) -> DockerMirror: ...
    def get_extra_mirrors(self, image: str) -> List[DockerMirror]:
        mirrors: List[DockerMirror]
    def get_epel_docker_mirrors(self, image: str) -> List[DockerMirror]: ...
    def get_epel_docker_mirror(self, image: str) -> DockerMirror: ...
    def ip_container(self, name: str) -> Optional[str]: ...
    def start_containers(self, image: str) -> Dict[str, Optional[str]]:
        done: Dict[str, Optional[str]]
    def start_container(self, image: str, container: str) -> Optional[str]: ...
    def stop_containers(self, image: str) -> Dict[str, str]:
        done: Dict[str, str]
    def stop_container(self, image: str, container: str) -> str: ...
    def info_containers(self, image: str) -> Dict[str, Optional[str]]: ...
    def info_container(self, image: str, container: str) -> Optional[str]: ...
    def get_containers(self, image: str) -> List[str]: ...
    def inspect_containers(self, image: str) -> Dict[str, Optional[str]]:
        done: Dict[str, Optional[str]]
    def add_hosts(self, image: str, done: Dict[str, Optional[str]] = {}) -> List[str]:
        args: List[str]
    def helps(self) -> str: ...
    def detect(self, image: Optional[str] = None) -> str: ...
    def epel(self, image: Optional[str] = None) -> str: ...
    def repo(self, image: Optional[str] = None) -> str: ...
    def repos(self, image: Optional[str] = None) -> str: ...
    def facts(self, image: Optional[str] = None) -> str: ...
    def starts(self, image: Optional[str] = None) -> str: ...
    def stops(self, image: Optional[str] = None) -> str: ...
    def wait_mirrors(self, hosts: Dict[str, Optional[str]]) -> bool: ...
    def infos(self, image: Optional[str] = None) -> str: ...
    def containers(self, image: Optional[str] = None) -> str: ...
    def inspects(self, image: Optional[str] = None) -> str: ...
    def from_dockerfile(self, dockerfile: str, defaults: Optional[str] = None) -> Optional[str]: ...

def repo_scripts() -> str: ...
