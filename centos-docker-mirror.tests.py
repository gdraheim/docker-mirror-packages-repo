#! /usr/bin/env python3
__copyright__ = "(C) 2025 Guido Draheim"
__contact__ = "https://github.com/gdraheim/docker-mirror-packages-repo"
__license__ = "CC0 Creative Commons Zero (Public Domain)"
__version__ = "1.7.7112"

# pylint: disable=unused-import,line-too-long,too-many-lines
from typing import Optional, Union, Dict, List, Any, Sequence, Callable, Iterable, cast, NamedTuple
import shutil
import inspect
import unittest
import sys
import os
import re
import time
from datetime import datetime as Time
from fnmatch import fnmatchcase as fnmatch
from glob import glob
import subprocess
#  getoutput, Popen, PIPE, call, CalledProcessError

import logging
logg = logging.getLogger("tests.centos")
DONE = (logging.ERROR + logging.WARNING)//2
logging.addLevelName(DONE, "DONE")
NIX = ""
LIST: List[str] = []

IMAGESREPO = os.environ.get("IMAGESREPO", "localhost:5000/mirror-packages")
IMAGESTESTREPO = os.environ.get("IMAGESTESTREPO", "localhost:5000/mirror-test")
DOCKERDEF = os.environ.get("DOCKER_EXE", os.environ.get("DOCKER_BIN", "docker"))
PYTHONDEF = os.environ.get("DOCKER_PYTHON", os.environ.get("DOCKER_PYTHON3", "python3"))
MIRRORDEF = os.environ.get("DOCKER_MIRROR_PY", os.environ.get("DOCKER_MIRROR",  "docker_mirror.py"))
DOCKER = DOCKERDEF
PYTHON = PYTHONDEF
MIRROR = MIRRORDEF
SCRIPT = "centos-docker-mirror.py"
PKGREPO = "yum"
PKGLIST = "yum"
ONLYVERSION = ""
COVERAGE = False
KEEP = False
DRY_RSYNC = 1
SLEEP = 66
VV="-v"
TRUE = 1
SKIPFULLIMAGE = True
KEEPFULLIMAGE = False
KEEPBASEIMAGE = False
SAVEBASEDISK = False

DISTRO1 = "almalinux"
DISTRO2 = "centos"

VER3: Dict[str, str] = {}
VER3["7.3"] = "7.3.1611"
VER3["7.9"] = "7.9.2009"
VER3["7.9"] = "7.9.2009"
VER3["8.3"] = "8.3.2011"
VER3["9.1"] = "9.1-20230407"
VER3["9.2"] = "9.2-20230718"
VER3["9.3"] = "9.3-20240410"
VER3["9.4"] = "9.4-20240530"

class DistroVer(NamedTuple):
    distro: str
    ver: str

def major(version):
    if len(version) > 2:
        if version[1] == ".":
            return version[0]
        else:
            return version[:2]
    return version

def sh(cmd: str, **args: Any) -> str:
    logg.debug("sh %s", cmd)
    return subprocess.getoutput(cmd, **args)
def calls(cmd: str, **args: Any) -> int:
    """ subprocess.call() defaults to shell=False"""
    logg.debug("run: %s", cmd)
    return calls_(cmd, **args)
def calls_(cmd: str, **args: Any) -> int:
    if isinstance(cmd, str):
        return subprocess.call(cmd, shell=True, **args)
    else:
        return subprocess.call(cmd, shell=False, **args)

class CompletedProc(NamedTuple):
    """ aligned with subprocess.CompletedProcess (Python 3.5) """
    stdout: str
    stderr: str
    returncode: int
    def getvalue(self) -> str:
        return self.stdout.rstrip()
    @property
    def out(self) -> str:
        return self.getvalue()
    @property
    def err(self) -> str:
        return self.stderr.rstrip()
    @property
    def ret(self) -> int:
        return self.returncode
    def check_returncode(self) -> None:
        if self.returncode != 0:
            raise subprocess.CalledProcessError(returncode=self.returncode, cmd = [], output=self.stdout, stderr=self.stderr)
def runs(cmd: str, **args: Any) -> CompletedProc:
    """ subprocess.run() defaults to shell=False (Python 3.5) and capture_output=False (Python 3.7)"""
    logg.debug("run: %s", cmd)
    return runs_(cmd, **args)
def runs_(cmd: str, **args: Any) -> CompletedProc:
    if isinstance(cmd, str):
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **args)
    else:
        proc = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **args)
    out, err = proc.communicate()
    return CompletedProc(decodes(out), decodes(err), proc.returncode)
def decodes(text: Union[str, bytes]) -> str:
    """ no need to provide encoding for subprocess.run() or subprocess.call() """
    if isinstance(text, bytes):
        encoded = sys.getdefaultencoding()
        if encoded in ["ascii"]:
            encoded = "utf-8"
        try:
            return text.decode(encoded)
        except: # pylint: disable=bare-except
            return text.decode("latin-1")
    return text

def get_HOME(root = False):
    if root: return "/root"
    return os.path.expanduser("~")
def get_CONFIG_HOME(root = False):
    CONFIG = "/etc"
    if root: return CONFIG
    HOME = get_HOME(root)
    return os.environ.get("XDG_CONFIG_HOME", HOME + "/.config")
def get_CACHE_HOME(root = False):
    CACHE = "/var/cache"
    if root: return CACHE
    HOME = get_HOME(root)
    return os.environ.get("XDG_CACHE_HOME", HOME + "/.cache")
def get_DATA_HOME(root = False):
    SHARE = "/usr/share"
    if root: return SHARE
    HOME = get_HOME(root)
    return os.environ.get("XDG_DATA_HOME", HOME + "/.local/share")
def get_LOG_DIR(root = False):
    LOGDIR = "/var/log"
    if root: return LOGDIR
    CONFIG = get_CONFIG_HOME(root)
    return os.path.join(CONFIG, "log")


def get_caller_name() -> str:
    frame = inspect.currentframe().f_back.f_back  # type: ignore
    return frame.f_code.co_name  # type: ignore
def get_caller_caller_name() -> str:
    frame = inspect.currentframe().f_back.f_back.f_back  # type: ignore
    return frame.f_code.co_name  # type: ignore

class CentosMirrorTest(unittest.TestCase):
    def caller_testname(self) -> str:
        name = get_caller_caller_name()
        x1 = name.find("_")
        if x1 < 0: return name
        x2 = name.find("_", x1 + 1)
        if x2 < 0: return name
        return name[:x2]
    def testname(self, suffix: str = NIX) -> str:
        name = self.caller_testname()
        if suffix:
            return name + "_" + suffix
        return name
    def testdir(self, testname: str = NIX, keep: bool = False) -> str:
        testname = testname or self.caller_testname()
        newdir = "tmp/tmp." + testname
        if os.path.isdir(newdir) and not keep:
            shutil.rmtree(newdir)
        if not os.path.isdir(newdir):
            os.makedirs(newdir)
        return newdir
    def rm_testdir(self, testname: str = NIX) -> str:
        testname = testname or self.caller_testname()
        newdir = "tmp/tmp." + testname
        if os.path.isdir(newdir):
            if not KEEP:
                shutil.rmtree(newdir)
        return newdir
    def coverage(self, testname: str = NIX) -> None:
        testname = testname or self.caller_testname()
        newcoverage = ".coverage."+testname
        oldcoverage = ".coverage"
        if os.path.isfile(oldcoverage):
            # shutil.copy(oldcoverage, newcoverage)
            f = open(oldcoverage, "rb")
            text = f.read()
            f.close()
            text2 = re.sub(rb"(\]\}\})[^{}]*(\]\}\})$", rb"\1", text)
            f = open(newcoverage, "wb")
            f.write(text2)
            f.close()
            os.unlink(oldcoverage)
    def cover(self) -> str:
        python = PYTHON
        cover = F"{python} -m coverage run -a" if COVERAGE else python
        return cover
    def testver(self, testname: str = NIX) -> None:
        testname = testname or self.caller_testname()
        ver3 = testname[-3:]
        ver2 = ver3[0:2]
        rel1 = ver3[2]
        if ver2.startswith("0") or ver2.startswith("1"):
            ver2 = ver2[1]
        if ver2 in ["6", "7", "8"]:
            return DistroVer("centos", ver2 + "." + rel1)
        else:
            return DistroVer("almalinux", ver2 + "." + rel1)
    def imagesdangling(self) -> List[str]:
        images: List[str] = []
        docker = DOCKER
        cmd = F"{docker} image list -q -f dangling=true"
        run = runs(cmd)
        for line in run.stdout.splitlines():
            images += [ line ]
        return images
    def imageslist(self, pat: Optional[str] = None) -> List[str]:
        images: List[str] = []
        docker = DOCKER
        cmd = F"{docker} image list -q --no-trunc --format {{{{.Repository}}}}:{{{{.Tag}}}}"
        run = runs_(cmd)
        if run.ret:
            logg.debug("out: %s", run.stdout)
        for line in run.stdout.splitlines():
            if not pat:
                continue
            elif "*" in pat:
                if fnmatch(line, pat):
                    images += [ line.rstrip() ]
            else:
                if line.startswith(pat):
                    images += [ line.rstrip() ]
        return images
    def containerlist(self, pat: Optional[str] = None) -> List[str]:
        images: List[str] = []
        docker = DOCKER
        cmd = F"{docker} container list -a --no-trunc --format {{{{.Names}}}}"
        run = runs_(cmd)
        if run.ret:
            logg.debug("out: %s", run.stdout)
        for line in run.stdout.splitlines():
            if not pat:
                continue
            elif "*" in pat:
                if fnmatch(line, pat):
                    images += [ line.rstrip() ]
            else:
                if line.startswith(pat):
                    images += [ line.rstrip() ]
        return images
    def repocontainer(self, testname: str = NIX) -> List[str]: # pylint: disable=unused-argument
        return self.containerlist("opensuse-repo")
    def testrepo(self, testname: str = NIX) -> str: # pylint: disable=unused-argument
        return IMAGESTESTREPO
    def rm_images(self, testname: str = NIX) -> List[str]: # pylint: disable=unused-argument
        pat = self.testrepo()
        images = self.imageslist(pat) + self.imagesdangling()
        docker = DOCKER
        cmd = F"{docker} rmi"
        if images:
            for image in images:
                cmd += F" {image}"
            calls(cmd)
        return images
    def testcontainer(self, testname: str = NIX) -> str:
        name = testname or self.caller_testname()
        return F"mirror-test-{name}"
    def rm_container(self, testname: str = NIX) -> List[str]: # pylint: disable=unused-argument
        docker = DOCKER
        pat = "mirror-test-"
        images = self.containerlist(pat) + self.repocontainer()
        cmd = F"{docker} stop"
        if images:
            for image in images:
                cmd += F" {image}"
            calls(cmd)
        time.sleep(1)
        images = self.containerlist(pat) + self.repocontainer()
        cmd = F"{docker} rm -f"
        if images:
            for image in images:
                cmd += F" {image}"
            calls(cmd)
        return images
    #
    def test_70010(self) -> None:
        cover = self.cover()
        script = SCRIPT
        cmd = F"{cover} {script} --help"
        out = sh(cmd)
        logg.debug("out: %s", out)
        self.assertIn("imagesrepo=PREFIX", out)
        self.coverage()
    def test_70011(self) -> None:
        cover = self.cover()
        script = SCRIPT
        cmd = F"{cover} {script} commands"
        out = sh(cmd)
        logg.debug("out: %s", out)
        self.assertIn("|disk|", out)
        self.assertIn("|image|", out)
        self.assertIn("|repo|", out)
        self.assertIn("|datadir|", out)
        self.assertIn("|version", out)
        self.coverage()
    def test_70018(self) -> None:
        cover = self.cover()
        script = SCRIPT
        cmd = F"{cover} {script} badcommand"
        run = runs(cmd)
        logg.debug("out: %s", run.out)
        self.assertEqual(1, run.ret)
        self.coverage()
    def test_70020(self) -> None:
        cover = self.cover()
        script = SCRIPT
        cmd = F"{cover} {script} datadir"
        out = sh(cmd)
        logg.debug("out: %s", out)
        self.coverage()
    def test_70021(self) -> None:
        cover = self.cover()
        script = SCRIPT
        cmd = F"{cover} {script} scripts"
        out = sh(cmd)
        logg.debug("out: %s", out)
        self.assertEqual("./scripts", out.strip())
        self.coverage()
    def test_70168(self) -> None:
        _distro, ver = self.testver()
        version = "6.8"
        self.assertEqual(ver, "6.8")
        cover = self.cover()
        script = SCRIPT
        cmd = F"{cover} {script} {ver} version"
        run = runs(cmd)
        have = run.out
        errs = run.err
        logg.debug("out: %s", have)
        self.assertEqual(version, have)
        self.assertIn("is not a known os version", errs)
        self.coverage()
    def test_70173(self) -> None:
        _distro, ver = self.testver()
        self.assertEqual(ver, "7.3")
        version = "7.3.1611"
        cover = self.cover()
        script = SCRIPT
        cmd = F"{cover} {script} {ver} version"
        run = runs(cmd)
        have = run.out
        errs = run.err
        logg.debug("out: %s", have)
        self.assertEqual(version, have)
        self.assertEqual("", errs)
        cmd = F"{cover} {script} {ver} distros"
        run = runs(cmd)
        want = ["centos", "epel"]
        have = run.out.splitlines()
        errs = run.err
        logg.debug("out: %s", have)
        self.assertEqual(want, have)
        self.assertEqual("", errs)
        cmd = F"{cover} {script} {ver} distdirs"
        run = runs(cmd)
        want = ['centosplus', 'extras', 'os', 'sclo', 'updates']
        have = run.out.splitlines()
        errs = run.err
        logg.debug("out: %s", have)
        self.assertEqual(want, have)
        self.assertEqual("", errs)
        self.coverage()
    def test_70177(self) -> None:
        _distro, ver = self.testver()
        version = "7.7.1908"
        self.assertEqual(ver, "7.7")
        cover = self.cover()
        script = SCRIPT
        cmd = F"{cover} {script} {ver} version"
        run = runs(cmd)
        have = run.stdout.strip()
        errs = run.stderr.strip()
        logg.debug("out: %s", have)
        self.assertEqual(version, have)
        self.assertIn("", errs)
        cmd = F"{cover} {script} {ver} distros"
        run = runs(cmd)
        want = ["centos", "epel"]
        have = run.out.splitlines()
        errs = run.err
        logg.debug("out: %s", have)
        self.assertEqual(want, have)
        self.assertEqual("", errs)
        cmd = F"{cover} {script} {ver} distdirs"
        run = runs(cmd)
        want = ['centosplus', 'extras', 'os', 'sclo', 'updates']
        have = run.out.splitlines()
        errs = run.err
        logg.debug("out: %s", have)
        self.assertEqual(want, have)
        self.assertEqual("", errs)
        self.coverage()
    def test_70183(self) -> None:
        _distro, ver = self.testver()
        self.assertEqual(ver, "8.3")
        version = "8.3.2011"
        cover = self.cover()
        script = SCRIPT
        cmd = F"{cover} {script} {ver} version"
        run = runs(cmd)
        have = run.stdout.strip()
        errs = run.stderr.strip()
        logg.debug("out: %s", have)
        self.assertEqual(version, have)
        self.assertEqual("", errs)
        cmd = F"{cover} {script} {ver} distros"
        run = runs(cmd)
        want = ["centos", "epel"]
        have = run.out.splitlines()
        errs = run.err
        logg.debug("out: %s", have)
        self.assertEqual(want, have)
        self.assertEqual("", errs)
        cmd = F"{cover} {script} {ver} distdirs"
        run = runs(cmd)
        want = ['AppStream', 'BaseOS', 'PowerTools', 'centosplus', 'extras']
        have = run.out.splitlines()
        errs = run.err
        logg.debug("out: %s", have)
        self.assertEqual(want, have)
        self.assertEqual("", errs)
        self.coverage()
    def test_70191(self) -> None:
        _distro, ver = self.testver()
        self.assertEqual(ver, "9.1")
        version = "9.1-20230407"
        cover = self.cover()
        script = SCRIPT
        cmd = F"{cover} {script} {ver} version"
        run = runs(cmd)
        have = run.stdout.strip()
        errs = run.stderr.strip()
        logg.debug("out: %s", have)
        self.assertEqual(version, have)
        self.assertEqual("", errs)
        cmd = F"{cover} {script} {ver} distros"
        run = runs(cmd)
        want = ["almalinux", "epel"]
        have = run.out.splitlines()
        errs = run.err
        logg.debug("out: %s", have)
        self.assertEqual(want, have)
        self.assertEqual("", errs)
        cmd = F"{cover} {script} {ver} distdirs"
        run = runs(cmd)
        want = ['AppStream', 'BaseOS', 'CRB', 'extras', 'plus']
        have = run.out.splitlines()
        errs = run.err
        logg.debug("out: %s", have)
        self.assertEqual(want, have)
        self.assertEqual("", errs)
        self.coverage()
    def test_70196(self) -> None:
        _distro, ver = self.testver()
        self.assertEqual(ver, "9.6")
        cover = self.cover()
        script = SCRIPT
        cmd = F"{cover} {script} {ver} version"
        run = runs(cmd)
        have = run.stdout.strip()
        errs = run.stderr.strip()
        logg.debug("out: %s", have)
        self.assertEqual(ver, have)
        self.assertIn("is not a known os version", errs)
        self.coverage()
    def test_70197(self) -> None:
        ver2 = "7"
        ver = "7.9.2009"
        cover = self.cover()
        script = SCRIPT
        cmd = F"{cover} {script} {ver2} version"
        run = runs(cmd)
        have = run.stdout.strip()
        errs = run.stderr.strip()
        logg.debug("out: %s", have)
        self.assertEqual(ver, have)
        self.assertEqual("", errs)
        self.coverage()
    def test_70198(self) -> None:
        ver2 = "8"
        ver = "8.9-20240410"
        cover = self.cover()
        script = SCRIPT
        cmd = F"{cover} {script} {ver2} version"
        run = runs(cmd)
        have = run.stdout.strip()
        errs = run.stderr.strip()
        logg.debug("out: %s", have)
        self.assertEqual(ver, have)
        self.assertEqual("", errs)
        self.coverage()
    def test_70199(self) -> None:
        ver2 = "9"
        ver = "9.4-20240530"
        cover = self.cover()
        script = SCRIPT
        cmd = F"{cover} {script} {ver2} version"
        run = runs(cmd)
        have = run.stdout.strip()
        errs = run.stderr.strip()
        logg.debug("out: %s", have)
        self.assertEqual(ver, have)
        self.assertEqual("", errs)
        self.coverage()
    def test_70200(self) -> None:
        tmp = self.testdir()
        cover = self.cover()
        script = SCRIPT
        cmd = F"{cover} {script} datadir"
        run = runs(cmd, env={"REPODATADIR": tmp})
        have = run.stdout.strip()
        logg.debug("out: %s", have)
        self.assertEqual(tmp, have)
        self.coverage()
        self.rm_testdir()
    def test_71001(self) -> None:
        tmp = self.testdir()
        cover = self.cover()
        script = SCRIPT
        cmd = F"{cover} {script} datadir --datadir={tmp}"
        run = runs(cmd)
        have = run.stdout.strip()
        logg.debug("out: %s", have)
        self.assertEqual(tmp, have)
        self.coverage()
        self.rm_testdir()
    def test_71002(self) -> None:
        tmp = self.testdir()
        cover = self.cover()
        script = SCRIPT
        data = F"{tmp}/data"
        repo = F"{tmp}/repo"
        cmd = F"{cover} {script} datadir --datadir={data} --repodir={repo}"
        run = runs(cmd)
        have = run.stdout.strip()
        logg.debug("out: %s", have)
        self.assertNotEqual(data, have) # datadir does now exist
        self.assertEqual(repo, have) # repodir not a fallback
        self.coverage()
        self.rm_testdir()
    def test_71003(self) -> None:
        tmp = self.testdir()
        cover = self.cover()
        script = SCRIPT
        data = F"{tmp}/data"
        repo = F"{tmp}/repo"
        os.makedirs(data)
        cmd = F"{cover} {script} datadir --datadir={data} --repodir={repo}"
        run = runs(cmd)
        have = run.stdout.strip()
        logg.debug("out: %s", have)
        self.assertEqual(data, have) # datadir does now exist
        self.assertNotEqual(repo, have) # repodir not a fallback
        self.coverage()
        self.rm_testdir()
    def test_71173(self) -> None:
        self.check_dir(self.testname())
    def test_71179(self) -> None:
        self.check_dir(self.testname())
    def test_71183(self) -> None:
        self.check_dir(self.testname())
    def test_71191(self) -> None:
        self.check_dir(self.testname())
    def test_71192(self) -> None:
        self.check_dir(self.testname())
    def test_71193(self) -> None:
        self.check_dir(self.testname())
    def test_71194(self) -> None:
        self.check_dir(self.testname())
    def check_dir(self, testname: str) -> None:
        distro, ver = self.testver(testname)
        ver3 = VER3[ver]
        if ONLYVERSION and ver != ONLYVERSION:
            self.skipTest(F"not testing {ver} (--only {ONLYVERSION})")
        tmp = self.testdir(testname)
        cover = self.cover()
        script = SCRIPT
        data = F"{tmp}/data"
        repo = F"{tmp}/repo"
        want = F"{repo}/{distro}.{ver3}"
        os.makedirs(data)
        #
        cmd = F"{cover} {script} {ver} dir --datadir={data} --repodir={repo}"
        run = runs(cmd)
        have = run.stdout.strip()
        logg.debug("out: %s", have)
        self.assertEqual(want, have)
        self.assertTrue(os.path.isdir(os.path.join(want, ".")))
        self.assertTrue(os.path.islink(want))
        self.assertIn(data, os.readlink(want))
        #
        want = F"{repo}/{distro}.{ver3}.alt"
        cmd = F"{cover} {script} {ver} dir --datadir={data} --repodir={repo} --variant=alt"
        run = runs(cmd)
        have = run.stdout.strip()
        logg.debug("out: %s", have)
        self.assertEqual(want, have)
        self.assertTrue(os.path.isdir(os.path.join(want, ".")))
        self.assertTrue(os.path.islink(want))
        self.assertIn(data, os.readlink(want))
        #
        want = os.path.abspath(F"{data}/{distro}.{ver3}.disk/srv/repo")
        cmd = F"{cover} {script} {ver} diskpath --datadir={data} --repodir={repo}"
        run = runs(cmd)
        have = run.stdout.strip()
        logg.debug("out: %s", have)
        self.assertEqual(want, have)
        #
        want = os.path.abspath(F"{data}/{distro}.{ver3}.altdisk/srv/repo")
        cmd = F"{cover} {script} {ver} diskpath --datadir={data} --repodir={repo} --variant=alt"
        run = runs(cmd)
        have = run.stdout.strip()
        logg.debug("out: %s", have)
        self.assertEqual(want, have)
        #
        want = os.path.abspath(F"{data}/{distro}.{ver3}.altdisktmp/srv/repo")
        cmd = F"{cover} {script} {ver} diskpath --datadir={data} --repodir={repo} --variant=alt --disksuffix=disktmp"
        run = runs(cmd)
        have = run.stdout.strip()
        logg.debug("out: %s", have)
        self.assertEqual(want, have)
        #
        self.coverage(testname)
        self.rm_testdir(testname)
    def test_72173(self) -> None:
        self.check_epeldir(self.testname())
    def test_72179(self) -> None:
        self.check_epeldir(self.testname())
    def test_72183(self) -> None:
        self.check_epeldir(self.testname())
    def test_72191(self) -> None:
        self.check_epeldir(self.testname())
    def test_72192(self) -> None:
        self.check_epeldir(self.testname())
    def test_72193(self) -> None:
        self.check_epeldir(self.testname())
    def test_72194(self) -> None:
        self.check_epeldir(self.testname())
    def check_epeldir(self, testname: str) -> None:
        _basedistro, ver = self.testver(testname)
        # ver3 = VER3[ver]
        epel = major(ver)
        if ONLYVERSION and ver != ONLYVERSION:
            self.skipTest(F"not testing {ver} (--only {ONLYVERSION})")
        distro = "epel"
        tmp = self.testdir(testname)
        cover = self.cover()
        script = SCRIPT
        data = F"{tmp}/data"
        repo = F"{tmp}/repo"
        # want = F"{repo}/{distro}.{ver3}"
        want = F"{repo}/{distro}.{epel}"
        os.makedirs(data)
        #
        cmd = F"{cover} {script} {ver} epeldir --datadir={data} --repodir={repo}"
        run = runs(cmd)
        have = run.stdout.strip()
        logg.debug("out: %s", have)
        self.assertEqual(want, have)
        self.assertTrue(os.path.isdir(os.path.join(want, ".")))
        self.assertTrue(os.path.islink(want))
        self.assertIn(data, os.readlink(want))
        #
        # want = F"{repo}/{distro}.{ver3}.alt"
        want = F"{repo}/{distro}.{epel}.alt"
        cmd = F"{cover} {script} {ver} epeldir --datadir={data} --repodir={repo} --variant=alt"
        run = runs(cmd)
        have = run.stdout.strip()
        logg.debug("out: %s", have)
        self.assertEqual(want, have)
        self.assertTrue(os.path.isdir(os.path.join(want, ".")))
        self.assertTrue(os.path.islink(want))
        self.assertIn(data, os.readlink(want))
        #
        # want = os.path.abspath(F"{data}/{distro}.{ver3}.disk/srv/repo")
        want = os.path.abspath(F"{data}/{distro}.{epel}.disk/srv/repo")
        cmd = F"{cover} {script} {ver} epeldiskpath --datadir={data} --repodir={repo}"
        run = runs(cmd)
        have = run.stdout.strip()
        logg.debug("out: %s", have)
        self.assertEqual(want, have)
        #
        # want = os.path.abspath(F"{data}/{distro}.{ver3}.altdisk/srv/repo")
        want = os.path.abspath(F"{data}/{distro}.{epel}.altdisk/srv/repo")
        cmd = F"{cover} {script} {ver} epeldiskpath --datadir={data} --repodir={repo} --variant=alt"
        run = runs(cmd)
        have = run.stdout.strip()
        logg.debug("out: %s", have)
        self.assertEqual(want, have)
        #
        # want = os.path.abspath(F"{data}/{distro}.{ver3}.altdisktmp/srv/repo")
        want = os.path.abspath(F"{data}/{distro}.{epel}.altdisktmp/srv/repo")
        cmd = F"{cover} {script} {ver} epeldiskpath --datadir={data} --repodir={repo} --variant=alt --disksuffix=disktmp"
        run = runs(cmd)
        have = run.stdout.strip()
        logg.debug("out: %s", have)
        self.assertEqual(want, have)
        #
        self.coverage(testname)
        self.rm_testdir(testname)
    def test_73191(self) -> None:
        self.check_sync(self.testname())
    def test_73194(self) -> None:
        self.check_sync(self.testname())
    def check_sync(self, testname: str) -> None:
        _distro, ver = self.testver(testname)
        if ONLYVERSION and ver != ONLYVERSION:
            self.skipTest(F"not testing {ver} (--only {ONLYVERSION})")
        tmp = self.testdir(testname)
        war = "tmp"
        cover = self.cover()
        script = SCRIPT
        data = F"{tmp}/data"
        repo = F"{tmp}/repo"
        os.makedirs(data)
        cmd = F"{cover} {script} {ver} sync {VV} --datadir={data} --repodir={repo} -W {war}"
        if DRY_RSYNC or COVERAGE:
            cmd += " --rsync='rsync --dry-run'"
        ret = calls(cmd)
        self.assertEqual(0, ret)
        self.coverage(testname)
        self.rm_testdir(testname)
    def test_74194(self) -> None:
        self.check_epelsync(self.testname())
    def check_epelsync(self, testname: str) -> None:
        _basedistro, ver = self.testver(testname)
        if ONLYVERSION and ver != ONLYVERSION:
            self.skipTest(F"not testing {ver} (--only {ONLYVERSION})")
        tmp = self.testdir(testname)
        war = "tmp"
        cover = self.cover()
        script = SCRIPT
        data = F"{tmp}/data"
        repo = F"{tmp}/repo"
        os.makedirs(data)
        cmd = F"{cover} {script} {ver} epelsync {VV} --datadir={data} --repodir={repo} -W {war}"
        if DRY_RSYNC or COVERAGE:
            cmd += " --rsync='rsync --dry-run'"
        ret = calls(cmd)
        self.assertEqual(0, ret)
        self.coverage(testname)
        self.rm_testdir(testname)
    def test_75179(self) -> None:
        self.make_repo_test(self.testname())
    def test_75183(self) -> None:
        self.make_repo_test(self.testname())
    def test_75191(self) -> None:
        self.make_repo_test(self.testname())
    def test_75194(self) -> None:
        self.make_repo_test(self.testname())
    def test_76179(self) -> None:
        self.make_repo_test(self.testname(), "--epel")
    def test_76183(self) -> None:
        self.make_repo_test(self.testname(), "--epel")
    def test_76191(self) -> None:
        self.make_repo_test(self.testname(), "--epel")
    def test_76194(self) -> None:
        self.make_repo_test(self.testname(), "--epel")
    def make_repo_test(self, testname: str, addepel: str = NIX) -> None:
        self.rm_container(testname)
        distro, ver = self.testver(testname)
        if ONLYVERSION and ver != ONLYVERSION:
            self.skipTest(F"not testing {ver} (--only {ONLYVERSION})")
        docker = DOCKER
        cover = self.cover()
        script = SCRIPT
        mirror = MIRROR
        pkgrepo = F"{PKGREPO} --nogpgcheck --setopt sslverify=false"
        pkglist = PKGLIST
        distro = DISTRO1
        testcontainer = self.testcontainer(testname)
        imagesrepo = self.testrepo(testname)
        cmd = F"{cover} {script} {ver} baseimage {VV}"
        run = runs(cmd)
        baseimage = run.stdout.strip()
        logg.debug("baseimage %s", baseimage)
        cmd = F"{cover} {script} {ver} pull {VV} --docker='{docker}' --imagesrepo='{imagesrepo}'"
        ret = calls(cmd)
        if not SKIPFULLIMAGE:
            cmd = F"{cover} {script} {ver} repo {VV} --docker='{docker}' --imagesrepo='{imagesrepo}' -vvv"
            ret = calls(cmd)
            self.assertEqual(0, ret)
        if not SKIPFULLIMAGE and addepel:
            cmd = F"{cover} {script} {ver} epelrepo {VV} --docker='{docker}' --imagesrepo='{imagesrepo}' -vvv"
            ret = calls(cmd)
            self.assertEqual(0, ret)
        cmd = F"{cover} {script} list --docker='{docker}' --imagesrepo='{imagesrepo}'"
        ret = calls(cmd)
        self.assertEqual(0, ret)
        cmd = F"{cover} {mirror} start {distro}:{ver} --local {VV} {addepel} --docker='{docker}' --imagesrepo='{imagesrepo}' -C /dev/null"
        ret = calls(cmd)
        self.assertEqual(0, ret)
        cmd = F"{cover} {mirror} addhost {distro}:{ver} --local {VV} {addepel} --docker='{docker}' --imagesrepo='{imagesrepo}' -C /dev/null"
        run = runs(cmd)
        logg.info("show: %s", run.stdout)
        addhost = run.stdout.strip()
        self.assertEqual(0, ret)
        cmd = F"{docker} run -d --name {testcontainer} {addhost} {baseimage} sleep {SLEEP}"
        ret = calls(cmd)
        logg.info("consume: %s", ret)
        self.assertEqual(0, ret)
        cmd = F"{docker} exec {testcontainer} {pkgrepo} clean all"
        ret = calls(cmd)
        logg.info("install clean: %s", ret)
        self.assertEqual(0, ret)
        cmd = F"{docker} exec {testcontainer} {pkgrepo} update"
        ret = calls(cmd)
        logg.info("install refresh: %s", ret)
        python3="python3"
        if ver.startswith("7"):
            python3="python36"
        if TRUE:
            cmd = F"{docker} exec {testcontainer} {pkgrepo} install -y {python3}-lxml"
            ret = calls(cmd)
            logg.info("install package: %s", ret)
            self.assertEqual(0, ret)
            cmd = F"{docker} exec {testcontainer} {pkglist} info {python3}-lxml"
            run = runs(cmd)
            val = run.stdout
            logg.info("install version: %s", val)
            self.assertIn("lxml is a Pythonic", val)
        if addepel:
            cmd = F"{docker} exec {testcontainer} {pkgrepo} install -y epel-release"
            ret = calls(cmd)
            logg.info("install epel-release: %s", ret)
            self.assertEqual(0, ret)
            cmd = F"{docker} exec {testcontainer} {pkgrepo} install -y {python3}-parsedatetime"
            ret = calls(cmd)
            logg.info("install package: %s", ret)
            self.assertEqual(0, ret)
            cmd = F"{docker} exec {testcontainer} {pkglist} info {python3}-parsedatetime"
            run = runs(cmd)
            val = run.stdout
            logg.info("install version: %s", val)
            self.assertIn("parse human-readable date", val)
        #
        cmd = F"{cover} {mirror} stop {distro}:{ver} {VV} {addepel} --docker='{docker}' --imagesrepo='{imagesrepo}' -C /dev/null"
        ret = calls(cmd)
        self.assertEqual(0, ret)
        cmd = F"{docker} image list -q --no-trunc --format '{{{{.Repository}}}}:{{{{.Tag}}}}\t{{{{.Size}}}}'"
        run = runs_(cmd)
        images = []
        for line in run.stdout.splitlines():
            if line.startswith(imagesrepo) and F"{distro}-repo" in line and F":{ver}" in line:
                images += [ "| " + line.rstrip().replace("\t", " | ").replace("mirror-test", "mirror-packages" )]
        logg.info("images:\n%s", "\n".join(images))
        sizesfile = os.path.join(get_CACHE_HOME(), F"{distro}-repo-{ver}.sizes.txt")
        with open(sizesfile, "w") as f:
            print("\n".join(images), file=f)
        logg.debug("written %s", sizesfile)
        self.coverage(testname)
        self.rm_testdir(testname)
        self.rm_container(testname)
        if not KEEPFULLIMAGE:
            self.rm_images(testname)
    def test_77179(self) -> None:
        self.make_disk_test(self.testname())
    def test_77183(self) -> None:
        self.make_disk_test(self.testname())
    def test_77191(self) -> None:
        self.make_disk_test(self.testname())
    def test_77194(self) -> None:
        self.make_disk_test(self.testname())
    def test_78179(self) -> None:
        self.make_disk_test(self.testname(), "--epel")
    def test_78183(self) -> None:
        self.make_disk_test(self.testname(), "--epel")
    def test_78191(self) -> None:
        self.make_disk_test(self.testname(), "--epel")
    def test_78194(self) -> None:
        self.make_disk_test(self.testname(), "--epel")
    def make_disk_test(self, testname: str, addepel: str = NIX) -> None:
        self.rm_container(testname)
        distro, ver = self.testver(testname)
        if ONLYVERSION and ver != ONLYVERSION:
            self.skipTest(F"not testing {ver} (--only {ONLYVERSION})")
        docker = DOCKER
        cover = self.cover()
        script = SCRIPT
        mirror = MIRROR
        pkgrepo = F"{PKGREPO} --nogpgcheck --setopt sslverify=false"
        pkglist = PKGLIST
        testcontainer = self.testcontainer(testname)
        imagesrepo = self.testrepo(testname)
        if TRUE:
            cmd = F"{cover} {script} {ver} base {VV} --imagesrepo={imagesrepo} -vv"
            run = runs(cmd)
            basemade = run.out
            logg.debug("basemade\\%s", run.err)
            logg.info("basemade = %s", basemade)
        if addepel:
            cmd = F"{cover} {script} {ver} epelbase {VV} --imagesrepo={imagesrepo} -vv"
            run = runs(cmd)
            epelbase = run.out
            logg.debug("epelbase\\%s", run.err)
            logg.info("epelbase = %s", epelbase)
        if TRUE:
            cmd = F"{cover} {script} {ver} diskpath {VV} --disksuffix={testname}_disk"
            run = runs(cmd)
            diskpath = run.out
            logg.debug("diskpath = %s", diskpath)
            self.assertIn(testname, diskpath)
            if os.path.isdir(diskpath):
                cmd = F"{cover} {script} {ver} dropdisk {VV} --disksuffix={testname}_disk"
                ret = calls(cmd)
            self.assertFalse(os.path.isdir(diskpath))
            cmd = F"{cover} {script} {ver} disk {VV} --disksuffix={testname}_disk --imagesrepo={imagesrepo}"
            ret = calls(cmd)
            self.assertTrue(os.path.isdir(diskpath))
        if addepel:
            cmd = F"{cover} {script} {ver} epeldiskpath {VV} --disksuffix={testname}_disk"
            run = runs(cmd)
            epeldiskpath = run.out
            logg.debug("epeldiskpath = %s", epeldiskpath)
            self.assertIn(testname, epeldiskpath)
            if os.path.isdir(epeldiskpath):
                cmd = F"{cover} {script} {ver} epeldropdisk {VV} --disksuffix={testname}_disk"
                ret = calls(cmd)
            self.assertFalse(os.path.isdir(epeldiskpath))
            cmd = F"{cover} {script} {ver} epeldisk {VV} --disksuffix={testname}_disk --imagesrepo={imagesrepo}"
            ret = calls(cmd)
            self.assertTrue(os.path.isdir(epeldiskpath))
        cmd = F"{cover} {script} {ver} baserepo {VV} --imagesrepo={imagesrepo}"
        run = runs(cmd)
        baserepo = run.out
        logg.info("baserepo = %s", baserepo)
        cmd = F"{cover} {script} {ver} image {VV} --imagesrepo={imagesrepo}"
        run = runs(cmd)
        image = run.out
        logg.info("image = %s", image)
        if addepel:
            cmd = F"{cover} {script} {ver} epelbaserepo {VV} --imagesrepo={imagesrepo}"
            run = runs(cmd)
            epelbaserepo = run.out
            logg.info("epelbaserepo = %s", epelbaserepo)
            cmd = F"{cover} {script} {ver} epelimage {VV} --imagesrepo={imagesrepo}"
            run = runs(cmd)
            epelimage = run.out
            logg.info("epelimage = %s", epelimage)
        tmp = self.testdir(testname)
        configfile = os.path.join(tmp, "mirror.ini")
        with open(configfile, "w") as cfg:
            print(F"[{image}]", file=cfg)
            print(F"image = {baserepo}", file=cfg)
            print(F"mount = {diskpath}", file=cfg)
            if addepel:
                print(F"[{epelimage}]", file=cfg)
                print(F"image = {epelbaserepo}", file=cfg)
                print(F"mount = {epeldiskpath}", file=cfg)
        calls(F"cat {configfile} | sed -e 's:^:| :'")
        cmd = F"{cover} {mirror} start {distro}:{ver} --local {VV} -vv {addepel} --docker='{docker}' -C {configfile}"
        ret = calls(cmd)
        self.assertEqual(0, ret)
        cmd = F"{cover} {mirror} addhost {distro}:{ver} --local {VV} -vv {addepel} --docker='{docker}' -C {configfile}"
        run = runs(cmd)
        addhost = run.stdout.strip()
        logg.info("addhost = %s", addhost)
        self.assertEqual(0, ret)
        cmd = F"{cover} {script} {ver} baseimage {VV}"
        run = runs(cmd)
        baseimage = run.stdout.strip()
        logg.debug("baseimage = %s", baseimage)
        cmd = F"{docker} run -d --name {testcontainer} {addhost} {baseimage} sleep {SLEEP}"
        ret = calls(cmd)
        logg.info("consume: %s", ret)
        self.assertEqual(0, ret)
        cmd = F"{docker} exec {testcontainer} {pkgrepo} clean all"
        ret = calls(cmd)
        logg.info("install clean: %s", ret)
        self.assertEqual(0, ret)
        cmd = F"{docker} exec {testcontainer} {pkgrepo} update"
        ret = calls(cmd)
        logg.info("install refresh: %s", ret)
        python3="python3"
        if ver.startswith("7"):
            python3="python36"
        if TRUE:
            cmd = F"{docker} exec {testcontainer} {pkgrepo} install -y {python3}-lxml"
            ret = calls(cmd)
            logg.info("install package: %s", ret)
            self.assertEqual(0, ret)
            cmd = F"{docker} exec {testcontainer} {pkglist} info {python3}-lxml"
            run = runs(cmd)
            val = run.out
            logg.info("install version: %s", val)
            self.assertIn("lxml is a Pythonic", val)
        if addepel:
            cmd = F"{docker} exec {testcontainer} {pkgrepo} install -y epel-release"
            ret = calls(cmd)
            logg.info("install epel-release: %s", ret)
            self.assertEqual(0, ret)
            cmd = F"{docker} exec {testcontainer} {pkgrepo} install -y {python3}-parsedatetime"
            ret = calls(cmd)
            logg.info("install package: %s", ret)
            self.assertEqual(0, ret)
            cmd = F"{docker} exec {testcontainer} {pkglist} info {python3}-parsedatetime"
            run = runs(cmd)
            val = run.stdout
            logg.info("install version: %s", val)
            self.assertIn("parse human-readable date", val)
        cmd = F"{cover} {mirror} stop {distro}:{ver} {VV} {addepel} --docker='{docker}' --imagesrepo='{imagesrepo}' -C {configfile}"
        ret = calls(cmd)
        self.assertEqual(0, ret)
        if SAVEBASEDISK:
            cmd = F"{cover} {script} {ver} diskpath {VV}"
            run = runs(cmd)
            savediskpath = run.out
            logg.debug("savediskpath = %s", savediskpath)
            cmd = F"{cover} {script} {ver} baserepo {VV}"
            run = runs(cmd)
            savebaserepo = run.out
            logg.debug("savebaserepo = %s", savebaserepo)
            cmd = F"{docker} rmi -f {savebaserepo}"
            logg.warning("## %s", cmd)
            calls(cmd)
            cmd = F"{docker} tag {baserepo} {savebaserepo}"
            logg.warning("## %s", cmd)
            calls(cmd)
            if os.path.isdir(savediskpath):
                logg.info("rm --tree %s", savediskpath)
                shutil.rmtree(savediskpath)
            parentpath = os.path.dirname(savediskpath)
            if not os.path.isdir(parentpath):
                logg.info("mkdir -p %s", parentpath)
                os.makedirs(parentpath)
            cmd = F"mv '{diskpath}' '{savediskpath}'"
            logg.warning("## %s", cmd)
            calls(cmd)
            cache = get_CACHE_HOME()
            cachefile = os.path.join(cache, F"docker_mirror.{distro}.{ver}.ini")
            with open(cachefile, "w") as cfg:
                today = Time.now().isoformat('.')
                print("", file=cfg)
                print(F"# {testname} {today}")
                print(F"[{image}]", file=cfg)
                print(F"image = {savebaserepo}", file=cfg)
                print(F"mount = {savediskpath}", file=cfg)
            logg.warning("written %s", cachefile)
            if addepel:
                cmd = F"{cover} {script} {ver} epeldiskpath {VV}"
                run = runs(cmd)
                saveepeldiskpath = run.out
                logg.debug("saveepeldiskpath = %s", saveepeldiskpath)
                cmd = F"{cover} {script} {ver} epelbaserepo {VV}"
                run = runs(cmd)
                saveepelbaserepo = run.out
                logg.debug("saveepelbaserepo = %s", saveepelbaserepo)
                cmd = F"{docker} rmi -f {saveepelbaserepo}"
                logg.warning("## %s", cmd)
                calls(cmd)
                cmd = F"{docker} tag {epelbaserepo} {saveepelbaserepo}"
                logg.warning("## %s", cmd)
                calls(cmd)
                if os.path.isdir(saveepeldiskpath):
                    logg.info("rm --tree %s", saveepeldiskpath)
                    shutil.rmtree(saveepeldiskpath)
                parentpath = os.path.dirname(saveepeldiskpath)
                if not os.path.isdir(parentpath):
                    logg.info("mkdir -p %s", parentpath)
                    os.makedirs(parentpath)
                cmd = F"mv '{epeldiskpath}' '{saveepeldiskpath}'"
                logg.warning("## %s", cmd)
                calls(cmd)
                cachefile = os.path.join(cache, F"docker_mirror.epel.{ver}.ini")
                with open(cachefile, "w") as cfg:
                    print("", file=cfg)
                    print(F"# {testname} {today}")
                    print(F"[{epelimage}]", file=cfg)
                    print(F"image = {saveepelbaserepo}", file=cfg)
                    print(F"mount = {saveepeldiskpath}", file=cfg)
                logg.warning("written %s", cachefile)
        #
        if os.path.isdir(diskpath) and not KEEPFULLIMAGE:
            cmd = F"{cover} {script} {ver} dropdisk {VV} --docker='{docker}' --imagesrepo='{imagesrepo}' --disksuffix={testname}_"
            ret = calls(cmd)
        self.coverage(testname)
        self.rm_testdir(testname)
        self.rm_container(testname)
        if not KEEPFULLIMAGE:
            self.rm_images(testname)
    def make_disk_cleanup(self) -> None:
        cache = get_CACHE_HOME()
        if SAVEBASEDISK:
            for distro in [DISTRO1, DISTRO2, "epel"]:
                cachefiles = glob(os.path.join(cache, F"docker_mirror.{distro}.*.ini"))
                for cachefile in cachefiles:
                    logg.info(" rm %s", cachefile)
                    os.unlink(cachefile)
    def test_79999(self) -> None:
        if COVERAGE:
            o1 = sh(F" {PYTHON} -m coverage combine")
            o2 = sh(F" {PYTHON} -m coverage report {SCRIPT}")
            o3 = sh(F" {PYTHON} -m coverage annotate  {SCRIPT}")
            logg.log(DONE,"COVERAGE:\n%s\n%s\n%s", o1, o2, o3)

if __name__ == "__main__":
    # unittest.main()
    from optparse import OptionParser # pylint: disable=deprecated-module
    cmdline = OptionParser("%s test...")
    cmdline.add_option("-v", "--verbose", action="count", default=0, help="more verbose logging")
    cmdline.add_option("-^", "--quiet", action="count", default=0, help="less verbose logging")
    cmdline.add_option("->", "--script", metavar="PY", default=SCRIPT, help="different path to [%default]")
    cmdline.add_option("-M", "--mirror", metavar="PY", default=MIRROR, help="different path to [%default]")
    cmdline.add_option("-D", "--docker", metavar="EXE", default=DOCKER, help="alternative to [%default] (e.g. podman)")
    cmdline.add_option("-P", "--python", metavar="EXE", default=PYTHON, help="alternative to [%default] (=python3.11)")
    cmdline.add_option("-k", "--keep", action="count", default=0, help="keep testdir")
    cmdline.add_option("--dry-rsync", action="count", default=DRY_RSYNC, help="upstream rsync --dry-run [%default]")
    cmdline.add_option("--real-rsync", action="count", default=0, help="upstream rsync for real [%default]")
    cmdline.add_option("--sleep", metavar="SEC", default=SLEEP)
    cmdline.add_option("-B", "--savebasedisk", action="count", default=0, help="rename */base image and test *.disk repo")
    cmdline.add_option("-S", "--skipfullimage", action="count", default=0, help="upstream rsync for real [%default]")
    cmdline.add_option("-K", "--keepfullimage", action="count", default=0, help="upstream rsync for real [%default]")
    cmdline.add_option("--keepbaseimage", action="count", default=0, help="upstream rsync for real [%default]")
    cmdline.add_option("--only", metavar="VER", default=ONLYVERSION, help="run tests only of that version")
    cmdline.add_option("--coverage", action="store_true", default=False,
                       help="Generate coverage data. [%default]")
    cmdline.add_option("--failfast", action="store_true", default=False,
                       help="Stop the test run on the first error or failure. [%default]")
    cmdline.add_option("--xmlresults", metavar="FILE", default=None,
                       help="capture results as a junit xml file [%default]")
    opt, _args = cmdline.parse_args()
    logging.basicConfig(level=max(0, logging.WARNING - 10 * opt.verbose + 10 * opt.quiet))
    DOCKER = opt.docker
    PYTHON = opt.python
    SCRIPT = opt.script
    MIRROR = opt.mirror
    KEEP = opt.keep
    SLEEP = int(opt.sleep)
    ONLYVERSION = opt.only
    COVERAGE = opt.coverage
    DRY_RSYNC = opt.dry_rsync - opt.real_rsync
    SAVEBASEDISK = opt.savebasedisk
    SKIPFULLIMAGE = opt.skipfullimage
    KEEPFULLIMAGE = opt.keepfullimage
    KEEPBASEIMAGE = opt.keepbaseimage
    if opt.verbose:
        VV= "-" + "v" * int(opt.verbose)
    if not _args:
        _args = ["test_*"]
    suite = unittest.TestSuite()
    for arg in _args:
        if len(arg) > 2 and arg[0].isalpha() and arg[1] == "_":
            arg = "test_" + arg[2:]
        for classname in sorted(globals()):
            if not classname.endswith("Test"):
                continue
            testclass = globals()[classname]
            for method in sorted(dir(testclass)):
                if "*" not in arg: arg += "*"
                if arg.startswith("_"): arg = arg[1:]
                if fnmatch(method, arg):
                    suite.addTest(testclass(method))
    # running
    xmlresults = None
    if opt.xmlresults:
        if os.path.exists(opt.xmlresults):
            os.remove(opt.xmlresults)
        xmlresults = open(opt.xmlresults, "wb")
    if xmlresults:
        import xmlrunner  # type: ignore[import], pylint: disable=import-error
        Runner = xmlrunner.XMLTestRunner
        result = Runner(xmlresults).run(suite)
        logg.info(" XML reports written to %s", opt.xmlresults)
    else:
        Runner = unittest.TextTestRunner
        result = Runner(verbosity=opt.verbose, failfast=opt.failfast).run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
