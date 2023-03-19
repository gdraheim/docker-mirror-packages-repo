#! /usr/bin/python3
"""
   You can just call tests by their number, or a common prefix thereof.
   (so that "./testsuite.py -v test_107" will run the tests from test_1070 to test_1079).
"""

__copyright__ = "(C) 2018-2023 Guido Draheim"
__contact__ = "https://github.com/gdraheim/docker-mirror-packages-repo"
__license__ = "CC0 Creative Commons Zero (Public Domain)"
__version__ = "1.7.5116"

from typing import Union, Optional, List, cast
import sys
import subprocess
import collections
import json
import os.path
import unittest
from fnmatch import fnmatchcase as fnmatch

import logging
logg = logging.getLogger("TESTSUITE")

string_types = str
xrange = range

KEEP = False
PREFIX = "localhost:5000/mirror-packages"
DOCKER = "docker"
DOCKER_SOCKET = "/var/run/docker.sock"
MR143 = True  # modify repos of opensuse/leap:14.3
MR151 = True  # modify repos of opensuse/leap:15.1

_docker_mirror = "./docker_mirror.py"

def decodes(text: Union[str, bytes]) -> str:
    if text is None: return None
    if isinstance(text, bytes):
        encoded = sys.getdefaultencoding()
        if encoded in ["ascii"]:
            encoded = "utf-8"
        try:
            return text.decode(encoded)
        except:
            return text.decode("latin-1")
    return text
def sh____(cmd: Union[str, List[str]], shell: bool = True) -> int:
    if isinstance(cmd, string_types):
        logg.debug(": %s", cmd)
    else:
        logg.debug(": %s", " ".join(["'%s'" % item for item in cmd]))
    return subprocess.check_call(cmd, shell=shell)
def sx____(cmd: Union[str, List[str]], shell: bool = True) -> int:
    if isinstance(cmd, string_types):
        logg.debug(": %s", cmd)
    else:
        logg.debug(": %s", " ".join(["'%s'" % item for item in cmd]))
    return subprocess.call(cmd, shell=shell)
def output(cmd: Union[str, List[str]], shell: bool = True) -> str:
    if isinstance(cmd, string_types):
        logg.debug(": %s", cmd)
    else:
        logg.debug(": %s", " ".join(["'%s'" % item for item in cmd]))
    run = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE)
    out, err = run.communicate()
    return decodes(out)

_subprocess = collections.namedtuple("_subprocess", ["out", "err", "rc"])
def runs(cmd: Union[str, List[str]], shell: bool = True) -> _subprocess:
    if isinstance(cmd, string_types):
        logg.debug(": %s", cmd)
    else:
        logg.debug(": %s", " ".join(["'%s'" % item for item in cmd]))
    run = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = run.communicate()
    return _subprocess(decodes(out), decodes(err), run.returncode)
    # return _subprocess(decodes(out.read()), decodes(err.read()), run.returncode)

def ip_container(name: str) -> Optional[str]:
    docker = DOCKER
    cmd = "{docker} inspect {name}"
    proc = runs(cmd.format(**locals()))
    if proc.rc:
        logg.debug("%s not found: rc=%i\n\t%s", name, proc.rc, proc.err)
        return None
    values = json.loads(proc.out)
    if not values or "NetworkSettings" not in values[0]:
        cmd_run = cmd.format(**locals())
        logg.critical(" %s => %s ", cmd, values)
    return cast(str, values[0]["NetworkSettings"]["IPAddress"])
def image_exist(name: str) -> Optional[str]:
    return image_exists("", name)
def image_exists(prefix: Optional[str], name: str) -> Optional[str]:
    docker = DOCKER
    name = name.strip()
    if prefix:
        proc = runs("{docker} inspect {prefix}/{name}".format(**locals()))
    else:
        proc = runs("{docker} inspect {name}".format(**locals()))
    if proc.rc:
        logg.debug("%s not found: rc=%i\n\t%s", name, proc.rc, proc.err)
        return ""
    values = json.loads(proc.out)
    if not values or "Container" not in values[0]:
        return None
    return cast(str, values[0]["Container"])
def make_file(name: str, content: str) -> None:
    with open(name, "w") as f:
        f.write(content)
def drop_file(name: str) -> None:
    if os.path.exists(name):
        os.remove(name)


class DockerMirrorPackagesTest(unittest.TestCase):
    def test_00001_hello(self) -> None:
        print("... starting the testsuite ...")
        logg.info("starting the testsuite ...")
    def test_10073_centos(self) -> None:
        prefix = PREFIX
        docker = DOCKER
        repo_image = "centos-repo:7.3.1611"
        box1_image = "centos:7.3.1611"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
        sh____("{docker} run -d --name test-repo {prefix}/{repo_image}".format(**locals()))
        mirror_ip = ip_container("test-repo")
        add_host = "--add-host mirrorlist.centos.org:{mirror_ip}".format(**locals())
        sh____("{docker} run -d --name test-box1 {add_host} {box1_image} sleep 600".format(**locals()))
        sh____("{docker} exec test-box1 yum install -y python-docker-py".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
    def test_10074_centos(self) -> None:
        prefix = PREFIX
        docker = DOCKER
        repo_image = "centos-repo:7.4.1708"
        box1_image = "centos:7.4.1708"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
        sh____("{docker} run -d --name test-repo {prefix}/{repo_image}".format(**locals()))
        mirror_ip = ip_container("test-repo")
        add_host = "--add-host mirrorlist.centos.org:{mirror_ip}".format(**locals())
        sh____("{docker} run -d --name test-box1 {add_host} {box1_image} sleep 600".format(**locals()))
        sh____("{docker} exec test-box1 yum install -y python-docker-py".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
    def test_10075_centos(self) -> None:
        prefix = PREFIX
        docker = DOCKER
        repo_image = "centos-repo:7.5.1804"
        box1_image = "centos:7.5.1804"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
        sh____("{docker} run -d --name test-repo {prefix}/{repo_image}".format(**locals()))
        mirror_ip = ip_container("test-repo")
        add_host = "--add-host mirrorlist.centos.org:{mirror_ip}".format(**locals())
        sh____("{docker} run -d --name test-box1 {add_host} {box1_image} sleep 600".format(**locals()))
        sh____("{docker} exec test-box1 yum install -y python-docker-py".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
    def test_10076_centos(self) -> None:
        prefix = PREFIX
        repo_image = "centos-repo:7.6.1810"
        box1_image = "centos:7.6.1810"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
        sh____("{docker} run -d --name test-repo {prefix}/{repo_image}".format(**locals()))
        mirror_ip = ip_container("test-repo")
        add_host = "--add-host mirrorlist.centos.org:{mirror_ip}".format(**locals())
        sh____("{docker} run -d --name test-box1 {add_host} {box1_image} sleep 600".format(**locals()))
        sh____("{docker} exec test-box1 yum install -y python-docker-py".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
    def test_10077_centos(self) -> None:
        prefix = PREFIX
        docker = DOCKER
        repo_image = "centos-repo:7.7.1908"
        box1_image = "centos:7.7.1908"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
        sh____("{docker} run -d --name test-repo {prefix}/{repo_image}".format(**locals()))
        mirror_ip = ip_container("test-repo")
        add_host = "--add-host mirrorlist.centos.org:{mirror_ip}".format(**locals())
        sh____("{docker} run -d --name test-box1 {add_host} {box1_image} sleep 600".format(**locals()))
        sh____("{docker} exec test-box1 yum install -y python-docker-py".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
    def test_10079_centos(self) -> None:
        prefix = PREFIX
        docker = DOCKER
        repo_image = "centos-repo:7.9.2009"
        box1_image = "centos:7.9.2009"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
        sh____("{docker} run -d --name test-repo {prefix}/{repo_image}".format(**locals()))
        mirror_ip = ip_container("test-repo")
        add_host = "--add-host mirrorlist.centos.org:{mirror_ip}".format(**locals())
        sh____("{docker} run -d --name test-box1 {add_host} {box1_image} sleep 600".format(**locals()))
        sh____("{docker} exec test-box1 yum install -y python-docker-py".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
    def test_10080_centos(self) -> None:
        prefix = PREFIX
        docker = DOCKER
        repo_image = "centos-repo:8.0.1905"
        box1_image = "centos:8"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
        sh____("{docker} run -d --name test-repo {prefix}/{repo_image}".format(**locals()))
        mirror_ip = ip_container("test-repo")
        add_host = "--add-host mirrorlist.centos.org:{mirror_ip}".format(**locals())
        sh____("{docker} run -d --name test-box1 {add_host} {box1_image} sleep 600".format(**locals()))
        # sh____("{docker} exec test-box1 yum install -y python-docker-py") # all /extras are now in epel
        sh____("{docker} exec test-box1 yum install -y python2-numpy".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
    def test_10081_centos(self) -> None:
        prefix = PREFIX
        docker = DOCKER
        repo_image = "centos-repo:8.1.1911"
        box1_image = "centos:8.1.1911"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
        sh____("{docker} run -d --name test-repo {prefix}/{repo_image}".format(**locals()))
        mirror_ip = ip_container("test-repo")
        add_host = "--add-host mirrorlist.centos.org:{mirror_ip}".format(**locals())
        sh____("{docker} run -d --name test-box1 {add_host} {box1_image} sleep 600".format(**locals()))
        # sh____("{docker} exec test-box1 yum install -y python-docker-py") # all /extras are now in epel
        sh____("{docker} exec test-box1 yum install -y python2-numpy".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
    def test_10083_centos(self) -> None:
        prefix = PREFIX
        docker = DOCKER
        repo_image = "centos-repo:8.3.2011"
        box1_image = "centos:8.3.2011"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
        cmd = "{docker} run -d --name test-repo {prefix}/{repo_image}"
        logg.warning("%s", cmd.format(**locals()))
        sh____(cmd.format(**locals()))
        mirror_ip = ip_container("test-repo")
        add_host = "--add-host mirrorlist.centos.org:{mirror_ip}".format(**locals())
        cmd = "{docker} run -d --name test-box1 {add_host} {box1_image} sleep 600"
        logg.warning("%s", cmd.format(**locals()))
        sh____(cmd.format(**locals()))
        # sh____("{docker} exec test-box1 yum install -y python-docker-py") # all /extras are now in epel
        sh____("{docker} exec test-box1 yum install -y python2-numpy".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
    def test_10091_almalinux(self) -> None:
        prefix = PREFIX
        docker = DOCKER
        repo_image = "almalinux-repo:9.1"
        box1_image = "almalinux:9.1"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
        cmd = "{docker} run -d --name test-repo {prefix}/{repo_image}"
        logg.warning("%s", cmd.format(**locals()))
        sh____(cmd.format(**locals()))
        mirror_ip = ip_container("test-repo")
        add_host = "--add-host mirrors.almalinux.org:{mirror_ip}".format(**locals())
        cmd = "{docker} run -d --name test-box1 {add_host} {box1_image} sleep 600"
        logg.warning("%s", cmd.format(**locals()))
        sh____(cmd.format(**locals()))
        retry = "--connect-timeout 5 --retry 3 --retry-connrefused"
        sh____("{docker} exec test-box1 curl -k {retry} https://mirrors.almalinux.org".format(**locals()))
        sh____("{docker} exec test-box1 bash -c 'echo sslverify=false >>/etc/yum.conf'".format(**locals()))
        sh____("{docker} exec test-box1 yum install -y python3-numpy".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
    def test_14422_opensuse(self) -> None:
        prefix = PREFIX
        docker = DOCKER
        repo_image = "opensuse-repo:42.2"
        box1_image = "opensuse:42.2"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
        sh____("{docker} run -d --name test-repo {prefix}/{repo_image}".format(**locals()))
        mirror_ip = ip_container("test-repo")
        add_host = "--add-host download.opensuse.org:{mirror_ip}".format(**locals())
        sh____("{docker} run -d --name test-box1 {add_host} {box1_image} sleep 600".format(**locals()))
        sh____("{docker} exec test-box1 zypper install -y python-docker-py".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
    def test_14423_opensuse(self) -> None:
        prefix = PREFIX
        docker = DOCKER
        repo_image = "opensuse-repo:42.3"
        box1_image = "opensuse:42.3"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
        sh____("{docker} run -d --name test-repo {prefix}/{repo_image}".format(**locals()))
        mirror_ip = ip_container("test-repo")
        add_host = "--add-host download.opensuse.org:{mirror_ip}".format(**locals())
        sh____("{docker} run -d --name test-box1 {add_host} {box1_image} sleep 600".format(**locals()))
        if MR143:
            # "zypper refresh repo-oss repo-update"
            sh____("{docker} exec test-box1 zypper mr --no-gpgcheck oss-update".format(**locals()))
        sh____("{docker} exec test-box1 zypper install -y python-docker-py".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
    def test_14150_opensuse(self) -> None:
        prefix = PREFIX
        docker = DOCKER
        repo_image = "opensuse-repo:15.0"
        box1_image = "opensuse/leap:15.0"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
        sh____("{docker} run -d --name test-repo {prefix}/{repo_image}".format(**locals()))
        mirror_ip = ip_container("test-repo")
        add_host = "--add-host download.opensuse.org:{mirror_ip}".format(**locals())
        sh____("{docker} run -d --name test-box1 {box1_image} sleep 600".format(**locals()))
        sh____("{docker} exec test-box1 zypper install -y python-docker-py".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
    def test_14151_opensuse(self) -> None:
        prefix = PREFIX
        docker = DOCKER
        repo_image = "opensuse-repo:15.1"
        box1_image = "opensuse/leap:15.1"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
        sh____("{docker} run -d --name test-repo {prefix}/{repo_image}".format(**locals()))
        mirror_ip = ip_container("test-repo")
        add_host = "--add-host download.opensuse.org:{mirror_ip}".format(**locals())
        sh____("{docker} run -d --name test-box1 {add_host} {box1_image} sleep 600".format(**locals()))
        if MR151:
            # sh____("{docker} exec test-box1 zypper repos".format(**locals()))
            sh____("{docker} exec test-box1 zypper mr --no-gpgcheck repo-update".format(**locals()))
            sh____("{docker} exec test-box1 zypper rr repo-non-oss repo-update-non-oss".format(**locals()))
        sh____("{docker} exec test-box1 zypper install -y python python-xml".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
    def test_14152_opensuse(self) -> None:
        prefix = PREFIX
        docker = DOCKER
        repo_image = "opensuse-repo:15.2"
        box1_image = "opensuse/leap:15.2"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
        sh____("{docker} run -d --name test-repo {prefix}/{repo_image}".format(**locals()))
        mirror_ip = ip_container("test-repo")
        add_host = "--add-host download.opensuse.org:{mirror_ip}".format(**locals())
        sh____("{docker} run -d --name test-box1 {add_host} {box1_image} sleep 600".format(**locals()))
        # if MR152:
        #   sh____("{docker} exec test-box1 zypper mr --no-gpgcheck repo-update".format(**locals()))
        sh____("{docker} exec test-box1 zypper --no-gpg-checks install -y python-docker-py".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
    def test_14252_opensuse(self) -> None:
        prefix = PREFIX
        docker = DOCKER
        repo_image = "opensuse-repo:15.2"
        box1_image = "opensuse/leap:15.2"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
        sh____("{docker} run -d --name test-repo {prefix}/{repo_image}".format(**locals()))
        mirror_ip = ip_container("test-repo")
        add_host = "--add-host download.opensuse.org:{mirror_ip}".format(**locals())
        sh____("{docker} run -d --name test-box1 {add_host} {box1_image} sleep 600".format(**locals()))
        # if MR152:
        #   sh____("{docker} exec test-box1 zypper mr --no-gpgcheck repo-update".format(**locals()))
        sh____("{docker} exec test-box1 zypper --no-gpg-checks refresh".format(**locals()))
        sh____("{docker} exec test-box1 zypper --no-gpg-checks install -y python-docker-py".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
    def test_11404_ubuntu(self) -> None:
        prefix = PREFIX
        docker = DOCKER
        repo_image = "ubuntu-repo:14.04"
        box1_image = "ubuntu:14.04"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
        sh____("{docker} run -d --name test-repo {prefix}/{repo_image}".format(**locals()))
        mirror_ip = ip_container("test-repo")
        add_host = "--add-host archive.ubuntu.com:{mirror_ip} --add-host security.ubuntu.com:{mirror_ip}".format(**locals())
        sh____("{docker} run -d --name test-box1 {add_host} {box1_image} sleep 600".format(**locals()))
        sh____("{docker} exec test-box1 apt-get update".format(**locals()))
        # sh____("{docker} exec test-box1 apt-get install -y python-docker".format(**locals()))
        sh____("{docker} exec test-box1 apt-get install -y apache2".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
    def test_11604_ubuntu(self) -> None:
        prefix = PREFIX
        docker = DOCKER
        repo_image = "ubuntu-repo:16.04"
        box1_image = "ubuntu:16.04"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
        sh____("{docker} run -d --name test-repo {prefix}/{repo_image}".format(**locals()))
        mirror_ip = ip_container("test-repo")
        add_host = "--add-host archive.ubuntu.com:{mirror_ip} --add-host security.ubuntu.com:{mirror_ip}".format(**locals())
        sh____("{docker} run -d --name test-box1 {add_host} {box1_image} sleep 600".format(**locals()))
        sh____("{docker} exec test-box1 apt-get update".format(**locals()))
        # sh____("{docker} exec test-box1 apt-get install -y python-docker".format(**locals()))
        sh____("{docker} exec test-box1 apt-get install -y apache2".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
    def test_11804_ubuntu(self) -> None:
        prefix = PREFIX
        docker = DOCKER
        repo_image = "ubuntu-repo:18.04"
        box1_image = "ubuntu:18.04"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
        sh____("{docker} run -d --name test-repo {prefix}/{repo_image}".format(**locals()))
        mirror_ip = ip_container("test-repo")
        add_host = "--add-host archive.ubuntu.com:{mirror_ip} --add-host security.ubuntu.com:{mirror_ip}".format(**locals())
        sh____("{docker} run -d --name test-box1 {add_host} {box1_image} sleep 600".format(**locals()))
        sh____("{docker} exec test-box1 apt-get update".format(**locals()))
        # sh____("{docker} exec test-box1 apt-get install -y python-docker".format(**locals()))
        sh____("{docker} exec test-box1 apt-get install -y apache2".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
    def test_20000_centos(self) -> None:
        prefix = PREFIX
        docker = DOCKER
        mirrors = _docker_mirror
        repo_image = "centos-repo:7.3.1611"
        base_image = "centos:7.3.1611"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sh____("{mirrors} facts {base_image}".format(**locals()))
        sh____("{mirrors} start {base_image} --add-hosts".format(**locals()))
        sh____("{mirrors} stop {base_image}".format(**locals()))
    def test_20073_centos(self) -> None:
        docker = DOCKER
        mirror = _docker_mirror
        image = "centos:7.3.1611"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        repo_image = output("{mirror} repo {image}".format(**locals()))
        if not image_exist(repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} start {image} --add-hosts".format(**locals()))
        add_host = output("{mirror} start {image} --add-hosts".format(**locals())).strip()
        sh____("{docker} run -d --name test-box1 {add_host} {image} sleep 600".format(**locals()))
        sh____("{docker} exec test-box1 yum install -y python-docker-py".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} stop {image} --add-host".format(**locals()))
    def test_20074_centos(self) -> None:
        docker = DOCKER
        mirror = _docker_mirror
        image = "centos:7.4.1708"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        repo_image = output("{mirror} repo {image}".format(**locals()))
        if not image_exist(repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} start {image} --add-hosts".format(**locals()))
        add_host = output("{mirror} start {image} --add-hosts".format(**locals())).strip()
        sh____("{docker} run -d --name test-box1 {add_host} {image} sleep 600".format(**locals()))
        sh____("{docker} exec test-box1 yum install -y python-docker-py".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} stop {image} --add-host".format(**locals()))
    def test_20075_centos(self) -> None:
        docker = DOCKER
        mirror = _docker_mirror
        image = "centos:7.5.1804"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        repo_image = output("{mirror} repo {image}".format(**locals()))
        if not image_exist(repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} start {image} --add-hosts".format(**locals()))
        add_host = output("{mirror} start {image} --add-hosts".format(**locals())).strip()
        sh____("{docker} run -d --name test-box1 {add_host} {image} sleep 600".format(**locals()))
        sh____("{docker} exec test-box1 yum install -y python-docker-py".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} stop {image} --add-host".format(**locals()))
    def test_20076_centos(self) -> None:
        docker = DOCKER
        mirror = _docker_mirror
        image = "centos:7.6.1810"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        repo_image = output("{mirror} repo {image}".format(**locals()))
        if not image_exist(repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} start {image} --add-hosts".format(**locals()))
        add_host = output("{mirror} start {image} --add-hosts".format(**locals())).strip()
        sh____("{docker} run -d --name test-box1 {add_host} {image} sleep 600".format(**locals()))
        sh____("{docker} exec test-box1 yum install -y python-docker-py".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} stop {image} --add-host".format(**locals()))
    def test_20077_centos(self) -> None:
        docker = DOCKER
        mirror = _docker_mirror
        image = "centos:7.7.1908"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        repo_image = output("{mirror} repo {image}".format(**locals()))
        if not image_exist(repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} start {image} --add-hosts".format(**locals()))
        add_host = output("{mirror} start {image} --add-hosts".format(**locals())).strip()
        sh____("{docker} run -d --name test-box1 {add_host} {image} sleep 600".format(**locals()))
        sh____("{docker} exec test-box1 yum install -y python-docker-py".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} stop {image} --add-host".format(**locals()))
    def test_20080_centos(self) -> None:
        docker = DOCKER
        mirror = _docker_mirror
        image = "centos:8.0.1905"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        repo_image = output("{mirror} repo {image}".format(**locals()))
        if not image_exist(repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} start {image} --add-hosts".format(**locals()))
        add_host = output("{mirror} start {image} --add-hosts".format(**locals())).strip()
        sh____("{docker} run -d --name test-box1 {add_host} {image} sleep 600".format(**locals()))
        # sh____("{docker} exec test-box1 yum install -y python-docker-py".format(**locals())) # all /extras are now in epel
        sh____("{docker} exec test-box1 yum install -y python2-numpy".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} stop {image} --add-host".format(**locals()))
    def test_20081_centos(self) -> None:
        docker = DOCKER
        mirror = _docker_mirror
        image = "centos:8.1.1911"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        repo_image = output("{mirror} repo {image}".format(**locals()))
        if not image_exist(repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} start {image} --add-hosts".format(**locals()))
        add_host = output("{mirror} start {image} --add-hosts".format(**locals())).strip()
        sh____("{docker} run -d --name test-box1 {add_host} {image} sleep 600".format(**locals()))
        # sh____("{docker} exec test-box1 yum install -y python-docker-py".format(**locals())) # all /extras are now in epel
        sh____("{docker} exec test-box1 yum install -y python2-numpy".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} stop {image} --add-host".format(**locals()))
    def test_20083_centos(self) -> None:
        docker = DOCKER
        mirror = _docker_mirror
        image = "centos:8.3.2011"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        repo_image = output("{mirror} repo {image}".format(**locals()))
        if not image_exist(repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} start {image} --add-hosts".format(**locals()))
        add_host = output("{mirror} start {image} --add-hosts".format(**locals())).strip()
        sh____("{docker} run -d --name test-box1 {add_host} {image} sleep 600".format(**locals()))
        sh____("{docker} exec test-box1 yum install -y python2-numpy".format(**locals()))
        if not KEEP:
            sx____("{docker} rm -f test-box1".format(**locals()))
            sh____("{mirror} stop {image} --add-host".format(**locals()))
    def test_20091_centos(self) -> None:
        docker = DOCKER
        mirror = _docker_mirror
        image = "almalinux:9.1"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        repo_image = output("{mirror} repo {image}".format(**locals()))
        if not image_exist(repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} start {image} --add-hosts -v".format(**locals()))
        add_host = output("{mirror} start {image} --add-hosts".format(**locals())).strip()
        sh____("{docker} run -d --name test-box1 {add_host} {image} sleep 600".format(**locals()))
        sh____("{docker} exec test-box1 bash -c 'echo sslverify=false >>/etc/yum.conf'".format(**locals()))
        sh____("{docker} exec test-box1 yum install -y python3-numpy".format(**locals()))
        if not KEEP:
            sx____("{docker} rm -f test-box1".format(**locals()))
            sh____("{mirror} stop {image} --add-host".format(**locals()))
    def test_24422_opensuse(self) -> None:
        docker = DOCKER
        mirror = _docker_mirror
        image = "opensuse:42.2"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        repo_image = output("{mirror} repo {image}".format(**locals()))
        if not image_exist(repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} start {image} --add-hosts".format(**locals()))
        add_host = output("{mirror} start {image} --add-hosts".format(**locals())).strip()
        sh____("{docker} run -d --name test-box1 {add_host} {image} sleep 600".format(**locals()))
        sh____("{docker} exec test-box1 zypper install -y python-docker-py".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} stop {image} --add-host".format(**locals()))
    def test_24423_opensuse(self) -> None:
        docker = DOCKER
        mirror = _docker_mirror
        image = "opensuse:42.3"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        repo_image = output("{mirror} repo {image}".format(**locals()))
        if not image_exist(repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} start {image} --add-hosts".format(**locals()))
        add_host = output("{mirror} start {image} --add-hosts".format(**locals())).strip()
        sh____("{docker} run -d --name test-box1 {add_host} {image} sleep 600".format(**locals()))
        if MR143:
            # "zypper refresh repo-oss repo-update"
            sh____("{docker} exec test-box1 zypper mr --no-gpgcheck oss-update".format(**locals()))
        sh____("{docker} exec test-box1 zypper install -y python-docker-py".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} stop {image} --add-host".format(**locals()))
    def test_24150_opensuse(self) -> None:
        docker = DOCKER
        mirror = _docker_mirror
        image = "opensuse/leap:15.0"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        repo_image = output("{mirror} repo {image}".format(**locals()))
        if not image_exist(repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} start {image} --add-hosts".format(**locals()))
        add_host = output("{mirror} start {image} --add-hosts".format(**locals())).strip()
        sh____("{docker} run -d --name test-box1 {add_host} {image} sleep 600".format(**locals()))
        sh____("{docker} exec test-box1 zypper install -y python-docker-py".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} stop {image} --add-host".format(**locals()))
    def test_24151_opensuse(self) -> None:
        docker = DOCKER
        mirror = _docker_mirror
        image = "opensuse/leap:15.1"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        repo_image = output("{mirror} repo {image}".format(**locals()))
        if not image_exist(repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} start {image} --add-hosts".format(**locals()))
        add_host = output("{mirror} start {image} --add-hosts".format(**locals())).strip()
        sh____("{docker} run -d --name test-box1 {add_host} {image} sleep 600".format(**locals()))
        if MR151:
            # sh____("{docker} exec test-box1 zypper repos".format(**locals()))
            sh____("{docker} exec test-box1 zypper mr --no-gpgcheck repo-update".format(**locals()))
            sh____("{docker} exec test-box1 zypper rr repo-non-oss repo-update-non-oss".format(**locals()))
        sh____("{docker} exec test-box1 zypper install -y python python-xml".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} stop {image} --add-host".format(**locals()))
    def test_24152_opensuse(self) -> None:
        docker = DOCKER
        mirror = _docker_mirror
        image = "opensuse/leap:15.2"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        repo_image = output("{mirror} repo {image}".format(**locals()))
        if not image_exist(repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} start {image} --add-hosts".format(**locals()))
        add_host = output("{mirror} start {image} --add-hosts".format(**locals())).strip()
        sh____("{docker} run -d --name test-box1 {add_host} {image} sleep 600".format(**locals()))
        # if MR152:
        #   sh____("{docker} exec test-box1 zypper mr --no-gpgcheck repo-update".format(**locals()))
        sh____("{docker} exec test-box1 zypper install -y python python-xml".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} stop {image} --add-host".format(**locals()))
    def test_21404_ubuntu(self) -> None:
        docker = DOCKER
        mirror = _docker_mirror
        image = "ubuntu:14.04"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        repo_image = output("{mirror} repo {image}".format(**locals()))
        if not image_exist(repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} start {image} --add-hosts".format(**locals()))
        add_host = output("{mirror} start {image} --add-hosts".format(**locals())).strip()
        sh____("{docker} run -d --name test-box1 {add_host} {image} sleep 600".format(**locals()))
        sh____("{docker} exec test-box1 apt-get update".format(**locals()))
        # sh____("{docker} exec test-box1 apt-get install -y python-docker".format(**locals()))
        sh____("{docker} exec test-box1 apt-get install -y apache2".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} stop {image} --add-host".format(**locals()))
    def test_21604_ubuntu(self) -> None:
        docker = DOCKER
        mirror = _docker_mirror
        image = "ubuntu:16.04"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        repo_image = output("{mirror} repo {image}".format(**locals()))
        if not image_exist(repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} start {image} --add-hosts".format(**locals()))
        add_host = output("{mirror} start {image} --add-hosts".format(**locals())).strip()
        sh____("{docker} run -d --name test-box1 {add_host} {image} sleep 600".format(**locals()))
        sh____("{docker} exec test-box1 apt-get update".format(**locals()))
        # sh____("{docker} exec test-box1 apt-get install -y python-docker".format(**locals()))
        sh____("{docker} exec test-box1 apt-get install -y apache2".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} stop {image} --add-host".format(**locals()))
    def test_21804_ubuntu(self) -> None:
        docker = DOCKER
        mirror = _docker_mirror
        image = "ubuntu:18.04"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        repo_image = output("{mirror} repo {image}".format(**locals()))
        if not image_exist(repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} start {image} --add-hosts".format(**locals()))
        add_host = output("{mirror} start {image} --add-hosts".format(**locals())).strip()
        sh____("{docker} run -d --name test-box1 {add_host} {image} sleep 600".format(**locals()))
        sh____("{docker} exec test-box1 apt-get update".format(**locals()))
        # sh____("{docker} exec test-box1 apt-get install -y python-docker".format(**locals()))
        sh____("{docker} exec test-box1 apt-get install -y apache2".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} stop {image} --add-host".format(**locals()))

    def test_30007_centos(self) -> None:
        prefix = PREFIX
        docker = DOCKER
        mirrors = _docker_mirror
        repo_image = "centos-repo:7.3.1611"
        base_image = "centos:7.3.1611"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sh____("{mirrors} repos {base_image} --epel".format(**locals()))
        sh____("{mirrors} start {base_image} --add-hosts --epel".format(**locals()))
        sh____("{mirrors} stop {base_image} --epel".format(**locals()))
    def test_30008_centos(self) -> None:
        prefix = PREFIX
        docker = DOCKER
        mirrors = _docker_mirror
        repo_image = "centos-repo:8.3.2011"
        base_image = "centos:8.3.2011"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sh____("{mirrors} repos {base_image} --epel".format(**locals()))
        sh____("{mirrors} start {base_image} --add-hosts --epel".format(**locals()))
        sh____("{mirrors} stop {base_image} --epel".format(**locals()))
    @unittest.expectedFailure
    def test_30077_centos_epel(self) -> None:
        docker = DOCKER
        mirror = _docker_mirror
        image = "centos:7.7.1908"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        repo_image = output("{mirror} repo {image}".format(**locals()))
        if not image_exist(repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} repos {image} --add-hosts --epel".format(**locals()))
        sh____("{mirror} start {image} --add-hosts --epel".format(**locals()))
        add_host = output("{mirror} start {image} --add-hosts --epel".format(**locals())).strip()
        sh____("{docker} run -d --name test-box1 {add_host} {image} sleep 600".format(**locals()))
        sh____("{docker} exec test-box1 yum install -y epel-release".format(**locals()))
        sh____("{docker} exec test-box1 bash -c 'echo sslverify=false >> /etc/yum.conf'".format(**locals()))
        sh____("{docker} exec test-box1 yum install -y python36-flask".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} stop {image} --add-host".format(**locals()))
    def test_30079_centos_epel(self) -> None:
        docker = DOCKER
        mirror = _docker_mirror
        image = "centos:7.9.2009"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        repo_image = output("{mirror} repo {image}".format(**locals()))
        if not image_exist(repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} repos {image} --add-hosts --epel".format(**locals()))
        sh____("{mirror} start {image} --add-hosts --epel".format(**locals()))
        add_host = output("{mirror} start {image} --add-hosts --epel".format(**locals())).strip()
        sh____("{docker} run -d --name test-box1 {add_host} {image} sleep 600".format(**locals()))
        sh____("{docker} exec test-box1 yum install -y epel-release".format(**locals()))
        sh____("{docker} exec test-box1 bash -c 'echo sslverify=false >> /etc/yum.conf'".format(**locals()))
        sh____("{docker} exec test-box1 yum install -y python36-flask".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} stop {image} --add-host".format(**locals()))
    def test_30081_centos_epel(self) -> None:
        docker = DOCKER
        mirror = _docker_mirror
        image = "centos:8.1.1911"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        repo_image = output("{mirror} repo {image}".format(**locals()))
        if not image_exist(repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} start {image} --add-hosts --epel".format(**locals()))
        add_host = output("{mirror} start {image} --add-hosts --epel".format(**locals())).strip()
        sh____("{docker} run -d --name test-box1 {add_host} {image} sleep 600".format(**locals()))
        sh____("{docker} exec test-box1 yum install -y epel-release".format(**locals()))
        sh____("{docker} exec test-box1 bash -c 'echo sslverify=false >> /etc/yum.conf'".format(**locals()))
        sh____("{docker} exec test-box1 yum install -y python3-flask-sqlalchemy".format(**locals()))
        if not KEEP:
            sx____("{docker} rm -f test-box1".format(**locals()))
            sh____("{mirror} stop {image} --add-host".format(**locals()))
    def test_30083_centos_epel(self) -> None:
        docker = DOCKER
        mirror = _docker_mirror
        image = "centos:8.3.2011"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        repo_image = output("{mirror} repo {image}".format(**locals()))
        if not image_exist(repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} start {image} --add-hosts --epel".format(**locals()))
        add_host = output("{mirror} start {image} --add-hosts --epel".format(**locals())).strip()
        sh____("{docker} run -d --name test-box1 {add_host} {image} sleep 600".format(**locals()))
        sh____("{docker} exec test-box1 yum install -y epel-release".format(**locals()))
        sh____("{docker} exec test-box1 bash -c 'echo sslverify=false >> /etc/yum.conf'".format(**locals()))
        sh____("{docker} exec test-box1 yum install -y python3-flask-sqlalchemy".format(**locals()))
        if not KEEP:
            sx____("{docker} rm -f test-box1".format(**locals()))
            sh____("{mirror} stop {image} --add-host".format(**locals()))
    def test_30091_centos_epel(self) -> None:
        docker = DOCKER
        mirror = _docker_mirror
        image = "almalinux:9.1"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        repo_image = output("{mirror} repo {image}".format(**locals()))
        if not image_exist(repo_image): self.skipTest("have no " + repo_image)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sh____("{mirror} start {image} --add-hosts --epel".format(**locals()))
        add_host = output("{mirror} start {image} --add-hosts --epel".format(**locals())).strip()
        retry = "--connect-timeout 5 --retry 3 --retry-connrefused"
        sh____("{docker} run -d --name test-box1 {add_host} {image} sleep 600".format(**locals()))
        sh____("{docker} exec test-box1 bash -c 'echo sslverify=false >> /etc/yum.conf'".format(**locals()))
        sh____("{docker} exec test-box1 curl -k {retry} https://mirrors.almalinux.org".format(**locals()))
        sh____("{docker} exec test-box1 yum install -y epel-release".format(**locals()))
        sh____("{docker} exec test-box1 yum install -y python3-flask-basicauth".format(**locals()))
        if not KEEP:
            sx____("{docker} rm -f test-box1".format(**locals()))
            sh____("{mirror} stop {image} --add-host".format(**locals()))
##
    def test_99999_hello(self) -> None:
        print("... finished the testsuite ...")
        logg.info("finished the testsuite ...")

if __name__ == "__main__":
    from optparse import OptionParser
    _o = OptionParser("%prog [options] test*",
                      epilog=__doc__.strip().split("\n")[0])
    _o.add_option("-v", "--verbose", action="count", default=0,
                  help="increase logging level [%default]")
    _o.add_option("-p", "--prefix", metavar="HOST", default=PREFIX,
                  help="storage site for images [%default]")
    _o.add_option("-D", "--docker", metavar="EXE", default=DOCKER,
                  help="use another docker container tool [%default]")
    _o.add_option("-H", "--host", metavar="DOCKER_HOST", default=DOCKER_SOCKET,
                  help="choose another docker daemon [%default]")
    _o.add_option("-k", "--keep", action="store_true", default=KEEP,
                  help="do not clean up containers [%default]")
    _o.add_option("--failfast", action="store_true", default=False,
                  help="Stop the test run on the first error or failure. [%default]")
    opt, args = _o.parse_args()
    logging.basicConfig(level=logging.WARNING - opt.verbose * 5)
    KEEP = opt.keep
    PREFIX = opt.prefix
    DOCKER = opt.docker
    DOCKER_SOCKET = opt.host
    # unittest.main()
    suite = unittest.TestSuite()
    if not args: args = ["test_*"]
    for arg in args:
        for classname in sorted(globals()):
            if not classname.endswith("Test"):
                continue
            testclass = globals()[classname]
            for method in sorted(dir(testclass)):
                if "*" not in arg: arg += "*"
                if fnmatch(method, arg):
                    suite.addTest(testclass(method))
    Runner = unittest.TextTestRunner
    result = Runner(verbosity=opt.verbose, failfast=opt.failfast).run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
