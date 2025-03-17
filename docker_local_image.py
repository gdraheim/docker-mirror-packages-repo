#! /usr/bin/env python3
# pylint: disable=line-too-long,bare-except,dangerous-default-value
""" build images using the local docker_mirror.py repo packages. """
from typing import List, Union, Optional, Mapping
from datetime import datetime as Time
import os.path
import sys
import subprocess
import logging
logg = logging.getLogger("local" if __name__ == "___main__" else __name__)

__copyright__ = "(C) 2025 Guido Draheim"
__contact__ = "https://github.com/gdraheim/docker-mirror-packages-repo"
__license__ = "CC0 Creative Commons Zero (Public Domain)"
__version__ = "1.7.7101"

# generalized from the testsuite.py in the docker-systemctl-replacement project

_maindir = os.path.dirname(sys.argv[0]) or "."
_mirror = os.path.join(_maindir, "docker_mirror.py")

NIX = ""
SKIP = True
DOCKER = "docker"
PYTHON = "/usr/bin/python3"
SAVETO = "localhost:5000/testing"
CONTAINER="into-"
RUNUSER=NIX
RUNEXE=NIX
RUNCMD=NIX
TIMEOUT = 999
_TAG="test_" + Time.now().strftime("%y%m%d%H%M")
_FROM="ubuntu:24.04"
FILEDEF=os.environ.get("DOCKER_LOCAL_IMAGE_DOCKERFILE", os.environ.get("DOCKER_LOCAL_IMAGE_FILE", NIX))
INTODEF=os.environ.get("DOCKER_LOCAL_IMAGE_INTO", os.environ.get("DOCKER_LOCAL_IMAGE_TAG", _TAG))
BASEDEF=os.environ.get("DOCKER_LOCAL_IMAGE_BASE", os.environ.get("DOCKER_LOCAL_IMAGE_FROM", _FROM))
DOCKERFILE = NIX
INTO = [] if not INTODEF else [INTODEF]
BASE = BASEDEF

if sys.version_info >= (3,10):
    from typing import TypeAlias
    intExitCode: TypeAlias = int
else:
    intExitCode = int

def decodes(text: Union[str, bytes, None]) -> str:
    if text is None: return ""
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
    if isinstance(cmd, str):
        logg.info(": %s", cmd)
    else:
        logg.info(": %s", " ".join([q_str(item) for item in cmd]))
    return subprocess.check_call(cmd, shell=shell)
def sx____(cmd: Union[str, List[str]], shell: bool = True) -> int:
    if isinstance(cmd, str):
        logg.info(": %s", cmd)
    else:
        logg.info(": %s", " ".join([q_str(item) for item in cmd]))
    return subprocess.call(cmd, shell=shell)
def output(cmd: Union[str, List[str]], shell: bool = True, env: Optional[Mapping[str, str]] = None) -> str:
    if isinstance(cmd, str):
        logg.info(": %s", cmd)
    else:
        logg.info(": %s", " ".join([q_str(item) for item in cmd]))
    run = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE, env=env)
    out, err = run.communicate()
    if err:
        logg.info("ERR %s", err)
    return decodes(out).rstrip()
def q_str(part: Union[str, int, None]) -> str:
    if part is None:
        return ""
    if isinstance(part, int):
        return str(part)
    return "'%s'" % part  # pylint: disable=consider-using-f-string

def package_tool(distro: str = NIX):
    if "centos" in distro or "almalinux" in distro or "rhel" in distro:
        return "yum --setopt=repo_gpgcheck=false"
    if "opensuse" in distro:
        return "zypper --no-gpg-checks --no-refresh"
    return "apt-get -o Acquire::AllowInsecureRepositories=true"
def package_refresh(distro: str = NIX):
    if "opensuse" in distro:
        return "zypper --no-gpg-checks refresh"
    return "apt-get -o Acquire::AllowInsecureRepositories=true update"
def package_search(distro: str = NIX):
    if "opensuse" in distro:
        return "zypper --no-refresh search"
    return "apt-cache search"

def docker_local_build(cmdlist: List[str] = [], cyclic: Optional[List[str]] = None) -> intExitCode:
    """" cmd2 should be given as pairs (cmd,arg) but some items are recognized by their format directly"""
    needsargument = ["FROM","from", "INTO", "into", "TAG", "tag", "COPY", "copy", "SAVE", "save",
                "SEARCH", "search", "INSTALL", "install","USER", "user","RUN", "run", "TEST", "test", 
                "SYMLINK", "symlink"]
    cyclic = cyclic if cyclic is not None else []
    mirror = _mirror
    docker = DOCKER
    dockerfile = DOCKERFILE
    tagging: str = INTO
    building: str = BASE
    timeout: int = TIMEOUT
    into: str = NIX
    runuser = RUNUSER
    runexe = RUNEXE
    runcmd = RUNCMD
    waitcmd: str = NIX
    search = NIX
    refresh = NIX
    distro = NIX
    package = NIX
    logg.info("-- %s", cmdlist)
    for nextarg in cmdlist:
        if waitcmd:
            cmd2 = F"{waitcmd} {nextarg}"
            waitcmd = NIX
        else:
            if " " in nextarg:
                cmd2 = nextarg
            elif "@" in nextarg:
                cmd2 = F"INSTALL {nextarg}"
            elif nextarg.startswith(":"):
                cmd2 = "MAKE {nextcmd}"
            elif nextarg in needsargument:
                waitcmd = nextarg
                continue
            else:
                logg.error("unrecognized command %s", nextarg)
                return os.EX_USAGE
        if " " in cmd2:
            cmd, arg = cmd2.split(" ", 1)
        else:
            cmd, arg = cmd2, NIX
        logg.info("- %s [%s]", cmd, arg)
        if cmd in ["FILE", "file"]:
            if not arg:
                logg.error("no dockerfile value provided: %s", arg)
                return os.EX_USAGE
            elif not os.path.exists(arg):
                logg.error("no dockerfile value provided: %s", arg)
                return os.EX_OSFILE
            else:
                dockerfile = arg
        elif cmd in ["BUILD", "build"]:
            directory = arg
            if not arg:
                logg.error("no build directory provided: %s", directory)
                return os.EX_USAGE
            elif not os.path.isdir(arg):
                logg.error("no build directory provided: %s", directory)
                return os.EX_OSFILE
            else:
                filename = os.path.realpath(os.path.join(directory, dockerfile))
                if not os.path.isfile(filename):
                    logg.error("dockerfile does not exist: %s", filename)
                    return os.EX_OSFILE
                try:
                    if filename in cyclic:
                        logg.error("cycle detection: '%s' = %s", arg, filename)
                        return os.EX_OSERR
                    cyclic2 = cyclic + [filename]
                    with open(arg, filename, encoding="utf-8") as f:
                        cmdlist2 = [line.rstrip() for line in f]
                        missing2 = [cmd2 for cmd2 in cmdlist2 if cmd2 in needsargument]
                        if missing2:
                            logg.error("in %s/%s  missing arguments for %s", directory, dockerfile, " and ".join(missing2))
                            return os.EX_DATAERR
                        exitcode = docker_local_build(cmdlist2, cyclic2)
                        if exitcode:
                            return exitcode
                except (OSError, IOError) as e:
                    logg.error("on import %s: %s", arg, e)
                    return os.EX_IOERR
        if cmd in  ["FROM","from"]:
            building = arg
            continue
        if cmd in  ["INTO","into","TAG","tag"]:
            if not arg:
                logg.warning("no tag value given")
                continue
            if into:
                runcmds = runexe.split(" ") + runcmd.split(" ") if runexe else runcmd.split(" ")
                runs = F"-c 'USER {runuser}'" if runuser else NIX
                cmds = F"-c 'CMD {runcmds}'" if runcmd else NIX
                sx____(F"{docker} rmi {tagging}")
                sx____(F"{docker} stop {into}")
                sh____(F"{docker} commit {cmds} {runs} {into} {tagging}")
                sh____(F"{docker} rm -f {into}")
                into = NIX
            tagging = arg
            into = CONTAINER+os.path.basename(tagging).replace(":","-").replace(".","-")
            distro = output(F"{mirror} detect {building}")
            addhosts = output(F"{mirror} start {distro} --add-hosts --no-detect")
            sh____(F"{docker} rm -f {into}")
            sh____(F"{docker} run -d --name={into} --rm=true {addhosts} {building} sleep {timeout}")
            continue
        if cmd in  ["EXE", "exe"]:
            if not arg:
                logg.warning("no exe value given")
                continue
            runexe = arg
            continue
        if cmd in  ["CMD", "cmd"]:
            if not arg:
                logg.warning("no cmd value given")
                continue
            runcmd = arg
            continue
        if cmd in  ["USER", "user"]:
            if not arg:
                logg.warning("no user value given")
                continue
            runuser = arg
            continue
        if cmd in  ["SEARCH", "search"]:
            pattern = arg
            if not arg:
                logg.warning("no search pattern given")
                continue
            if not refresh:
                refresh = package_refresh(distro)
                if refresh:
                    sx____(F"{docker} exec {into} {refresh}")
            search = package_search(distro)
            sx____(F"{docker} exec {into} {search} {pattern}")
            cmd = NIX
            continue
        if cmd in  ["INSTALL", "install"]:
            if "@" in arg:
                test, pack = arg.split("@", 1)
            else:
                test, pack = NIX, arg
            if not pack:
                logg.warning("no install pack given")
                continue
            if not refresh:
                refresh = package_refresh(distro)
                logg.debug("install %s", refresh)
                if refresh:
                    sx____(F"{docker} exec {into} {refresh}")
            package = package_tool(distro)
            logg.debug("TEST %s PACK %s FROM %s", test, pack, arg)
            if test:
                sx____(F"{docker} exec {into} bash -c 'test -f {test} || {package} install -y {pack}'")
            else:
                sx____(F"{docker} exec {into} {package} install -y {pack}")
            continue
        if cmd in  ["MAKE", "MAKE"]:
            if arg.startswith(":"):
                dst = arg[1:]
            else:
                dst = arg
            if not dst:
                logg.warning("no make dst given")
                continue
            if dst.endswith("/"):
                sx____(F"{docker} exec {into} mkdir -p {dst}")
            else:
                if "/" in dst:
                    dstdir = os.path.dirname(dst)
                    sx____(F"{docker} exec {into} mkdir -p {dstdir}")
                sx____(F"{docker} exec {into} touch {dst}")
            continue
        if cmd in  ["COPY", "copy"]:
            logg.info("--copy %s", arg)
            if ":" in arg:
                src, dst = arg.split(":", 1)
            else:
                src, dst = arg, NIX
            if not src:
                logg.warning("no copy src given")
                continue
            if not dst:
                logg.warning("no copy dst given")
                continue
            sx____(F"{docker} copy {src} {into}:{dst}")
            continue
        if cmd in  ["SAVE", "save"]:
            logg.info("--save %s", arg)
            if ":" in arg:
                src, dst = arg.split(":", 1)
            else:
                src, dst = arg, "./"
            sx____(F"{docker} copy {into}:{src} {dst}")
            continue
        if cmd in  ["SYMLINK", "symlink"]:
            logg.info("--symlink %s", arg)
            if ":" in arg:
                src, dst = arg.split(":", 1)
            else:
                src, dst = arg, "/tmp"
            if "/" not in dst and "/" in src:
                srcdir=os.path.dirname(src)
                srcname=os.path.basename(src)
                sx____(F"{docker} exec {into} ln -s {srcname} {srcdir}/{dst}")
            else:
                sx____(F"{docker} exec {into} ln -s {src} {dst}")
            continue
        if cmd in  ["TEST", "test"]:
            logg.info("--test %s", arg)
            if arg.startswith(":"):
                dst = arg[1:]
                sh____(F"{docker} exec {into} wc -l {dst}")
            else:
                dst = arg
                sh____(F"{docker} exec {into} {dst}")
            continue
        if cmd in  ["RUN", "run"]:
            logg.info("- RUN %s", arg)
            dst = arg.replace("'", "\\'")
            sh____(F"{docker} exec {into} bash -c '{dst}'")
            continue
        if cmd in ["COMMIT", "commit"]:
            logg.info("--commit")
            if into:
                runcmds = runexe.split(" ") + runcmd.split(" ") if runexe else runcmd.split(" ")
                runs = F"-c 'USER {runuser}'" if runuser else NIX
                cmds = F"-c 'CMD {runcmds}'" if runcmd else NIX
                sx____(F"{docker} rmi {tagging}")
                sh____(F"{docker} commit {cmds} {runs} {into} {tagging}")
                sh____(F"{docker} rm -f {into}")
                into = NIX
            continue
        logg.error("unknown cmd %s", cmd)
        continue
    if into:
        logg.info("--ends")
        runcmds = runexe.split(" ") + runcmd.split(" ") if runexe else runcmd.split(" ")
        runs = "-c 'USER {runuser}'" if runuser else NIX
        cmds = "-c 'CMD {runcmds}'" if runcmd else NIX
        sx____(F"{docker} rmi {tagging}")
        sh____(F"{docker} commit {cmds} {runs} {into} {tagging}")
        sh____(F"{docker} rm -f {into}")
    addhosts = output(F"{mirror} stop {distro} --add-hosts --no-detect")
    return 0

if __name__ == "__main__":
    from optparse import OptionParser  # pylint: disable=deprecated-module
    _o = OptionParser("%prog [options] test*",
                      epilog=__doc__.strip().split("\n", 1)[0])
    _o.add_option("-v", "--verbose", action="count", default=0,
                  help="increase logging level [%default]")
    _o.add_option("-D", "--docker", metavar="EXE", default=DOCKER,
                  help="use another docker container tool [%default]")
    _o.add_option("-p", "--python", metavar="EXE", default=PYTHON,
                  help="use another python execution engine [%default]")
    _o.add_option("-C", "--chdir", metavar="PATH", default="",
                  help="change directory before building {%default}")
    _o.add_option("-b", "--base", "--from", metavar="NAME", default=BASE,
                  help="FROM=%default (or CENTOS)")
    _o.add_option("-t", "--into", "--tag", metavar="NAME", action="append", default=INTO,
                  help="TAG=%default (")
    _o.add_option("-f", "--file", metavar="Dockerfile", default=DOCKERFILE,
                  help="set dockerfile name for BUILD")
    opt, args = _o.parse_args()
    logging.basicConfig(level = logging.WARNING - opt.verbose * 10)
    DOCKER=opt.docker
    PYTHON=opt.python
    BASE=opt.base
    INTO=opt.into
    CHDIR=opt.chdir
    DOCKERFILE=opt.file
    sys.exit(docker_local_build(args))
