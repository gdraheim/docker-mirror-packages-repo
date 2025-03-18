#! /usr/bin/python3
# pylint: disable=possibly-unused-variable,unused-variable,line-too-long
""" checking easy build with the local docker mirror packages repos """

from typing import Union, Optional, List, Mapping, Iterable, Iterator, TextIO
import unittest
import sys
import os
import re
import subprocess
import inspect
from fnmatch import fnmatchcase as fnmatch
import logging

logg = logging.getLogger("TEST")
NIX = ""
OK = True

DOCKERDEF = os.environ.get("DOCKER_EXE", os.environ.get("DOCKER_BIN", "docker"))
PYTHONDEF = os.environ.get("DOCKER_PYTHON", os.environ.get("DOCKER_PYTHON3", "python3"))
MIRRORDEF = os.environ.get("DOCKER_MIRROR_PY", os.environ.get("DOCKER_MIRROR",  "docker_mirror.py"))
DOCKER = DOCKERDEF
PYTHON = PYTHONDEF
MIRROR = MIRRORDEF
SCRIPT = "docker_image.py"
IMAGES = "docker-local"
LOCAL = 0

string_types = str
xrange = range

def make_file(name: str, content: str) -> None:
    with open(name, "w") as f:
        f.write(content)
def drop_file(name: str) -> None:
    if os.path.exists(name):
        os.remove(name)

def decodes(text: Union[str, bytes]) -> str:
    if text is None: return None
    if isinstance(text, bytes):
        encoded = sys.getdefaultencoding()
        if encoded in ["ascii"]:
            encoded = "utf-8"
        try:
            return text.decode(encoded)
        except UnicodeDecodeError:
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

class CalledProcessError(subprocess.SubprocessError):
    def __init__(self, args: Union[str, List[str]], returncode: int = 0,
        stdout: Union[str,bytes] = NIX, stderr: Union[str,bytes] = NIX) -> None:
        self.cmd = args
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.output = self.stdout
class CompletedProcess:
    def __init__(self, args: Union[str, List[str]], returncode: int = 0,
        stdout: Union[str,bytes] = NIX, stderr: Union[str,bytes] = NIX) -> None:
        self.args = args
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
    def check_returncode(self) -> None:
        if self.returncode:
            raise CalledProcessError(self.args, self.returncode, self.stdout, self.stderr)
    @property
    def err(self) -> str:
        return decodes(self.stderr).rstrip()
    @property
    def out(self) -> str:
        return decodes(self.stdout).rstrip()

def X(args: Union[str, List[str]], stdin: Optional[int]=None, inputs: Optional[bytes]=None,
    stdout: Optional[int]=None, stderr: Optional[int]=None,
    shell: Optional[bool]=None, cwd: Optional[str]=None, timeout: Optional[int]=None,
    check: bool=False, env: Optional[Mapping[bytes, str]]=None) -> CompletedProcess:
    """ a variant of subprocess.run() """
    shell = isinstance(args, str) if shell is None else shell
    stdout = subprocess.PIPE if stdout is None else stdout
    stderr = subprocess.PIPE if stderr is None else stderr
    proc = subprocess.Popen(args, stdin=stdin, stdout=stdout, stderr=stderr, shell=shell, cwd=cwd, env=env)
    try:
        outs, errs = proc.communicate(input=inputs, timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()
    completed = CompletedProcess(args, proc.returncode, outs, errs)
    if check:
        completed.check_returncode()
    return completed


def get_caller_name() -> str:
    currentframe = inspect.currentframe()
    if not currentframe:
        return "global"
    if not currentframe.f_back:
        frame = currentframe
    elif not currentframe.f_back.f_back:
        frame = currentframe.f_back
    else:
        frame = currentframe.f_back.f_back
    return frame.f_code.co_name
def get_caller_caller_name() -> str:
    currentframe = inspect.currentframe()
    if not currentframe:
        return "global"
    if not currentframe.f_back:
        frame = currentframe
    elif not currentframe.f_back.f_back:
        frame = currentframe.f_back
    elif not currentframe.f_back.f_back.f_back:
        frame = currentframe.f_back.f_back
    else:
        frame = currentframe.f_back.f_back.f_back
    return frame.f_code.co_name

def _lines4(textlines: Union[str, List[str], Iterator[str], TextIO]) -> List[str]:
    if isinstance(textlines, string_types):
        linelist = decodes(textlines).split("\n")
        if len(linelist) and linelist[-1] == "":
            linelist = linelist[:-1]
        return linelist
    return list(textlines)
def lines4(textlines: Union[str, List[str], Iterator[str], TextIO]) -> List[str]:
    linelist = []
    for line in _lines4(textlines):
        linelist.append(line.rstrip())
    return linelist
def each_grep(patterns: Iterable[str], textlines: Union[str, List[str], TextIO]) -> Iterator[str]:
    for line in _lines4(textlines):
        for pattern in patterns:
            if re.search(pattern, line.rstrip()):
                yield line.rstrip()
def grep(pattern: str, textlines: Union[str, List[str], TextIO]) -> List[str]:
    return list(each_grep([pattern], textlines))
def greps(textlines: Union[str, List[str], TextIO], *pattern: str) -> List[str]:
    return list(each_grep(pattern, textlines))

class DockerLocalImageTest(unittest.TestCase):
    def caller_testname(self) -> str:
        name = get_caller_caller_name()
        x1 = name.find("_")
        if x1 < 0: return name
        x2 = name.find("_", x1 + 1)
        if x2 < 0: return name
        return name[:x2]
    def testname(self, suffix: Optional[str] = None) -> str:
        name = self.caller_testname()
        if suffix:
            return name + "_" + suffix
        return name
    def testver(self, testname: str = NIX) -> None:
        testname = testname or self.caller_testname()
        ver3 = testname[-3:]
        if ver3.startswith("0"):
            return ver3[1] + "." + ver3[2]
        if ver3.startswith("14"):
            return "42" + "." + ver3[2]
        if ver3.startswith("2"):
            num = ver3[2]
            if num == "4":
                return ver3[0:2] + ".04"
            if num == "9":
                return ver3[0:2] + ".10"
        return ver3[0:2] + "." + ver3[2]
    def test_90001_hello(self) -> None:
        print("... starting the testsuite ...")
        logg.info("starting the testsuite ...")
    def test_91094(self) -> None:
        """ almalinux has python3 and python3.11 """
        python = PYTHON
        script = SCRIPT if not LOCAL else F"{SCRIPT} --local"
        docker = DOCKER
        images = IMAGES
        testname = self.testname()
        version = self.testver()
        sh____(F"{python} {script} FROM almalinux:{version} INTO {images}/{testname}:{version} SEARCH setuptools -vvv")
        x1 = X(F"{docker} inspect {images}/{testname}:{version}")
        self.assertTrue(greps(x1.out, "RepoTags"))
        sh____(F"{docker} rm -f {images}/{testname}:{version}")
    def test_91099(self) -> None:
        """ almalinux has python3 and python3.11 """
        python = PYTHON
        script = SCRIPT if not LOCAL else F"{SCRIPT} --local"
        docker = DOCKER
        images = IMAGES
        testname = self.testname()
        version = "9.4" # self.testver() # !!!!!
        sh____(F"{python} {script} --epel FROM almalinux:{version} INTO {images}/{testname}:{version} INSTALL epel-release SEARCH setuptools -vvv")
        x1 = X(F"{docker} inspect {images}/{testname}:{version}")
        self.assertTrue(greps(x1.out, "RepoTags"))
        sh____(F"{docker} rm -f {images}/{testname}:{version}")
    def test_91154(self) -> None:
        python = PYTHON
        script = SCRIPT if not LOCAL else F"{SCRIPT} --local"
        docker = DOCKER
        images = IMAGES
        testname = self.testname()
        version = self.testver()
        sh____(F"{python} {script} FROM opensuse/leap:{version} INTO {images}/{testname}:{version} SEARCH setuptools -vvv")
        x1 = X(F"{docker} inspect {images}/{testname}:{version}")
        self.assertTrue(greps(x1.out, "RepoTags"))
        sh____(F"{docker} rm -f {images}/{testname}:{version}")
    def test_91155(self) -> None:
        python = PYTHON
        script = SCRIPT if not LOCAL else F"{SCRIPT} --local"
        docker = DOCKER
        images = IMAGES
        testname = self.testname()
        version = self.testver()
        sh____(F"{python} {script} FROM opensuse/leap:{version} INTO {images}/{testname}:{version} SEARCH setuptools -vvv")
        x1 = X(F"{docker} inspect {images}/{testname}:{version}")
        self.assertTrue(greps(x1.out, "RepoTags"))
        sh____(F"{docker} rm -f {images}/{testname}:{version}")
    def test_91156(self) -> None:
        python = PYTHON
        script = SCRIPT if not LOCAL else F"{SCRIPT} --local"
        docker = DOCKER
        images = IMAGES
        testname = self.testname()
        version = self.testver()
        sh____(F"{python} {script} FROM opensuse/leap:{version} INTO {images}/{testname}:{version} SEARCH setuptools -vvv")
        x1 = X(F"{docker} inspect {images}/{testname}:{version}")
        self.assertTrue(greps(x1.out, "RepoTags"))
        sh____(F"{docker} rm -f {images}/{testname}:{version}")
    def test_91224(self) -> None:
        python = PYTHON
        script = SCRIPT if not LOCAL else F"{SCRIPT} --local"
        docker = DOCKER
        images = IMAGES
        testname = self.testname()
        version = self.testver()
        sh____(F"{python} {script} FROM ubuntu:{version} INTO {images}/{testname}:{version} SEARCH setuptools -vvv")
        x1 = X(F"{docker} inspect {images}/{testname}:{version}")
        self.assertTrue(greps(x1.out, "RepoTags"))
        sh____(F"{docker} rm -f {images}/{testname}:{version}")
    def test_91244(self) -> None:
        python = PYTHON
        script = SCRIPT if not LOCAL else F"{SCRIPT} --local"
        docker = DOCKER
        images = IMAGES
        testname = self.testname()
        version = self.testver()
        sh____(F"{python} {script} FROM ubuntu:{version} INTO {images}/{testname}:{version} SEARCH setuptools -vvv")
        x1 = X(F"{docker} inspect {images}/{testname}:{version}")
        self.assertTrue(greps(x1.out, "RepoTags"))
        sh____(F"{docker} rm -f {images}/{testname}:{version}")
    def test_92094(self) -> None:
        """ almalinux does not have it - but python3-mypy is on EPEL"""
        python = PYTHON
        script = SCRIPT if not LOCAL else F"{SCRIPT} --local --epel"
        docker = DOCKER
        images = IMAGES
        testname = self.testname()
        version = self.testver()
        sh____(F"{python} {script} FROM almalinux:{version} INTO {images}/{testname}:{version} INSTALL epel-release SEARCH mypy -vvv")
        x1 = X(F"{docker} inspect {images}/{testname}:{version}")
        self.assertTrue(greps(x1.out, "RepoTags"))
        sh____(F"{docker} rm -f {images}/{testname}:{version}")
    def test_92156(self) -> None:
        """ mypy is first distributed as python311-mypy in opensuse 15.6 """
        python = PYTHON
        script = SCRIPT if not LOCAL else F"{SCRIPT} --local"
        docker = DOCKER
        images = IMAGES
        testname = self.testname()
        version = self.testver()
        sh____(F"{python} {script} FROM opensuse/leap:{version} INTO {images}/{testname}:{version} SEARCH mypy -vvv")
        x1 = X(F"{docker} inspect {images}/{testname}:{version}")
        self.assertTrue(greps(x1.out, "RepoTags"))
        sh____(F"{docker} rm -f {images}/{testname}:{version}")
    def test_92204(self) -> None:
        """ ubuntu:20.04 does already have a python3-mypy """
        python = PYTHON
        script = SCRIPT if not LOCAL else F"{SCRIPT} --local"
        docker = DOCKER
        images = IMAGES
        testname = self.testname()
        version = self.testver()
        sh____(F"{python} {script} FROM ubuntu:{version} INTO {images}/{testname}:{version} SEARCH mypy -vvv")
        x1 = X(F"{docker} inspect {images}/{testname}:{version}")
        self.assertTrue(greps(x1.out, "RepoTags"))
        sh____(F"{docker} rm -f {images}/{testname}:{version}")
    def test_92224(self) -> None:
        python = PYTHON
        script = SCRIPT if not LOCAL else F"{SCRIPT} --local"
        docker = DOCKER
        images = IMAGES
        testname = self.testname()
        version = self.testver()
        sh____(F"{python} {script} FROM ubuntu:{version} INTO {images}/{testname}:{version} SEARCH mypy -vvv")
        x1 = X(F"{docker} inspect {images}/{testname}:{version}")
        self.assertTrue(greps(x1.out, "RepoTags"))
        sh____(F"{docker} rm -f {images}/{testname}:{version}")
    def test_92244(self) -> None:
        python = PYTHON
        script = SCRIPT if not LOCAL else F"{SCRIPT} --local"
        docker = DOCKER
        images = IMAGES
        testname = self.testname()
        version = self.testver()
        sh____(F"{python} {script} FROM ubuntu:{version} INTO {images}/{testname}:{version} SEARCH mypy -vvv")
        x1 = X(F"{docker} inspect {images}/{testname}:{version}")
        self.assertTrue(greps(x1.out, "RepoTags"))
        sh____(F"{docker} rm -f {images}/{testname}:{version}")
    def test_93156(self) -> None:
        python = PYTHON
        script = SCRIPT if not LOCAL else F"{SCRIPT} --local"
        docker = DOCKER
        images = IMAGES
        testname = self.testname()
        version = self.testver()
        sh____(F"{python} {script} FROM opensuse/leap:{version} INTO {images}/{testname}:{version} INSTALL python3-setuptools INSTALL python311-setuptools TEST 'python3 --version' TEST 'python3.11 --version'")
        x1 = X(F"{docker} inspect {images}/{testname}:{version}")
        self.assertTrue(greps(x1.out, "RepoTags"))
        sh____(F"{docker} rm -f {images}/{testname}:{version}")
    def test_93224(self) -> None:
        python = PYTHON
        script = SCRIPT if not LOCAL else F"{SCRIPT} --local"
        docker = DOCKER
        images = IMAGES
        testname = self.testname()
        version = self.testver()
        sh____(F"{python} {script} FROM ubuntu:{version} INTO {images}/{testname}:{version} INSTALL python3-setuptools TEST 'python3 --version'")
        x1 = X(F"{docker} inspect {images}/{testname}:{version}")
        self.assertTrue(greps(x1.out, "RepoTags"))
        sh____(F"{docker} rm -f {images}/{testname}:{version}")
    def test_93244(self) -> None:
        python = PYTHON
        script = SCRIPT if not LOCAL else F"{SCRIPT} --local"
        docker = DOCKER
        images = IMAGES
        testname = self.testname()
        version = self.testver()
        sh____(F"{python} {script} FROM ubuntu:{version} INTO {images}/{testname}:{version} INSTALL python3-setuptools TEST 'python3 --version'")
        x1 = X(F"{docker} inspect {images}/{testname}:{version}")
        self.assertTrue(greps(x1.out, "RepoTags"))
        sh____(F"{docker} rm -f {images}/{testname}:{version}")


if __name__ == "__main__":
    from optparse import OptionParser # pylint: disable=deprecated-module
    cmdline = OptionParser("%prog [options] test*",
                      epilog=__doc__.strip().split("\n", 1)[0])
    cmdline.add_option("-v", "--verbose", action="count", default=0, help="more verbose logging [%default]")
    cmdline.add_option("-^", "--quiet", action="count", default=0, help="less verbose logging [%default]")
    cmdline.add_option("->", "--script", metavar="PY", default=SCRIPT, help="different path to [%default]")
    cmdline.add_option("-M", "--mirror", metavar="PY", default=MIRROR, help="different path to [%default]")
    cmdline.add_option("-P", "--python", metavar="EXE", default=PYTHON, help="alternative to [%default] (=python3.11)")
    cmdline.add_option("-D", "--docker", metavar="EXE", default=DOCKER, help="alternative to [%default] (e.g. podman)")
    cmdline.add_option("-l", "--local", action="count", default=0, help="fail if local mirror not found [%(default)s]")
    cmdline.add_option("--failfast", action="store_true", default=False,
                  help="Stop the test run on the first error or failure. [%default]")
    opt, cmdline_args = cmdline.parse_args()
    logging.basicConfig(level=max(0, logging.WARNING - 10 * opt.verbose + 10 * opt.quiet))
    SCRIPT = opt.script
    DOCKER = opt.docker
    PYTHON = opt.python
    MIRROR = opt.mirror
    LOCAL = opt.local
    # unittest.main()
    suite = unittest.TestSuite()
    if not cmdline_args: cmdline_args = ["test_*"]
    for cmdline_arg in cmdline_args:
        for classname in sorted(globals()):
            if not classname.endswith("Test"):
                continue
            testclass = globals()[classname]
            for method in sorted(dir(testclass)):
                if cmdline_arg.endswith("/"):
                    cmdline_arg = cmdline_arg[:-1]
                if "*" not in cmdline_arg:
                    cmdline_arg += "*"
                if fnmatch(method, cmdline_arg):
                    suite.addTest(testclass(method))
    Runner = unittest.TextTestRunner
    result = Runner(verbosity=opt.verbose, failfast=opt.failfast).run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
