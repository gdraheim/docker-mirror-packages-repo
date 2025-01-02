#! /usr/bin/env python3
__copyright__ = "(C) 2024 Guido Draheim"
__contact__ = "https://github.com/gdraheim/docker-mirror-packages-repo"
__license__ = "CC0 Creative Commons Zero (Public Domain)"
__version__ = "1.7.6334"

# pylint: disable=unused-import,line-too-long
from typing import Optional, Union, Dict, List, Any, Sequence, Callable, Iterable, cast, NamedTuple
import shutil
import inspect
import unittest
import sys
import os
import re
import time
from fnmatch import fnmatchcase as fnmatch
from subprocess import getoutput, Popen, PIPE, call, CalledProcessError

import logging
logg = logging.getLogger("tests.opensuse")
DONE = (logging.ERROR + logging.WARNING)//2
logging.addLevelName(DONE, "DONE")
NIX = ""
LIST: List[str] = []

PYTHON = "python3"
SCRIPT = "opensuse-docker-mirror.py"
MIRROR = "docker_mirror.py"
COVERAGE = False
KEEP = False
DRY_RSYNC = 1
DOCKER = "docker"
VV="-v"
SKIPFULLIMAGE = True
KEEPFULLIMAGE = False
KEEPBASEIMAGE = False

def sh(cmd: str, **args: Any) -> str:
    logg.debug("sh %s", cmd)
    return getoutput(cmd, **args)
class CompletedProc(NamedTuple):
    """ aligned with subprocess.CompletedProcess (Python 3.5) """
    stdout: str
    stderr: str
    ret: int
    @property
    def returncode(self) -> int:
        return self.ret
    def check_returncode(self) -> None:
        if self.returncode != 0:
            raise CalledProcessError(returncode=self.returncode, cmd = [], output=self.stdout, stderr=self.stderr)
def runs(cmd: str, **args: Any) -> CompletedProc:
    """ subprocess.run() defaults to shell=False (Python 3.5) and capture_output=False (Python 3.7)"""
    logg.debug("run: %s", cmd)
    return runs_(cmd, **args)
def runs_(cmd: str, **args: Any) -> CompletedProc:
    if isinstance(cmd, str):
        proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, **args)
    else:
        proc = Popen(cmd, shell=False, stdout=PIPE, stderr=PIPE, **args)
    out, err = proc.communicate()
    return CompletedProc(decodes(out), decodes(err), proc.returncode)
def calls(cmd: str, **args: Any) -> int:
    """ subprocess.call() defaults to shell=False"""
    logg.debug("run: %s", cmd)
    return calls_(cmd, **args)
def calls_(cmd: str, **args: Any) -> int:
    if isinstance(cmd, str):
        return call(cmd, shell=True, **args)
    else:
        return call(cmd, shell=False, **args)
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

def get_caller_name() -> str:
    frame = inspect.currentframe().f_back.f_back  # type: ignore
    return frame.f_code.co_name  # type: ignore
def get_caller_caller_name() -> str:
    frame = inspect.currentframe().f_back.f_back.f_back  # type: ignore
    return frame.f_code.co_name  # type: ignore

class OpensuseMirrorTest(unittest.TestCase):
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
        if os.path.isfile(".coverage"):
            # shutil.copy(".coverage", newcoverage)
            f = open(".coverage", "rb")
            text = f.read()
            f.close()
            text2 = re.sub(rb"(\]\}\})[^{}]*(\]\}\})$", rb"\1", text)
            f = open(newcoverage, "wb")
            f.write(text2)
            f.close()
    def cover(self) -> str:
        python = PYTHON
        cover = F"{python} -m coverage run" if COVERAGE else python
        return cover
    def testver(self, testname: str = NIX) -> None:
        testname = testname or self.caller_testname()
        ver3 = testname[-3:]
        if ver3.startswith("14"):
            return "42" + "." + ver3[2]
        return ver3[0:2] + "." + ver3[2]
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
        return "localhost:5000/mirror-test"
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
    def test_50100(self) -> None:
        cover = self.cover()
        script = SCRIPT
        cmd = F"{cover} {script} --help"
        out = sh(cmd)
        logg.debug("out: %s", out)
        self.assertIn("imagesrepo=PREFIX", out)
        self.coverage()
    def test_50101(self) -> None:
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
    def test_50110(self) -> None:
        cover = self.cover()
        script = SCRIPT
        cmd = F"{cover} {script} datadir"
        out = sh(cmd)
        logg.debug("out: %s", out)
        self.coverage()
    def test_50111(self) -> None:
        cover = self.cover()
        script = SCRIPT
        cmd = F"{cover} {script} scripts"
        out = sh(cmd)
        logg.debug("out: %s", out)
        self.assertEqual("./scripts", out.strip())
        self.coverage()
    def test_50132(self) -> None:
        ver = self.testver()
        self.assertEqual(ver, "13.2")
        cover = self.cover()
        script = SCRIPT
        cmd = F"{cover} {script} {ver} version"
        run = runs(cmd)
        have = run.stdout.strip()
        errs = run.stderr.strip()
        logg.debug("out: %s", run.stdout)
        self.assertEqual(ver, have)
        self.assertEqual("", errs)
        self.coverage()
    def test_50140(self) -> None:
        ver = self.testver()
        self.assertEqual(ver, "42.0")
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
    def test_50142(self) -> None:
        ver = self.testver()
        self.assertEqual(ver, "42.2")
        cover = self.cover()
        script = SCRIPT
        cmd = F"{cover} {script} {ver} version"
        run = runs(cmd)
        have = run.stdout.strip()
        errs = run.stderr.strip()
        logg.debug("out: %s", have)
        self.assertEqual(ver, have)
        self.assertEqual("", errs)
        self.coverage()
    def test_50143(self) -> None:
        ver = self.testver()
        self.assertEqual(ver, "42.3")
        cover = self.cover()
        script = SCRIPT
        cmd = F"{cover} {script} {ver} version"
        run = runs(cmd)
        have = run.stdout.strip()
        errs = run.stderr.strip()
        logg.debug("out: %s", have)
        self.assertEqual(ver, have)
        self.assertEqual("", errs)
        self.coverage()
    def test_50151(self) -> None:
        ver = self.testver()
        self.assertEqual(ver, "15.1")
        cover = self.cover()
        script = SCRIPT
        cmd = F"{cover} {script} {ver} version"
        run = runs(cmd)
        have = run.stdout.strip()
        errs = run.stderr.strip()
        logg.debug("out: %s", have)
        self.assertEqual(ver, have)
        self.assertEqual("", errs)
        self.coverage()
    def test_50152(self) -> None:
        ver = self.testver()
        self.assertEqual(ver, "15.2")
        cover = self.cover()
        script = SCRIPT
        cmd = F"{cover} {script} {ver} version"
        run = runs(cmd)
        have = run.stdout.strip()
        errs = run.stderr.strip()
        logg.debug("out: %s", have)
        self.assertEqual(ver, have)
        self.assertEqual("", errs)
        self.coverage()
    def test_50153(self) -> None:
        ver = self.testver()
        self.assertEqual(ver, "15.3")
        cover = self.cover()
        script = SCRIPT
        cmd = F"{cover} {script} {ver} version"
        run = runs(cmd)
        have = run.stdout.strip()
        errs = run.stderr.strip()
        logg.debug("out: %s", have)
        self.assertEqual(ver, have)
        self.assertEqual("", errs)
        self.coverage()
    def test_50154(self) -> None:
        ver = self.testver()
        self.assertEqual(ver, "15.4")
        cover = self.cover()
        script = SCRIPT
        cmd = F"{cover} {script} {ver} version"
        run = runs(cmd)
        have = run.stdout.strip()
        errs = run.stderr.strip()
        logg.debug("out: %s", have)
        self.assertEqual(ver, have)
        self.assertEqual("", errs)
        self.coverage()
    def test_50155(self) -> None:
        ver = self.testver()
        self.assertEqual(ver, "15.5")
        cover = self.cover()
        script = SCRIPT
        cmd = F"{cover} {script} {ver} version"
        run = runs(cmd)
        have = run.stdout.strip()
        errs = run.stderr.strip()
        logg.debug("out: %s", have)
        self.assertEqual(ver, have)
        self.assertEqual("", errs)
        self.coverage()
    def test_50156(self) -> None:
        ver = self.testver()
        self.assertEqual(ver, "15.6")
        cover = self.cover()
        script = SCRIPT
        cmd = F"{cover} {script} {ver} version"
        run = runs(cmd)
        have = run.stdout.strip()
        errs = run.stderr.strip()
        logg.debug("out: %s", have)
        self.assertEqual(ver, have)
        self.assertEqual("", errs)
        self.coverage()
    def test_50159(self) -> None:
        ver = self.testver()
        self.assertEqual(ver, "15.9")
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
    def test_50160(self) -> None:
        ver = self.testver()
        self.assertEqual(ver, "16.0")
        cover = self.cover()
        script = SCRIPT
        cmd = F"{cover} {script} {ver} version"
        run = runs(cmd)
        have = run.stdout.strip()
        errs = run.stderr.strip()
        logg.debug("out: %s", have)
        self.assertEqual(ver, have)
        self.assertEqual("", errs)
        self.coverage()
    def test_50193(self) -> None:
        ver2 = "13"
        ver = "13.2"
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
    def test_50195(self) -> None:
        ver2 = "15"
        ver = "15.6"
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
    def test_50196(self) -> None:
        ver2 = "16"
        ver = "16.0"
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
    def test_50200(self) -> None:
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
    def test_51001(self) -> None:
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
    def test_51002(self) -> None:
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
    def test_51003(self) -> None:
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
    def test_51132(self) -> None:
        ver = self.testver()
        tmp = self.testdir()
        cover = self.cover()
        script = SCRIPT
        data = F"{tmp}/data"
        repo = F"{tmp}/repo"
        want = F"{repo}/opensuse.{ver}"
        os.makedirs(data)
        cmd = F"{cover} {script} {ver} dir --datadir={data} --repodir={repo}"
        run = runs(cmd)
        have = run.stdout.strip()
        logg.debug("out: %s", have)
        self.assertEqual(want, have)
        self.assertTrue(os.path.isdir(os.path.join(want, ".")))
        self.assertTrue(os.path.islink(want))
        self.assertIn(data, os.readlink(want))
        self.coverage()
        self.rm_testdir()
    def test_51142(self) -> None:
        ver = self.testver()
        tmp = self.testdir()
        cover = self.cover()
        script = SCRIPT
        data = F"{tmp}/data"
        repo = F"{tmp}/repo"
        want = F"{repo}/opensuse.{ver}"
        os.makedirs(data)
        cmd = F"{cover} {script} {ver} dir --datadir={data} --repodir={repo}"
        run = runs(cmd)
        have = run.stdout.strip()
        logg.debug("out: %s", have)
        self.assertEqual(want, have)
        self.assertTrue(os.path.isdir(os.path.join(want, ".")))
        self.assertTrue(os.path.islink(want))
        self.assertIn(data, os.readlink(want))
        self.coverage()
        self.rm_testdir()
    def test_51153(self) -> None:
        ver = self.testver()
        tmp = self.testdir()
        cover = self.cover()
        script = SCRIPT
        data = F"{tmp}/data"
        repo = F"{tmp}/repo"
        want = F"{repo}/opensuse.{ver}"
        os.makedirs(data)
        cmd = F"{cover} {script} {ver} dir --datadir={data} --repodir={repo}"
        run = runs(cmd)
        have = run.stdout.strip()
        logg.debug("out: %s", have)
        self.assertEqual(want, have)
        self.assertTrue(os.path.isdir(os.path.join(want, ".")))
        self.assertTrue(os.path.islink(want))
        self.assertIn(data, os.readlink(want))
        self.coverage()
        self.rm_testdir()
    def test_51160(self) -> None:
        ver = self.testver()
        tmp = self.testdir()
        cover = self.cover()
        script = SCRIPT
        data = F"{tmp}/data"
        repo = F"{tmp}/repo"
        want = F"{repo}/opensuse.{ver}"
        os.makedirs(data)
        cmd = F"{cover} {script} {ver} dir --datadir={data} --repodir={repo}"
        run = runs(cmd)
        have = run.stdout.strip()
        logg.debug("out: %s", have)
        self.assertEqual(want, have)
        self.assertTrue(os.path.isdir(os.path.join(want, ".")))
        self.assertTrue(os.path.islink(want))
        self.assertIn(data, os.readlink(want))
        self.coverage()
        self.rm_testdir()
    def test_52160(self) -> None:
        war = "disk"
        ver = self.testver()
        tmp = self.testdir()
        cover = self.cover()
        script = SCRIPT
        data = F"{tmp}/data"
        repo = F"{tmp}/repo"
        want = F"{repo}/opensuse.{ver}.{war}"
        os.makedirs(data)
        cmd = F"{cover} {script} {ver} dir --datadir={data} --repodir={repo} -W {war}"
        run = runs(cmd)
        have = run.stdout.strip()
        logg.debug("out: %s", have)
        self.assertEqual(want, have)
        self.assertTrue(os.path.isdir(os.path.join(want, ".")))
        self.assertTrue(os.path.islink(want))
        self.assertIn(data, os.readlink(want))
        self.coverage()
        self.rm_testdir()
    def test_53156(self) -> None:
        war = "tmp"
        ver = self.testver()
        tmp = self.testdir()
        cover = self.cover()
        script = SCRIPT
        data = F"{tmp}/data"
        repo = F"{tmp}/repo"
        os.makedirs(data)
        cmd = F"{cover} {script} {ver} sync {VV} --datadir={data} --repodir={repo} -W {war}"
        if DRY_RSYNC:
            cmd += " --rsync='rsync --dry-run'"
        ret = calls(cmd)
        self.assertEqual(0, ret)
        self.coverage()
        self.rm_testdir()
    def test_53160(self) -> None:
        war = "tmp"
        ver = self.testver()
        tmp = self.testdir()
        cover = self.cover()
        script = SCRIPT
        data = F"{tmp}/data"
        repo = F"{tmp}/repo"
        os.makedirs(data)
        cmd = F"{cover} {script} {ver} sync {VV} --datadir={data} --repodir={repo} -W {war}"
        if DRY_RSYNC:
            cmd += " --rsync='rsync --dry-run'"
        ret = calls(cmd)
        self.assertEqual(0, ret)
        self.coverage()
        self.rm_testdir()
    def test_54156(self) -> None:
        self.check_54(self.testname())
    def check_54(self, testname: str) -> None:
        self.rm_container(testname)
        ver = self.testver(testname)
        docker = DOCKER
        cover = self.cover()
        script = SCRIPT
        mirror = MIRROR
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
        cmd = F"{cover} {mirror} start opensuse:{ver} {VV} --docker='{docker}' --imagesrepo='{imagesrepo}' -C /dev/null"
        ret = calls(cmd)
        self.assertEqual(0, ret)
        cmd = F"{cover} {mirror} addhost opensuse:{ver} {VV} --docker='{docker}' --imagesrepo='{imagesrepo}' -C /dev/null"
        run = runs(cmd)
        logg.info("show: %s", run.stdout)
        addhost = run.stdout.strip()
        self.assertEqual(0, ret)
        cmd = F"{docker} run -d --name {testcontainer} {addhost} {baseimage} sleep 33"
        ret = calls(cmd)
        logg.info("consume: %s", ret)
        self.assertEqual(0, ret)
        cmd = F"{docker} exec {testcontainer} zypper mr --no-gpgcheck --all"
        ret = calls(cmd)
        logg.info("install nocheck: %s", ret)
        cmd = F"{docker} exec {testcontainer} zypper clean --all"
        ret = calls(cmd)
        logg.info("install clean: %s", ret)
        self.assertEqual(0, ret)
        cmd = F"{docker} exec {testcontainer} zypper install -y python3-lxml"
        ret = calls(cmd)
        logg.info("install package: %s", ret)
        self.assertEqual(0, ret)
        cmd = F"{cover} {mirror} stop opensuse:{ver} {VV} --docker='{docker}' --imagesrepo='{imagesrepo}' -C /dev/null"
        ret = calls(cmd)
        self.assertEqual(0, ret)
        cmd = F"{docker} exec {testcontainer} rpm -q --info python3-lxml"
        run = runs(cmd)
        val = run.stdout
        logg.info("install version: %s", val)
        self.assertIn("Pythonic XML", val)
        self.coverage(testname)
        self.rm_testdir(testname)
        self.rm_container(testname)
        if not KEEPFULLIMAGE:
            self.rm_images(testname)
    def test_54160(self) -> None:
        ver = self.testver()
        docker = DOCKER
        cover = self.cover()
        script = SCRIPT
        imagesrepo = self.testrepo()
        cmd = F"{cover} {script} {ver} pull {VV} --docker='{docker}' --imagesrepo='{imagesrepo}'"
        ret = calls(cmd)
        if not SKIPFULLIMAGE:
            cmd = F"{cover} {script} {ver} repo {VV} --docker='{docker}' --imagesrepo='{imagesrepo}'"
            ret = calls(cmd)
            self.assertEqual(0, ret)
        self.coverage()
        self.rm_testdir()
        if not KEEPFULLIMAGE:
            self.rm_images()
    def test_59999(self) -> None:
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
    cmdline.add_option("-k", "--keep", action="count", default=0, help="keep testdir")
    cmdline.add_option("-D", "--docker", metavar="EXE", default=DOCKER, help="use different docker/podman [%default]")
    cmdline.add_option("--dry-rsync", action="count", default=DRY_RSYNC, help="upstream rsync --dry-run [%default]")
    cmdline.add_option("--real-rsync", action="count", default=0, help="upstream rsync for real [%default]")
    cmdline.add_option("-S", "--skipfullimage", action="count", default=0, help="upstream rsync for real [%default]")
    cmdline.add_option("-K", "--keepfullimage", action="count", default=0, help="upstream rsync for real [%default]")
    cmdline.add_option("--keepbaseimage", action="count", default=0, help="upstream rsync for real [%default]")
    cmdline.add_option("--coverage", action="store_true", default=False,
                       help="Generate coverage data. [%default]")
    cmdline.add_option("--failfast", action="store_true", default=False,
                       help="Stop the test run on the first error or failure. [%default]")
    cmdline.add_option("--xmlresults", metavar="FILE", default=None,
                       help="capture results as a junit xml file [%default]")
    opt, _args = cmdline.parse_args()
    logging.basicConfig(level=max(0, logging.WARNING - 10 * opt.verbose + 10 * opt.quiet))
    KEEP = opt.keep
    COVERAGE = opt.coverage
    DRY_RSYNC = opt.dry_rsync - opt.real_rsync
    DOCKER = opt.docker
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
