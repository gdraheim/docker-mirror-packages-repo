#! /usr/bin/env python3
__copyright__ = "(C) 2024 Guido Draheim"
__contact__ = "https://github.com/gdraheim/docker-mirror-packages-repo"
__license__ = "CC0 Creative Commons Zero (Public Domain)"
__version__ = "1.7.6334"

from typing import Optional, Union, Dict, List, Any, Sequence, Callable, Iterable, cast, NamedTuple
import shutil
import inspect
import unittest
import sys, os, re
from fnmatch import fnmatchcase as fnmatch
from subprocess import getoutput, Popen, PIPE

import logging
logg = logging.getLogger("tests.opensuse")
DONE = (logging.ERROR + logging.WARNING)//2
logging.addLevelName(DONE, "DONE")
NIX = ""
LIST: List[str] = []

PYTHON = "python3"
SCRIPT = "opensuse-docker-mirror.py"
COVERAGE = False
KEEP = False

def sh(cmd: str, **args: Any) -> str:
    logg.debug("sh %s", cmd)
    return getoutput(cmd, **args)
class Proc(NamedTuple):
    out: str
    err: str
    ret: int
def runs(cmd: str, **args: Any) -> Proc:
    logg.debug("run %s", cmd)
    if isinstance(cmd, str):
        proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, **args)
    else:
        proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, **args)
    out, err = proc.communicate()
    return Proc(decodes(out), decodes(err), proc.returncode)
def decodes(text: Union[str, bytes]) -> str:
    if isinstance(text, bytes):
        encoded = sys.getdefaultencoding()
        if encoded in ["ascii"]:
            encoded = "utf-8"
        try: 
            return text.decode(encoded)
        except:
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
    def testname(self, suffix: Optional[str] = None) -> str:
        name = self.caller_testname()
        if suffix:
            return name + "_" + suffix
        return name
    def testdir(self, testname: Optional[str] = None, keep: bool = False) -> str:
        testname = testname or self.caller_testname()
        newdir = "tmp/tmp." + testname
        if os.path.isdir(newdir) and not keep:
            shutil.rmtree(newdir)
        if not os.path.isdir(newdir):
            os.makedirs(newdir)
        return newdir
    def rm_testdir(self, testname: Optional[str] = None) -> str:
        testname = testname or self.caller_testname()
        newdir = "tmp/tmp." + testname
        if os.path.isdir(newdir):
            if not KEEP:
                shutil.rmtree(newdir)
        return newdir
    def coverage(self, testname: Optional[str] = None) -> None:
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
    #
    def test_2100(self) -> None:
        cover = self.cover()
        script = SCRIPT
        cmd = F"{cover} {script} --help"
        out = sh(cmd)
        logg.debug("out: %s", out)
        self.assertIn("imagesrepo=PREFIX", out)
        self.coverage()
    def test_2101(self) -> None:
        cover = self.cover()
        script = SCRIPT
        cmd = F"{cover} {script} commands"
        out = sh(cmd)
        logg.debug("out: %s", out)
        self.assertIn("|disk|", out)
        self.assertIn("|image|", out)
        self.assertIn("|repo|", out)
        self.assertIn("|datadir|", out)
        self.coverage()
    def test_2110(self) -> None:
        cover = self.cover()
        script = SCRIPT
        cmd = F"{cover} {script} datadir"
        out = sh(cmd)
        logg.debug("out: %s", out)
        self.coverage()
    def test_2200(self) -> None:
        tmp = self.testdir()
        cover = self.cover()
        script = SCRIPT
        cmd = F"{cover} {script} datadir"
        run = runs(cmd, env={"REPODATADIR": tmp})
        logg.debug("out: %s", run.out)
        self.assertEqual(tmp, run.out.strip())
        self.coverage()
        self.rm_testdir()
    def test_2201(self) -> None:
        tmp = self.testdir()
        cover = self.cover()
        script = SCRIPT
        cmd = F"{cover} {script} datadir --datadir={tmp}"
        run = runs(cmd)
        logg.debug("out: %s", run.out)
        self.assertEqual(tmp, run.out.strip())
        self.coverage()
        self.rm_testdir()
    def test_2202(self) -> None:
        tmp = self.testdir()
        cover = self.cover()
        script = SCRIPT
        data = F"{tmp}/data"
        repo = F"{tmp}/repo"
        cmd = F"{cover} {script} datadir --datadir={data} --repodir={repo}"
        run = runs(cmd)
        logg.debug("out: %s", run.out)
        self.assertNotEqual(data, run.out.strip()) # datadir does not exist
        self.assertEqual(repo, run.out.strip()) # repodir is fallback
        self.coverage()
        self.rm_testdir()
    def test_2203(self) -> None:
        tmp = self.testdir()
        cover = self.cover()
        script = SCRIPT
        data = F"{tmp}/data"
        repo = F"{tmp}/repo"
        os.makedirs(data)
        cmd = F"{cover} {script} datadir --datadir={data} --repodir={repo}"
        run = runs(cmd)
        logg.debug("out: %s", run.out)
        self.assertEqual(data, run.out.strip()) # datadir does now exist
        self.assertNotEqual(repo, run.out.strip()) # repodir not a fallback
        self.coverage()
        self.rm_testdir()
    def test_999(self) -> None:
        if COVERAGE:
            o1 = sh(F" {PYTHON} -m coverage combine")
            o2 = sh(F" {PYTHON} -m coverage report {SCRIPT}")
            o3 = sh(F" {PYTHON} -m coverage annotate  {SCRIPT}")
            logg.log(DONE,"COVERAGE:\n%s\n%s\n%s", o1, o2, o3)

if __name__ == "__main__":
    # unittest.main()
    from optparse import OptionParser
    cmdline = OptionParser("%s test...")
    cmdline.add_option("-v", "--verbose", action="count", default=0, help="more verbose logging")
    cmdline.add_option("-^", "--quiet", action="count", default=0, help="less verbose logging")
    cmdline.add_option("-k", "--keep", action="count", default=0, help="keep testdir")
    cmdline.add_option("--coverage", action="store_true", default=False,
                       help="Generate coverage data. [%default]")
    cmdline.add_option("--failfast", action="store_true", default=False,
                       help="Stop the test run on the first error or failure. [%default]")
    cmdline.add_option("--xmlresults", metavar="FILE", default=None,
                       help="capture results as a junit xml file [%default]")
    opt, args = cmdline.parse_args()
    logging.basicConfig(level=max(0, logging.WARNING - 10 * opt.verbose + 10 * opt.quiet))
    KEEP = opt.keep
    COVERAGE = opt.coverage
    if not args:
        args = ["test_*"]
    suite = unittest.TestSuite()
    for arg in args:
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