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
        # sh____("docker exec test-box1 yum install -y python-docker-py") # all /extras are now in epel
        sh____("docker exec test-box1 yum install -y python2-numpy")
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
    def test_4073_centos(self):
        prefix = PREFIX
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
       command: docker rm -f 'test-box1'
       ignore_errors: yes
     - name: start setup container
       command: docker run -d --rm=true {{{{ distro_packages_mirror_add_hosts }}}} \\
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
        sx____("docker rm -f test-box1")
        sx____("docker rm -f {test_repo}".format(**locals()))
        make_file(test_file, test_playbook_text)
        sh____("ansible-playbook {test_file} -v".format(**locals()))
        drop_file(test_file)
        sx____("docker rm -f test-box1")
        sx____("docker rm -f {test_repo}".format(**locals()))
##
    def test_4074_centos(self):
        prefix = PREFIX
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
       command: docker rm -f 'test-box1'
       ignore_errors: yes
     - name: start setup container
       command: docker run -d --rm=true {{{{ distro_packages_mirror_add_hosts }}}} \\
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
        sx____("docker rm -f test-box1")
        sx____("docker rm -f {test_repo}".format(**locals()))
        make_file(test_file, test_playbook_text)
        sh____("ansible-playbook {test_file} -v".format(**locals()))
        drop_file(test_file)
        sx____("docker rm -f test-box1")
        sx____("docker rm -f {test_repo}".format(**locals()))
##
    def test_4075_centos(self):
        prefix = PREFIX
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
       command: docker rm -f 'test-box1'
       ignore_errors: yes
     - name: start setup container
       command: docker run -d --rm=true {{{{ distro_packages_mirror_add_hosts }}}} \\
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
        sx____("docker rm -f test-box1")
        sx____("docker rm -f {test_repo}".format(**locals()))
        make_file(test_file, test_playbook_text)
        sh____("ansible-playbook {test_file} -v".format(**locals()))
        drop_file(test_file)
        sx____("docker rm -f test-box1")
        sx____("docker rm -f {test_repo}".format(**locals()))
##
    def test_4076_centos(self):
        prefix = PREFIX
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
       command: docker rm -f 'test-box1'
       ignore_errors: yes
     - name: start setup container
       command: docker run -d --rm=true {{{{ distro_packages_mirror_add_hosts }}}} \\
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
        sx____("docker rm -f test-box1")
        sx____("docker rm -f {test_repo}".format(**locals()))
        make_file(test_file, test_playbook_text)
        sh____("ansible-playbook {test_file} -v".format(**locals()))
        drop_file(test_file)
        sx____("docker rm -f test-box1")
        sx____("docker rm -f {test_repo}".format(**locals()))
##
    def test_4077_centos(self):
        """
            docker pull centos:7
            docker tag centos:7 centos:7.7.1908
        """
        prefix = PREFIX
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
       command: docker rm -f 'test-box1'
       ignore_errors: yes
     - name: start setup container
       command: docker run -d --rm=true {{{{ distro_packages_mirror_add_hosts }}}} \\
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
        sx____("docker rm -f test-box1")
        sx____("docker rm -f {test_repo}".format(**locals()))
        make_file(test_file, test_playbook_text)
        sh____("ansible-playbook {test_file} -v".format(**locals()))
        drop_file(test_file)
        sx____("docker rm -f test-box1")
        sx____("docker rm -f {test_repo}".format(**locals()))
##
    def test_4080_centos(self):
        """
            docker pull centos:8
            docker tag centos:8 centos:8.0.1905
        """
        prefix = PREFIX
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
       command: docker rm -f 'test-box1'
       ignore_errors: yes
     - name: start setup container
       command: docker run -d --rm=true {{{{ distro_packages_mirror_add_hosts }}}} \\
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
        sx____("docker rm -f test-box1")
        sx____("docker rm -f {test_repo}".format(**locals()))
        make_file(test_file, test_playbook_text)
        sh____("ansible-playbook {test_file} -v".format(**locals()))
        drop_file(test_file)
        sx____("docker rm -f test-box1")
        sx____("docker rm -f {test_repo}".format(**locals()))
##
    def test_4143_opensuse(self):
        prefix = PREFIX
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
       command: docker rm -f 'test-box1'
       ignore_errors: yes
     - name: start setup container
       command: docker run -d --rm=true {{{{ distro_packages_mirror_add_hosts }}}} \\
                     --name "test-box1" "{{{{ base_image }}}}" {{{{ base_command }}}}
     - name: fixup setup container
       command: docker exec test-box1 bash -c "zypper repos ; zypper mr --no-gpgcheck oss-update"
       when: 'distro_os_family == "Suse"'
     - name: fixup setup container
       command: docker exec test-box1 bash -c "zypper refresh oss oss-update; zypper install -y python python-xml"
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
        sx____("docker rm -f test-box1")
        sx____("docker rm -f {test_repo}".format(**locals()))
        make_file(test_file, test_playbook_text)
        sh____("ansible-playbook {test_file} -v".format(**locals()))
        drop_file(test_file)
        sx____("docker rm -f test-box1")
        sx____("docker rm -f {test_repo}".format(**locals()))
    def test_4150_opensuse(self):
        prefix = PREFIX
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
       command: docker rm -f 'test-box1'
       ignore_errors: yes
     - name: start setup container
       command: docker run -d --rm=true {{{{ distro_packages_mirror_add_hosts }}}} \\
                     --name "test-box1" "{{{{ base_image }}}}" {{{{ base_command }}}}
     - name: fixup setup container
       command: docker exec test-box1 bash -c "zypper repos"
       when: 'distro_os_family == "Suse"'
     - name: fixup setup container
       command: docker exec test-box1 bash -c "zypper refresh repo-oss repo-update; zypper install -y python python-xml"
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
        sx____("docker rm -f test-box1")
        sx____("docker rm -f {test_repo}".format(**locals()))
        make_file(test_file, test_playbook_text)
        sh____("ansible-playbook {test_file} -v".format(**locals()))
        drop_file(test_file)
        sx____("docker rm -f test-box1")
        sx____("docker rm -f {test_repo}".format(**locals()))
    def test_4151_opensuse(self):
        prefix = PREFIX
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
       command: docker rm -f 'test-box1'
       ignore_errors: yes
     - name: start setup container
       command: docker run -d --rm=true {{{{ distro_packages_mirror_add_hosts }}}} \\
                     --name "test-box1" "{{{{ base_image }}}}" {{{{ base_command }}}}
     - name: fixup setup container
       command: docker exec test-box1 bash -c "zypper repos ; zypper mr --no-gpgcheck repo-update"
       when: 'distro_os_family == "Suse"'
     - name: fixup setup container
       command: docker exec test-box1 bash -c "zypper refresh repo-oss repo-update; zypper install -y python python-xml"
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
        sx____("docker rm -f test-box1")
        sx____("docker rm -f {test_repo}".format(**locals()))
        make_file(test_file, test_playbook_text)
        sh____("ansible-playbook {test_file} -v".format(**locals()))
        drop_file(test_file)
        sx____("docker rm -f test-box1")
        sx____("docker rm -f {test_repo}".format(**locals()))


##
    def test_5075_centos(self):
        prefix = PREFIX
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
       command: docker rm -f 'test-box1'
       ignore_errors: yes
     - name: start setup container
       command: docker run -d --rm=true {{{{ distro_packages_mirror_add_hosts }}}} \\
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
         name: "python-numpy"
""".format(**locals())
        sx____("docker rm -f test-box1")
        sx____("docker rm -f {test_repo}".format(**locals()))
        make_file(test_file, test_playbook_text)
        sh____("ansible-playbook {test_file} -v".format(**locals()))
        drop_file(test_file)
        sx____("docker rm -f test-box1")
        sx____("docker rm -f {test_repo}".format(**locals()))
##
    def test_5080_centos(self):
        """
            docker pull centos:8
            docker tag centos:8 centos:8.0.1905
        """
        prefix = PREFIX
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
       command: docker rm -f 'test-box1'
       ignore_errors: yes
     - name: start setup container
       command: docker run -d --rm=true {{{{ distro_packages_mirror_add_hosts }}}} \\
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
         name: "python2-docker"       
""".format(**locals())
        sx____("docker rm -f test-box1")
        sx____("docker rm -f {test_repo}".format(**locals()))
        make_file(test_file, test_playbook_text)
        sh____("ansible-playbook {test_file} -v".format(**locals()))
        drop_file(test_file)
        sx____("docker rm -f test-box1")
        sx____("docker rm -f {test_repo}".format(**locals()))
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
