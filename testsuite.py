#! /usr/bin/python3
"""
   You can just call tests by their number, or a common prefix thereof.
   (so that "./testsuite.py -v test_107" will run the tests from test_1070 to test_1079).
"""

__copyright__ = "(C) 2018-2020 Guido Draheim"
__contact__ = "https://github.com/gdraheim/docker-mirror-packages-repo"
__license__ = "CC0 Creative Commons Zero (Public Domain)"
__version__ = "1.5.2256"

import sys
import subprocess
import collections
import json
import os.path
import unittest
from fnmatch import fnmatchcase as fnmatch

import logging
logg = logging.getLogger("TESTSUITE")

if sys.version[0] == '2':
    string_types = basestring
    BlockingIOError = IOError
else:
    string_types = str
    xrange = range

KEEP=False
PREFIX="localhost:5000/mirror-packages"
DOCKER = "docker"
DOCKER_SOCKET="/var/run/docker.sock"
MR143 = True # modify repos of opensuse/leap:14.3
MR151 = True # modify repos of opensuse/leap:15.1

_docker_mirror = "./docker_mirror.py"

def decodes(text):
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
def sh____(cmd, shell=True):
    if isinstance(cmd, string_types):
        logg.debug(": %s", cmd)
    else:    
        logg.debug(": %s", " ".join(["'%s'" % item for item in cmd]))
    return subprocess.check_call(cmd, shell=shell)
def sx____(cmd, shell=True):
    if isinstance(cmd, string_types):
        logg.debug(": %s", cmd)
    else:    
        logg.debug(": %s", " ".join(["'%s'" % item for item in cmd]))
    return subprocess.call(cmd, shell=shell)
def output(cmd, shell=True):
    if isinstance(cmd, string_types):
        logg.debug(": %s", cmd)
    else:    
        logg.debug(": %s", " ".join(["'%s'" % item for item in cmd]))
    run = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE)
    out, err = run.communicate()
    return decodes(out)
def runs(cmd, shell=True):
    if isinstance(cmd, string_types):
        logg.debug(": %s", cmd)
    else:    
        logg.debug(": %s", " ".join(["'%s'" % item for item in cmd]))
    run = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = run.communicate()
    _subprocess = collections.namedtuple("_subprocess", ["out", "err", "rc"])
    return _subprocess(decodes(out), decodes(err), run.returncode)
    # return _subprocess(decodes(out.read()), decodes(err.read()), run.returncode)

def ip_container(name):
    docker = DOCKER
    cmd = "{docker} inspect {name}"
    proc = runs(cmd.format(**locals()))
    if proc.rc: 
        logg.debug("%s not found: rc=%i\n\t%s", name, proc.rc, proc.err)
        return 0
    values = json.loads(proc.out)
    if not values or "NetworkSettings" not in values[0]:
        cmd_run = cmd.format(**locals())
        logg.critical(" %s => %s ", cmd, values)
    return values[0]["NetworkSettings"]["IPAddress"]
def image_exist(name):
    return image_exists("", name)
def image_exists(prefix, name):
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
    return values[0]["Container"]
def make_file(name, content):
    with open(name, "w") as f:
        f.write(content)
def drop_file(name):
    if os.path.exists(name):
        os.remove(name)
    

class DockerMirrorPackagesTest(unittest.TestCase):
    def test_0001_hello(self):
        print("... starting the testsuite ...")
        logg.info("starting the testsuite ...")
    def test_1073_centos(self):
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
    def test_1074_centos(self):
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
    def test_1075_centos(self):
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
    def test_1076_centos(self):
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
    def test_1077_centos(self):
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
    def test_1079_centos(self):
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
    def test_1080_centos(self):
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
    def test_1081_centos(self):
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
    def test_1083_centos(self):
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
    def test_1142_opensuse(self):
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
    def test_1143_opensuse(self):
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
    def test_1150_opensuse(self):
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
    def test_1151_opensuse(self):
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
    def test_1152_opensuse(self):
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
        sh____("{docker} exec test-box1 zypper install -y python-docker-py".format(**locals()))
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f test-repo".format(**locals()))
    def test_1404_ubuntu(self):
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
    def test_1604_ubuntu(self):
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
    def test_1804_ubuntu(self):
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
    def test_2000_centos(self):
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
    def test_2073_centos(self):
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
    def test_2074_centos(self):
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
    def test_2075_centos(self):
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
    def test_2076_centos(self):
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
    def test_2077_centos(self):
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
    def test_2080_centos(self):
        docker = DOCKER
        mirror = _docker_mirror
        image = "centos:8"
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
    def test_2142_opensuse(self):
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
    def test_2143_opensuse(self):
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
    def test_2150_opensuse(self):
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
    def test_2151_opensuse(self):
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
    def test_2152_opensuse(self):
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
    def test_2404_ubuntu(self):
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
    def test_2604_ubuntu(self):
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
    def test_2804_ubuntu(self):
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


    def test_4073_centos(self):
        prefix = PREFIX
        docker = DOCKER
        repo_image = "centos-repo:7.3.1611"
        box1_image = "centos:7.3.1611"
        os_family = "RedHat"
        main_mirror = "mirrorlist.centos.org"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        box1_vendor = box1_image.split(":")[0]
        box1_version = box1_image.split(":")[1]
        test_repo = repo_image.replace(":","-")
        test_file = "tmp.{test_repo}-playbook.yml".format(**locals())
        #
        test_playbook_text = """
- hosts: localhost
  vars:
     base_image: "{box1_image}"
     base_command: "sleep 900"
  roles:
     - role: docker_distro_version
       image: "{{{{ base_image }}}}"
     - role: docker_distro_packages_mirror
  tasks:
     - debug: var=distro_packages_mirror_name
     - assert:
         that:
           - 'distro_vendor == "{box1_vendor}"'
           - 'distro_version == "{box1_version}"'
           - 'distro_packages_mirror_name == "mirror-packages/{repo_image}"'
           - '"--add-host" in distro_packages_mirror_add_hosts'
           - '"{main_mirror}:" in distro_packages_mirror_add_hosts'
           - 'distro_os_family == "{os_family}"'
     - name: remove setup container
       command: {docker} rm -f 'test-box1'
       ignore_errors: yes
     - name: start setup container
       command: {docker} run -d --rm=true {{{{ distro_packages_mirror_add_hosts }}}} \\
                     --name "test-box1" "{{{{ base_image }}}}" {{{{ base_command }}}}
     - name: attach setup container
       add_host:
         hostname: 'test-box1'
         ansible_connection: 'docker'
         ansible_user: "root"
         groups: [ 'target' ]
     - name: gather facts on it
       delegate_to: 'test-box1'
       setup:
         gather_subset: "all"
- hosts: target
  tasks:
     - package:
         name: "python-docker-py"       
""".format(**locals())
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f {test_repo}".format(**locals()))
        make_file(test_file, test_playbook_text)
        sh____("ansible-playbook {test_file} -v".format(**locals()))
        drop_file(test_file)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f {test_repo}".format(**locals()))
##
    def test_4074_centos(self):
        prefix = PREFIX
        docker = DOCKER
        repo_image = "centos-repo:7.4.1708"
        box1_image = "centos:7.4.1708"
        os_family = "RedHat"
        main_mirror = "mirrorlist.centos.org"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        box1_vendor = box1_image.split(":")[0]
        box1_version = box1_image.split(":")[1]
        test_repo = repo_image.replace(":","-")
        test_file = "tmp.{test_repo}-playbook.yml".format(**locals())
        #
        test_playbook_text = """
- hosts: localhost
  vars:
     base_image: "{box1_image}"
     base_command: "sleep 900"
  roles:
     - role: docker_distro_version
       image: "{{{{ base_image }}}}"
     - role: docker_distro_packages_mirror
  tasks:
     - debug: var=distro_packages_mirror_name
     - assert:
         that:
           - 'distro_vendor == "{box1_vendor}"'
           - 'distro_version == "{box1_version}"'
           - 'distro_packages_mirror_name == "mirror-packages/{repo_image}"'
           - '"--add-host" in distro_packages_mirror_add_hosts'
           - '"{main_mirror}:" in distro_packages_mirror_add_hosts'
           - 'distro_os_family == "{os_family}"'
     - name: remove setup container
       command: {docker} rm -f 'test-box1'
       ignore_errors: yes
     - name: start setup container
       command: {docker} run -d --rm=true {{{{ distro_packages_mirror_add_hosts }}}} \\
                     --name "test-box1" "{{{{ base_image }}}}" {{{{ base_command }}}}
     - name: attach setup container
       add_host:
         hostname: 'test-box1'
         ansible_connection: 'docker'
         ansible_user: "root"
         groups: [ 'target' ]
     - name: gather facts on it
       delegate_to: 'test-box1'
       setup:
         gather_subset: "all"
- hosts: target
  tasks:
     - package:
         name: "python-docker-py"       
""".format(**locals())
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f {test_repo}".format(**locals()))
        make_file(test_file, test_playbook_text)
        sh____("ansible-playbook {test_file} -v".format(**locals()))
        drop_file(test_file)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f {test_repo}".format(**locals()))
##
    def test_4075_centos(self):
        prefix = PREFIX
        docker = DOCKER
        repo_image = "centos-repo:7.5.1804"
        box1_image = "centos:7.5.1804"
        os_family = "RedHat"
        main_mirror = "mirrorlist.centos.org"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        box1_vendor = box1_image.split(":")[0]
        box1_version = box1_image.split(":")[1]
        test_repo = repo_image.replace(":","-")
        test_file = "tmp.{test_repo}-playbook.yml".format(**locals())
        #
        test_playbook_text = """
- hosts: localhost
  vars:
     base_image: "{box1_image}"
     base_command: "sleep 900"
  roles:
     - role: docker_distro_version
       image: "{{{{ base_image }}}}"
     - role: docker_distro_packages_mirror
  tasks:
     - debug: var=distro_packages_mirror_name
     - assert:
         that:
           - 'distro_vendor == "{box1_vendor}"'
           - 'distro_version == "{box1_version}"'
           - 'distro_packages_mirror_name == "mirror-packages/{repo_image}"'
           - '"--add-host" in distro_packages_mirror_add_hosts'
           - '"{main_mirror}:" in distro_packages_mirror_add_hosts'
           - 'distro_os_family == "{os_family}"'
     - name: remove setup container
       command: {docker} rm -f 'test-box1'
       ignore_errors: yes
     - name: start setup container
       command: {docker} run -d --rm=true {{{{ distro_packages_mirror_add_hosts }}}} \\
                     --name "test-box1" "{{{{ base_image }}}}" {{{{ base_command }}}}
     - name: attach setup container
       add_host:
         hostname: 'test-box1'
         ansible_connection: 'docker'
         ansible_user: "root"
         groups: [ 'target' ]
     - name: gather facts on it
       delegate_to: 'test-box1'
       setup:
         gather_subset: "all"
- hosts: target
  tasks:
     - package:
         name: "python-docker-py"       
""".format(**locals())
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f {test_repo}".format(**locals()))
        make_file(test_file, test_playbook_text)
        sh____("ansible-playbook {test_file} -v".format(**locals()))
        drop_file(test_file)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f {test_repo}".format(**locals()))
##
    def test_4076_centos(self):
        prefix = PREFIX
        docker = DOCKER
        repo_image = "centos-repo:7.6.1810"
        box1_image = "centos:7.6.1810"
        os_family = "RedHat"
        main_mirror = "mirrorlist.centos.org"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        box1_vendor = box1_image.split(":")[0]
        box1_version = box1_image.split(":")[1]
        test_repo = repo_image.replace(":","-")
        test_file = "tmp.{test_repo}-playbook.yml".format(**locals())
        #
        test_playbook_text = """
- hosts: localhost
  vars:
     base_image: "{box1_image}"
     base_command: "sleep 900"
  roles:
     - role: docker_distro_version
       image: "{{{{ base_image }}}}"
     - role: docker_distro_packages_mirror
  tasks:
     - debug: var=distro_packages_mirror_name
     - assert:
         that:
           - 'distro_vendor == "{box1_vendor}"'
           - 'distro_version == "{box1_version}"'
           - 'distro_packages_mirror_name == "mirror-packages/{repo_image}"'
           - '"--add-host" in distro_packages_mirror_add_hosts'
           - '"{main_mirror}:" in distro_packages_mirror_add_hosts'
           - 'distro_os_family == "{os_family}"'
     - name: remove setup container
       command: {docker} rm -f 'test-box1'
       ignore_errors: yes
     - name: start setup container
       command: {docker} run -d --rm=true {{{{ distro_packages_mirror_add_hosts }}}} \\
                     --name "test-box1" "{{{{ base_image }}}}" {{{{ base_command }}}}
     - name: attach setup container
       add_host:
         hostname: 'test-box1'
         ansible_connection: 'docker'
         ansible_user: "root"
         groups: [ 'target' ]
     - name: gather facts on it
       delegate_to: 'test-box1'
       setup:
         gather_subset: "all"
- hosts: target
  tasks:
     - package:
         name: "python-docker-py"       
""".format(**locals())
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f {test_repo}".format(**locals()))
        make_file(test_file, test_playbook_text)
        sh____("ansible-playbook {test_file} -v".format(**locals()))
        drop_file(test_file)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f {test_repo}".format(**locals()))
##
    def test_4077_centos(self):
        """
            docker pull centos:7
            docker tag centos:7 centos:7.7.1908
        """
        prefix = PREFIX
        docker = DOCKER
        repo_image = "centos-repo:7.7.1908"
        box1_image = "centos:7.7.1908"
        os_family = "RedHat"
        main_mirror = "mirrorlist.centos.org"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        box1_vendor = box1_image.split(":")[0]
        box1_version = box1_image.split(":")[1]
        test_repo = repo_image.replace(":","-")
        test_file = "tmp.{test_repo}-playbook.yml".format(**locals())
        #
        test_playbook_text = """
- hosts: localhost
  vars:
     base_image: "{box1_image}"
     base_command: "sleep 900"
  roles:
     - role: docker_distro_version
       image: "{{{{ base_image }}}}"
     - role: docker_distro_packages_mirror
  tasks:
     - debug: var=distro_packages_mirror_name
     - assert:
         that:
           - 'distro_vendor == "{box1_vendor}"'
           - 'distro_version == "{box1_version}"'
           - 'distro_packages_mirror_name == "mirror-packages/{repo_image}"'
           - '"--add-host" in distro_packages_mirror_add_hosts'
           - '"{main_mirror}:" in distro_packages_mirror_add_hosts'
           - 'distro_os_family == "{os_family}"'
     - name: remove setup container
       command: {docker} rm -f 'test-box1'
       ignore_errors: yes
     - name: start setup container
       command: {docker} run -d --rm=true {{{{ distro_packages_mirror_add_hosts }}}} \\
                     --name "test-box1" "{{{{ base_image }}}}" {{{{ base_command }}}}
     - name: attach setup container
       add_host:
         hostname: 'test-box1'
         ansible_connection: 'docker'
         ansible_user: "root"
         groups: [ 'target' ]
     - name: gather facts on it
       delegate_to: 'test-box1'
       setup:
         gather_subset: "all"
- hosts: target
  tasks:
     - package:
         name: "python-docker-py"       
""".format(**locals())
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f {test_repo}".format(**locals()))
        make_file(test_file, test_playbook_text)
        sh____("ansible-playbook {test_file} -v".format(**locals()))
        drop_file(test_file)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f {test_repo}".format(**locals()))
##
    def test_4080_centos(self):
        """
            docker pull centos:8
            docker tag centos:8 centos:8.0.1905
        """
        prefix = PREFIX
        docker = DOCKER
        repo_image = "centos-repo:8.0.1905"
        box1_image = "centos:8.0.1905"
        os_family = "RedHat"
        main_mirror = "mirrorlist.centos.org"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        box1_vendor = box1_image.split(":")[0]
        box1_version = box1_image.split(":")[1]
        test_repo = repo_image.replace(":","-")
        test_file = "tmp.{test_repo}-playbook.yml".format(**locals())
        #
        test_playbook_text = """
- hosts: localhost
  vars:
     base_image: "{box1_image}"
     base_command: "sleep 900"
  roles:
     - role: docker_distro_version
       image: "{{{{ base_image }}}}"
     - role: docker_distro_packages_mirror
  tasks:
     - debug: var=distro_packages_mirror_name
     - assert:
         that:
           - 'distro_vendor == "{box1_vendor}"'
           - 'distro_version == "{box1_version}"'
           - 'distro_packages_mirror_name == "mirror-packages/{repo_image}"'
           - '"--add-host" in distro_packages_mirror_add_hosts'
           - '"{main_mirror}:" in distro_packages_mirror_add_hosts'
           - 'distro_os_family == "{os_family}"'
     - name: remove setup container
       command: {docker} rm -f 'test-box1'
       ignore_errors: yes
     - name: start setup container
       command: {docker} run -d --rm=true {{{{ distro_packages_mirror_add_hosts }}}} \\
                     --name "test-box1" "{{{{ base_image }}}}" {{{{ base_command }}}}
     - name: attach setup container
       add_host:
         hostname: 'test-box1'
         ansible_connection: 'docker'
         ansible_user: "root"
         groups: [ 'target' ]
     - name: gather facts on it
       delegate_to: 'test-box1'
       setup:
         gather_subset: "all"
- hosts: target
  tasks:
     - package:
         name: "python2-numpy"       
""".format(**locals())
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f {test_repo}".format(**locals()))
        make_file(test_file, test_playbook_text)
        sh____("ansible-playbook {test_file} -v".format(**locals()))
        drop_file(test_file)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f {test_repo}".format(**locals()))
##
    def test_4143_opensuse(self):
        prefix = PREFIX
        docker = DOCKER
        repo_image = "opensuse-repo:42.3"
        box1_image = "opensuse:42.3"
        main_mirror = "download.opensuse.org"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        os_family = "Suse"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        box1_vendor = box1_image.split(":")[0].split("/")[0]
        box1_version = box1_image.split(":")[1]
        test_repo = repo_image.replace(":","-")
        test_file = "tmp.{test_repo}-playbook.yml".format(**locals())
        #
        test_playbook_text = """
- hosts: localhost
  vars:
     base_image: "{box1_image}"
     base_command: "sleep 900"
  roles:
     - role: docker_distro_version
       image: "{{{{ base_image }}}}"
     - role: docker_distro_packages_mirror
  tasks:
     - debug: var=distro_packages_mirror_name
     - assert:
         that:
           - 'distro_vendor == "{box1_vendor}"'
           - 'distro_version == "{box1_version}"'
           - 'distro_packages_mirror_name == "mirror-packages/{repo_image}"'
           - '"--add-host" in distro_packages_mirror_add_hosts'
           - '"{main_mirror}:" in distro_packages_mirror_add_hosts'
           - 'distro_os_family == "{os_family}"'
     - name: remove setup container
       command: {docker} rm -f 'test-box1'
       ignore_errors: yes
     - name: start setup container
       command: {docker} run -d --rm=true {{{{ distro_packages_mirror_add_hosts }}}} \\
                     --name "test-box1" "{{{{ base_image }}}}" {{{{ base_command }}}}
     - name: fixup setup container
       command: {docker} exec test-box1 bash -c "zypper repos ; zypper mr --no-gpgcheck oss-update"
       when: 'distro_os_family == "Suse"'
     - name: refresh and install package
       command: {docker} exec test-box1 bash -c "zypper refresh oss oss-update; zypper install -y python python-xml"
       when: 'distro_os_family == "Suse"'
     - name: attach setup container
       add_host:
         hostname: 'test-box1'
         ansible_connection: 'docker'
         ansible_user: "root"
         groups: [ 'target' ]
     - name: gather facts on it
       delegate_to: 'test-box1'
       setup:
         gather_subset: "all"
- hosts: target
  tasks:
     - package:
         name: "python-docker-py"       
""".format(**locals())
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f {test_repo}".format(**locals()))
        make_file(test_file, test_playbook_text)
        sh____("ansible-playbook {test_file} -v".format(**locals()))
        drop_file(test_file)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f {test_repo}".format(**locals()))
    def test_4150_opensuse(self):
        prefix = PREFIX
        docker = DOCKER
        repo_image = "opensuse-repo:15.0"
        box1_image = "opensuse/leap:15.0"
        main_mirror = "download.opensuse.org"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        os_family = "Suse"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        box1_vendor = box1_image.split(":")[0].split("/")[0]
        box1_version = box1_image.split(":")[1]
        test_repo = repo_image.replace(":","-")
        test_file = "tmp.{test_repo}-playbook.yml".format(**locals())
        #
        test_playbook_text = """
- hosts: localhost
  vars:
     base_image: "{box1_image}"
     base_command: "sleep 900"
  roles:
     - role: docker_distro_version
       image: "{{{{ base_image }}}}"
     - role: docker_distro_packages_mirror
  tasks:
     - debug: var=distro_packages_mirror_name
     - assert:
         that:
           - 'distro_vendor == "{box1_vendor}"'
           - 'distro_version == "{box1_version}"'
           - 'distro_packages_mirror_name == "mirror-packages/{repo_image}"'
           - '"--add-host" in distro_packages_mirror_add_hosts'
           - '"{main_mirror}:" in distro_packages_mirror_add_hosts'
           - 'distro_os_family == "{os_family}"'
     - name: remove setup container
       command: {docker} rm -f 'test-box1'
       ignore_errors: yes
     - name: start setup container
       command: {docker} run -d --rm=true {{{{ distro_packages_mirror_add_hosts }}}} \\
                     --name "test-box1" "{{{{ base_image }}}}" {{{{ base_command }}}}
     - name: fixup setup container
       command: {docker} exec test-box1 bash -c "zypper repos"
       when: 'distro_os_family == "Suse"'
     - name: refresh and install package
       command: {docker} exec test-box1 bash -c "zypper refresh repo-oss repo-update; zypper install -y python python-xml"
       when: 'distro_os_family == "Suse"'
     - name: attach setup container
       add_host:
         hostname: 'test-box1'
         ansible_connection: 'docker'
         ansible_user: "root"
         groups: [ 'target' ]
     - name: gather facts on it
       delegate_to: 'test-box1'
       setup:
         gather_subset: "all"
- hosts: target
  tasks:
     - package:
         name: "python-docker-py"       
""".format(**locals())
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f {test_repo}".format(**locals()))
        make_file(test_file, test_playbook_text)
        sh____("ansible-playbook {test_file} -v".format(**locals()))
        drop_file(test_file)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f {test_repo}".format(**locals()))
    def test_4151_opensuse(self):
        prefix = PREFIX
        docker = DOCKER
        repo_image = "opensuse-repo:15.1"
        box1_image = "opensuse/leap:15.1"
        main_mirror = "download.opensuse.org"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        os_family = "Suse"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        box1_vendor = box1_image.split(":")[0].split("/")[0]
        box1_version = box1_image.split(":")[1]
        test_repo = repo_image.replace(":","-")
        test_file = "tmp.{test_repo}-playbook.yml".format(**locals())
        #
        test_playbook_text = """
- hosts: localhost
  vars:
     base_image: "{box1_image}"
     base_command: "sleep 900"
  roles:
     - role: docker_distro_version
       image: "{{{{ base_image }}}}"
     - role: docker_distro_packages_mirror
  tasks:
     - debug: var=distro_packages_mirror_name
     - assert:
         that:
           - 'distro_vendor == "{box1_vendor}"'
           - 'distro_version == "{box1_version}"'
           - 'distro_packages_mirror_name == "mirror-packages/{repo_image}"'
           - '"--add-host" in distro_packages_mirror_add_hosts'
           - '"{main_mirror}:" in distro_packages_mirror_add_hosts'
           - 'distro_os_family == "{os_family}"'
     - name: remove setup container
       command: {docker} rm -f 'test-box1'
       ignore_errors: yes
     - name: start setup container
       command: {docker} run -d --rm=true {{{{ distro_packages_mirror_add_hosts }}}} \\
                     --name "test-box1" "{{{{ base_image }}}}" {{{{ base_command }}}}
     - name: fixup setup container
       command: {docker} exec test-box1 bash -c "zypper repos ; zypper mr --no-gpgcheck repo-oss repo-update repo-non-oss repo-update-non-oss"
       when: 'distro_os_family == "Suse"'
     - name: refresh and install package
       command: {docker} exec test-box1 bash -c "zypper refresh repo-oss repo-update; zypper install -y python python-xml"
       when: 'distro_os_family == "Suse"'
     - name: attach setup container
       add_host:
         hostname: 'test-box1'
         ansible_connection: 'docker'
         ansible_user: "root"
         groups: [ 'target' ]
     - name: gather facts on it
       delegate_to: 'test-box1'
       setup:
         gather_subset: "all"
- hosts: target
  tasks:
     - package:
         name: "python-docker-py"       
""".format(**locals())
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f {test_repo}".format(**locals()))
        make_file(test_file, test_playbook_text)
        sh____("ansible-playbook {test_file} -v".format(**locals()))
        drop_file(test_file)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f {test_repo}".format(**locals()))


##
    def test_5075_centos(self):
        prefix = PREFIX
        docker = DOCKER
        repo_image = "centos-repo:7.5.1804"
        box1_image = "centos:7.5.1804"
        os_family = "RedHat"
        main_mirror = "mirrorlist.centos.org"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        box1_vendor = box1_image.split(":")[0]
        box1_version = box1_image.split(":")[1]
        test_repo = repo_image.replace(":","-")
        test_file = "tmp.{test_repo}-playbook.yml".format(**locals())
        #
        test_playbook_text = """
- hosts: localhost
  vars:
     base_image: "{box1_image}"
     base_command: "sleep 9000"
  roles:
     - role: docker_distro_version
       image: "{{{{ base_image }}}}"
     - role: docker_distro_packages_mirrors
  tasks:
     - debug: var=distro_packages_mirror_name
     - assert:
         that:
           - 'distro_vendor == "{box1_vendor}"'
           - 'distro_version == "{box1_version}"'
           - 'distro_packages_mirror_name == "mirror-packages/{repo_image}"'
           - '"--add-host" in distro_packages_mirrors_add_hosts'
           - '"{main_mirror}:" in distro_packages_mirrors_add_hosts'
           - 'distro_os_family == "{os_family}"'
     - name: remove setup container
       command: {docker} rm -f 'test-box1'
       ignore_errors: yes
     - name: start setup container
       command: {docker} run -d --rm=true {{{{ distro_packages_mirrors_add_hosts }}}} \\
                     --name "test-box1" "{{{{ base_image }}}}" {{{{ base_command }}}}
     - name: attach setup container
       add_host:
         hostname: 'test-box1'
         ansible_connection: 'docker'
         ansible_user: "root"
         groups: [ 'target' ]
     - name: gather facts on it
       delegate_to: 'test-box1'
       setup:
         gather_subset: "all"
- hosts: target
  tasks:
     - name: install base package
       package:
         name: "python-docker-py"
     - name: install epel.repo
       package:
         name: "epel-release"
     - name: http for epel.repo
       replace:
         path: "/etc/yum.repos.d/epel.repo"
         regexp: "https://"
         replace: "http://"
     - name: install extra package
       package:
         name: "python2-numpy"
""".format(**locals())
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f {test_repo}".format(**locals()))
        make_file(test_file, test_playbook_text)
        sh____("ansible-playbook {test_file} -v".format(**locals()))
        drop_file(test_file)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f {test_repo}".format(**locals()))
##
    def test_5080_centos(self):
        """
            docker pull centos:8
            docker tag centos:8 centos:8.0.1905
        """
        prefix = PREFIX
        docker = DOCKER
        repo_image = "centos-repo:8.0.1905"
        box1_image = "centos:8.0.1905"
        os_family = "RedHat"
        main_mirror = "mirrorlist.centos.org"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        box1_vendor = box1_image.split(":")[0]
        box1_version = box1_image.split(":")[1]
        test_repo = repo_image.replace(":","-")
        test_file = "tmp.{test_repo}-playbook.yml".format(**locals())
        #
        test_playbook_text = """
- hosts: localhost
  vars:
     base_image: "{box1_image}"
     base_command: "sleep 9000"
  roles:
     - role: docker_distro_version
       image: "{{{{ base_image }}}}"
     - role: docker_distro_packages_mirrors
  tasks:
     - debug: var=distro_packages_mirror_name
     - assert:
         that:
           - 'distro_vendor == "{box1_vendor}"'
           - 'distro_version == "{box1_version}"'
           - 'distro_packages_mirror_name == "mirror-packages/{repo_image}"'
           - '"--add-host" in distro_packages_mirror_add_hosts'
           - '"{main_mirror}:" in distro_packages_mirror_add_hosts'
           - 'distro_os_family == "{os_family}"'
     - name: remove setup container
       command: {docker} rm -f 'test-box1'
       ignore_errors: yes
     - name: start setup container
       command: {docker} run -d --rm=true {{{{ distro_packages_mirror_add_hosts }}}} \\
                     --name "test-box1" "{{{{ base_image }}}}" {{{{ base_command }}}}
     - name: attach setup container
       add_host:
         hostname: 'test-box1'
         ansible_connection: 'docker'
         ansible_user: "root"
         groups: [ 'target' ]
     - name: gather facts on it
       delegate_to: 'test-box1'
       setup:
         gather_subset: "all"
- hosts: target
  tasks:
     - name: install base package
       package:
         name: "python2-numpy"       
     - name: install epel.repo
       package:
         name: "epel-release"
     - name: http for epel.repo
       replace:
         path: "/etc/yum.repos.d/epel.repo"
         regexp: "https://"
         replace: "http://"
     - name: install extra package
       package:
         name: "python2-beautifulsoup4"
""".format(**locals())
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f {test_repo}".format(**locals()))
        make_file(test_file, test_playbook_text)
        sh____("ansible-playbook {test_file} -v".format(**locals()))
        drop_file(test_file)
        sx____("{docker} rm -f test-box1".format(**locals()))
        sx____("{docker} rm -f {test_repo}".format(**locals()))
##

    def test_9999_hello(self):
        print("... finished the testsuite ...")
        logg.info("finished the testsuite ...")

if __name__ == "__main__":
    from optparse import OptionParser
    _o = OptionParser("%prog [options] test*",
       epilog=__doc__.strip().split("\n")[0])
    _o.add_option("-v","--verbose", action="count", default=0,
       help="increase logging level [%default]")
    _o.add_option("-p","--prefix", metavar="HOST", default=PREFIX,
       help="storage site for images [%default]")
    _o.add_option("-D","--docker", metavar="EXE", default=DOCKER,
       help="use another docker container tool [%default]")
    _o.add_option("-H","--host", metavar="DOCKER_HOST", default=DOCKER_SOCKET,
       help="choose another docker daemon [%default]")
    _o.add_option("-k","--keep", action="store_true", default=KEEP,
       help="do not clean up containers [%default]")
    opt, args = _o.parse_args()
    logging.basicConfig(level = logging.WARNING - opt.verbose * 5)
    KEEP = opt.keep
    PREFIX = opt.prefix
    DOCKER = opt.docker
    DOCKER_SOCKET = opt.host
    # unittest.main()
    suite = unittest.TestSuite()
    if not args: args = [ "test_*" ]
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
    result = Runner(verbosity=opt.verbose).run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
