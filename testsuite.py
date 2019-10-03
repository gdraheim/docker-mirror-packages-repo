#! /usr/bin/python3
"""
   You can just call tests by their number, or a common prefix thereof.
   (so that "./testsuite.py -v test_107" will run the tests from test_1070 to test_1079).
"""

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

PREFIX="localhost:5000/mirror-packages"
DOCKER_SOCKET="/var/run/docker.sock"

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
    return out
def runs(cmd, shell=True):
    if isinstance(cmd, string_types):
        logg.debug(": %s", cmd)
    else:    
        logg.debug(": %s", " ".join(["'%s'" % item for item in cmd]))
    run = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = run.communicate()
    _subprocess = collections.namedtuple("_subprocess", ["out", "err", "rc"])
    return _subprocess(out, err, run.returncode)
    # return _subprocess(out.read(), err.read(), run.returncode)

def ip_container(name):
    proc = runs("docker inspect {name}".format(**locals()))
    if proc.rc: 
        logg.debug("%s not found: rc=%i\n\t%s", name, proc.rc, proc.err)
        return 0
    values = json.loads(proc.out)
    if not values or "NetworkSettings" not in values[0]:
        logg.critical(" docker inspect %s => %s ", name, values)
    return values[0]["NetworkSettings"]["IPAddress"]
def image_exists(prefix, name):
    proc = runs("docker inspect {prefix}/{name}".format(**locals()))
    if proc.rc:
        logg.debug("%s not found: rc=%i\n\t%s", name, proc.rc, proc.err)
        return ""
    values = json.loads(proc.out)
    if not values or "Container" not in values[0]:
        return None
    return values[0]["Container"]
    

class DockerMirrorPackagesTest(unittest.TestCase):
    def test_0001_hello(self):
        print("... starting the testsuite ...")
        logg.info("starting the testsuite ...")
    def test_1073_centos(self):
        prefix = PREFIX
        repo_image = "centos-repo:7.3.1611"
        box1_image = "centos:7.3.1611"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sx____("docker rm -f test-box1")
        sx____("docker rm -f test-repo")
        sh____("docker run -d --name test-repo {prefix}/{repo_image}".format(**locals()))
        mirror = ip_container("test-repo")
        add_host = "--add-host mirrorlist.centos.org:{mirror}".format(**locals())
        sh____("docker run -d --name test-box1 {box1_image} sleep 600".format(**locals()))
        sh____("docker exec test-box1 yum install -y python-docker-py")
        sx____("docker rm -f test-box1")
        sx____("docker rm -f test-repo")
    def test_1074_centos(self):
        prefix = PREFIX
        repo_image = "centos-repo:7.4.1708"
        box1_image = "centos:7.4.1708"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sx____("docker rm -f test-box1")
        sx____("docker rm -f test-repo")
        sh____("docker run -d --name test-repo {prefix}/{repo_image}".format(**locals()))
        mirror = ip_container("test-repo")
        add_host = "--add-host mirrorlist.centos.org:{mirror}".format(**locals())
        sh____("docker run -d --name test-box1 {box1_image} sleep 600".format(**locals()))
        sh____("docker exec test-box1 yum install -y python-docker-py")
        sx____("docker rm -f test-box1")
        sx____("docker rm -f test-repo")
    def test_1075_centos(self):
        prefix = PREFIX
        repo_image = "centos-repo:7.5.1804"
        box1_image = "centos:7.5.1804"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sx____("docker rm -f test-box1")
        sx____("docker rm -f test-repo")
        sh____("docker run -d --name test-repo {prefix}/{repo_image}".format(**locals()))
        mirror = ip_container("test-repo")
        add_host = "--add-host mirrorlist.centos.org:{mirror}".format(**locals())
        sh____("docker run -d --name test-box1 {box1_image} sleep 600".format(**locals()))
        sh____("docker exec test-box1 yum install -y python-docker-py")
        sx____("docker rm -f test-box1")
        sx____("docker rm -f test-repo")
    def test_1076_centos(self):
        prefix = PREFIX
        repo_image = "centos-repo:7.6.1810"
        box1_image = "centos:7.6.1810"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sx____("docker rm -f test-box1")
        sx____("docker rm -f test-repo")
        sh____("docker run -d --name test-repo {prefix}/{repo_image}".format(**locals()))
        mirror = ip_container("test-repo")
        add_host = "--add-host mirrorlist.centos.org:{mirror}".format(**locals())
        sh____("docker run -d --name test-box1 {box1_image} sleep 600".format(**locals()))
        sh____("docker exec test-box1 yum install -y python-docker-py")
        sx____("docker rm -f test-box1")
        sx____("docker rm -f test-repo")
    def test_1077_centos(self):
        prefix = PREFIX
        repo_image = "centos-repo:7.7.1908"
        box1_image = "centos:7.7.1908"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sx____("docker rm -f test-box1")
        sx____("docker rm -f test-repo")
        sh____("docker run -d --name test-repo {prefix}/{repo_image}".format(**locals()))
        mirror = ip_container("test-repo")
        add_host = "--add-host mirrorlist.centos.org:{mirror}".format(**locals())
        sh____("docker run -d --name test-box1 {box1_image} sleep 600".format(**locals()))
        sh____("docker exec test-box1 yum install -y python-docker-py")
        sx____("docker rm -f test-box1")
        sx____("docker rm -f test-repo")
    def test_1080_centos(self):
        prefix = PREFIX
        repo_image = "centos-repo:8.0.1905"
        box1_image = "centos:8"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sx____("docker rm -f test-box1")
        sx____("docker rm -f test-repo")
        sh____("docker run -d --name test-repo {prefix}/{repo_image}".format(**locals()))
        mirror = ip_container("test-repo")
        add_host = "--add-host mirrorlist.centos.org:{mirror}".format(**locals())
        sh____("docker run -d --name test-box1 {box1_image} sleep 600".format(**locals()))
        sh____("docker exec test-box1 yum install -y python-docker-py")
        sx____("docker rm -f test-box1")
        sx____("docker rm -f test-repo")
    def test_1142_opensuse(self):
        prefix = PREFIX
        repo_image = "opensuse-repo:42.2"
        box1_image = "opensuse:42.2"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sx____("docker rm -f test-box1")
        sx____("docker rm -f test-repo")
        sh____("docker run -d --name test-repo {prefix}/{repo_image}".format(**locals()))
        mirror = ip_container("test-repo")
        add_host = "--add-host download.opensuse.org:{mirror}".format(**locals())
        sh____("docker run -d --name test-box1 {box1_image} sleep 600".format(**locals()))
        sh____("docker exec test-box1 zypper install -y python-docker-py")
        sx____("docker rm -f test-box1")
        sx____("docker rm -f test-repo")
    def test_1143_opensuse(self):
        prefix = PREFIX
        repo_image = "opensuse-repo:42.3"
        box1_image = "opensuse:42.3"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sx____("docker rm -f test-box1")
        sx____("docker rm -f test-repo")
        sh____("docker run -d --name test-repo {prefix}/{repo_image}".format(**locals()))
        mirror = ip_container("test-repo")
        add_host = "--add-host download.opensuse.org:{mirror}".format(**locals())
        sh____("docker run -d --name test-box1 {box1_image} sleep 600".format(**locals()))
        sh____("docker exec test-box1 zypper install -y python-docker-py")
        sx____("docker rm -f test-box1")
        sx____("docker rm -f test-repo")
    def test_1150_opensuse(self):
        prefix = PREFIX
        repo_image = "opensuse-repo:15.0"
        box1_image = "opensuse/leap:15.0"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sx____("docker rm -f test-box1")
        sx____("docker rm -f test-repo")
        sh____("docker run -d --name test-repo {prefix}/{repo_image}".format(**locals()))
        mirror = ip_container("test-repo")
        add_host = "--add-host download.opensuse.org:{mirror}".format(**locals())
        sh____("docker run -d --name test-box1 {box1_image} sleep 600".format(**locals()))
        sh____("docker exec test-box1 zypper install -y python-docker-py")
        sx____("docker rm -f test-box1")
        sx____("docker rm -f test-repo")
    def test_1151_opensuse(self):
        prefix = PREFIX
        repo_image = "opensuse-repo:15.1"
        box1_image = "opensuse/leap:15.1"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sx____("docker rm -f test-box1")
        sx____("docker rm -f test-repo")
        sh____("docker run -d --name test-repo {prefix}/{repo_image}".format(**locals()))
        mirror = ip_container("test-repo")
        add_host = "--add-host download.opensuse.org:{mirror}".format(**locals())
        sh____("docker run -d --name test-box1 {box1_image} sleep 600".format(**locals()))
        sh____("docker exec test-box1 zypper install -y python-docker-py")
        sx____("docker rm -f test-box1")
        sx____("docker rm -f test-repo")
    def test_1152_opensuse(self):
        prefix = PREFIX
        repo_image = "opensuse-repo:15.2"
        box1_image = "opensuse/leap:15.2"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sx____("docker rm -f test-box1")
        sx____("docker rm -f test-repo")
        sh____("docker run -d --name test-repo {prefix}/{repo_image}".format(**locals()))
        mirror = ip_container("test-repo")
        add_host = "--add-host download.opensuse.org:{mirror}".format(**locals())
        sh____("docker run -d --name test-box1 {box1_image} sleep 600".format(**locals()))
        sh____("docker exec test-box1 zypper install -y python-docker-py")
        sx____("docker rm -f test-box1")
        sx____("docker rm -f test-repo")
    def test_1404_ubuntu(self):
        prefix = PREFIX
        repo_image = "ubuntu-repo:14.04"
        box1_image = "ubuntu:14.04"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sx____("docker rm -f test-box1")
        sx____("docker rm -f test-repo")
        sh____("docker run -d --name test-repo {prefix}/{repo_image}".format(**locals()))
        mirror = ip_container("test-repo")
        add_host = "--add-host archive.ubuntu.com:{mirror} --add-host security.ubuntu.com:{mirror}".format(**locals())
        sh____("docker run -d --name test-box1 {box1_image} sleep 600".format(**locals()))
        sh____("docker exec test-box1 apt-get update")
        sh____("docker exec test-box1 apt-get install -y python-docker")
        sx____("docker rm -f test-box1")
        sx____("docker rm -f test-repo")
    def test_1604_ubuntu(self):
        prefix = PREFIX
        repo_image = "ubuntu-repo:16.04"
        box1_image = "ubuntu:16.04"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sx____("docker rm -f test-box1")
        sx____("docker rm -f test-repo")
        sh____("docker run -d --name test-repo {prefix}/{repo_image}".format(**locals()))
        mirror = ip_container("test-repo")
        add_host = "--add-host archive.ubuntu.com:{mirror} --add-host security.ubuntu.com:{mirror}".format(**locals())
        sh____("docker run -d --name test-box1 {box1_image} sleep 600".format(**locals()))
        sh____("docker exec test-box1 apt-get update")
        sh____("docker exec test-box1 apt-get install -y python-docker")
        sx____("docker rm -f test-box1")
        sx____("docker rm -f test-repo")
    def test_1804_ubuntu(self):
        prefix = PREFIX
        repo_image = "ubuntu-repo:18.04"
        box1_image = "ubuntu:18.04"
        if not os.path.exists(DOCKER_SOCKET): self.skipTest("docker-base test")
        if not image_exists(prefix, repo_image): self.skipTest("have no " + repo_image)
        sx____("docker rm -f test-box1")
        sx____("docker rm -f test-repo")
        sh____("docker run -d --name test-repo {prefix}/{repo_image}".format(**locals()))
        mirror = ip_container("test-repo")
        add_host = "--add-host archive.ubuntu.com:{mirror} --add-host security.ubuntu.com:{mirror}".format(**locals())
        sh____("docker run -d --name test-box1 {box1_image} sleep 600".format(**locals()))
        sh____("docker exec test-box1 apt-get update")
        sh____("docker exec test-box1 apt-get install -y python-docker")
        sx____("docker rm -f test-box1")
        sx____("docker rm -f test-repo")

    def test_9999_hello(self):
        print("... finished the testsuite ...")
        logg.info("finished the testsuite ...")

if __name__ == "__main__":
    from optparse import OptionParser
    _o = OptionParser("%prog [options] test*",
       epilog=__doc__.strip().split("\n")[0])
    _o.add_option("-v","--verbose", action="count", default=0,
       help="increase logging level [%default]")
    opt, args = _o.parse_args()
    logging.basicConfig(level = logging.WARNING - opt.verbose * 5)
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
