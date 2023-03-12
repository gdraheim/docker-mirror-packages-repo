#! /usr/bin/python3
""" sync packages repo to disk and make docker mirror images from it.
    Try to run 'sync' followed be 'repo'. If a command starts with a
    number then it changes the version to be handled. A usual command
    would be 'mirror.py 7.7 sync repo -v'. If no argument is given
    then 'make' the last version = 'sync pull repo test check tags'."""

__copyright__ = "(C) 2023 Guido Draheim"
__contact__ = "https://github.com/gdraheim/docker-mirror-packages-repo"
__license__ = "CC0 Creative Commons Zero (Public Domain)"
__version__ = "1.7.5111"

# from __future__ import literal_string_interpolation # PEP498 Python3.6
from typing import Optional, Dict, List, Tuple, Union
from collections import OrderedDict
import os
import os.path as path
import sys
import re
import json
import datetime
import subprocess
import shutil
import logging
logg = logging.getLogger("MIRROR")

if sys.version[0] == '3':
    basestring = str
    xrange = range

IMAGESREPO = os.environ.get("IMAGESREPO", "localhost:5000/mirror-packages")
REPODATADIR = os.environ.get("REPODATADIR", "")
REPODIR = os.environ.get("REPODIR", "repo.d")

DATADIRS = [REPODATADIR,
            "/srv/docker-mirror-packages",
            "/data/docker-mirror-packages",
            "/data/docker-centos-repo-mirror",
            "/dock/docker-mirror-packages"]

BASE: Dict[str, str] = {}
BASE["42.2"] = "opensuse/leap"
BASE["42.3"] = "opensuse/leap"
BASE["15.0"] = "opensuse/leap"
BASE["15.1"] = "opensuse/leap"
BASE["15.2"] = "opensuse/leap"
BASE["15.3"] = "opensuse/leap"
BASE["15.4"] = "opensuse/leap"
XXLEAP: List[str] = []  # ["15.2"] # obsolete, using repodata-fix.py now
LEAP: str = "15.3"

RSYNC_SUSE = "rsync://suse.uni-leipzig.de/opensuse-full/opensuse"
RSYNC_SUSE2 = "rsync://ftp.tu-chemnitz.de/pub/linux/opensuse"
RSYNC_SUSE3 = "rsync://mirror.cs.upb.de/opensuse"

RSYNC = "rsync"
DOCKER = "docker"
LAYER = "base"
RETRY = 3

BASEVERSION: Dict[str, str] = {}
BASEVERSION["15.4"] = "15.3"  # image:opensuse/base

def opensuse_make() -> None:
    opensuse_sync()
    opensuse_repo()
    opensuse_test()

def opensuse_sync() -> None:
    opensuse_dir()
    opensuse_sync_1()
    opensuse_sync_2()
    opensuse_sync_3()
    opensuse_sync_4()

def opensuse_dir(suffix: str = "") -> str:
    leap = LEAP
    repodir = REPODIR
    dirname = "opensuse.{leap}{suffix}".format(**locals())
    dirlink = path.join(repodir, dirname)
    if not path.isdir(repodir):
        os.mkdir(repodir)
    if path.islink(dirlink) and not path.isdir(dirlink):
        os.unlink(dirlink)
    if not path.islink(dirlink):
        if path.isdir(dirlink):
            shutil.rmtree(dirlink)  # local dir
        # we want to put the mirror data on an external disk
        for data in reversed(DATADIRS):
            logg.debug(".. check %s", data)
            if path.isdir(data):
                dirpath = path.join(data, dirname)
                if not path.isdir(dirpath):
                    os.makedirs(dirpath)
                os.symlink(dirpath, dirlink)
                break
    dircheck = path.join(dirlink, ".")
    if path.isdir(dircheck):
        logg.info("%s -> %s", dirlink, os.readlink(dirlink))
    else:
        os.mkdir(dirname)  # local dir
        logg.warning("%s/. local dir", dirlink)
    return dirlink

def opensuse_save() -> None:
    yymmdd = datetime.date.today().strftime("%Y.%m%d")
    leap = LEAP
    repodir = REPODIR
    src = "{repodir}/opensuse.{leap}/.".format(**locals())
    dst = opensuse_dir("." + yymmdd) + "/."
    logg.info("src = %s", src)
    logg.info("dst = %s", dst)
    for srcpath, dirnames, filenames in os.walk(src):
        logg.info("dirpath %s dirnames %s", srcpath, dirnames)
        dstpath = srcpath.replace(src, dst)
        for dirname in dirnames:
            dirpath = path.join(dstpath, dirname)
            if not path.isdir(dirpath):
                os.mkdir(dirpath)
        for filename in filenames:
            srcfile = path.join(srcpath, filename)
            dstfile = path.join(dstpath, filename)
            if not path.exists(dstfile):
                if dstfile.endswith(".rpm"):
                    os.link(srcfile, dstfile)
                else:
                    shutil.copy(srcfile, dstfile)

skipdirs = [
    "boot", "EFI", "160.3-boot", "20.8-boot", "24.5-boot",
    "aarch64", "s390x", "ppc", "ppc64le", ]

def opensuse_sync_1() -> None:
    opensuse_sync_repo_("distribution", "oss")
def opensuse_sync_2() -> None:
    opensuse_sync_repo_("distribution", "non-oss")
def opensuse_sync_3() -> None:
    opensuse_sync_pack_("update", "non-oss")
def opensuse_sync_4() -> None:
    opensuse_sync_pack_("update", "non-oss", ["x86_64", "noarch", "strc", "nosrc"])

def opensuse_sync_repo_(dist: str, repo: str, filters: List[str] = []) -> None:
    leap = LEAP
    repodir = REPODIR
    mirror = RSYNC_SUSE
    rsync = RSYNC
    excludes = "".join(["""--filter="exclude %s" """ % name for name in skipdirs])
    excludes += "".join(["""--filter="exclude %s" """ % name for name in filters])
    excludes += """ --size-only --filter="exclude *.src.rpm" """
    leaprepo = "{repodir}/opensuse.{leap}/{dist}/leap/{leap}/repo".format(**locals())
    if not path.isdir(leaprepo): os.makedirs(leaprepo)
    cmd = "{rsync} -rv {mirror}/{dist}/leap/{leap}/repo/{repo} {leaprepo}/ {excludes}".format(**locals())
    # sh___(cmd):
    logfile = "{repodir}/opensuse.{leap}.log".format(**locals())
    for attempt in xrange(RETRY):
        try:
            sh___("set -o pipefail ; {cmd} |& tee {logfile}".format(**locals()))
        except subprocess.CalledProcessError as e:
            logg.warning("[%s] %s", e.returncode, cmd)
            raise

def opensuse_sync_pack_(dist: str, repo: str, filters: List[str] = []) -> None:
    leap = LEAP
    repodir = REPODIR
    mirror = RSYNC_SUSE
    rsync = RSYNC
    excludes = "".join(["""--filter="exclude %s" """ % name for name in skipdirs])
    excludes += "".join(["""--filter="exclude %s" """ % name for name in filters])
    excludes += """ --size-only --filter="exclude *.src.rpm" """
    leaprepo = "{repodir}/opensuse.{leap}/{dist}/leap/{leap}".format(**locals())
    if not path.isdir(leaprepo): os.makedirs(leaprepo)
    cmd = "{rsync} -rv {mirror}/{dist}/leap/{leap}/{repo} {leaprepo}/ {excludes}".format(**locals())
    # sh___(cmd):
    logfile = "{repodir}/opensuse.{leap}.log".format(**locals())
    for attempt in xrange(RETRY):
        try:
            sh___("set -o pipefail ; {cmd} |& tee {logfile}".format(**locals()))
        except subprocess.CalledProcessError as e:
            logg.warning("[%s] %s", e.returncode, cmd)
            log = open(logfile).read()
            if "No such file or directory" in log:
                logg.info("OK - no updates yet")
                break
            raise

# /etc/zypp/repos.d/oss-update.repo:baseurl=http://download.opensuse.org/update/42.2/
# /etc/zypp/repos.d/update-non-oss.repo:baseurl=http://download.opensuse.org/update/leap/42.2/non-oss/
# /etc/zypp/repos.d/oss.repo:baseurl=http://download.opensuse.org/distribution/leap/42.2/repo/oss/
# /etc/zypp/repos.d/non-oss.repo:baseurl=http://download.opensuse.org/distribution/leap/42.2/repo/non-oss/

# noarch/supertuxkart-data-1.1-lp152.1.2.noarch.rpm: Group       : Amusements/Games/3D/Race
def opensuse_games(suffix: str = "") -> None:
    games: Dict[str, str] = {}
    leap = LEAP
    repodir = REPODIR
    dirname = "{repodir}/opensuse.{leap}{suffix}".format(**locals())
    basedir = dirname + "/."
    logg.info("check %s", basedir)
    if path.isdir(basedir):
        for dirpath, dirnames, filenames in os.walk(basedir):
            for filename in filenames:
                if filename.endswith(".rpm"):
                    rpm = path.join(dirpath, filename)
                    # if "tux" not in rpm: continue
                    out, end = output2("rpm -q --info {rpm}".format(**locals()))
                    for line in out.splitlines():
                        if line.startswith("Group"):
                            if "/Games/" in line:
                                games[filename] = line.split(":", 1)[1].strip()
    gameslist = dirname + "-games.json"
    if games:
        json.dump(games, open(gameslist, "w"), indent=2, ensure_ascii=False, sort_keys=True)
        logg.info("found %s games, written to %s", len(games), gameslist)

opensuserepo_CMD = ["/usr/bin/python", "/srv/scripts/filelist.py", "--data", "/srv/repo"]
opensuserepo_PORT = "80"
def opensuse_repo() -> None:
    docker = DOCKER
    leap = LEAP
    repodir = REPODIR
    baseversion = leap
    if baseversion in BASEVERSION:
        baseversion = BASEVERSION[baseversion]
    scripts = repo_scripts()
    cname = "opensuse-repo-" + leap
    image = BASE[LEAP]
    imagesrepo = IMAGESREPO
    bind_repo = ""
    base_repo = "{repodir}/opensuse.{leap}/distribution/leap/{leap}/repo/oss".format(**locals())
    logg.info("/base-repo -> %s", base_repo)
    if path.isdir(base_repo):
        base_repo_path = path.abspath(base_repo)
        bind_repo = "-v {base_repo_path}:/base-repo".format(**locals())
    sx___("{docker} rm --force {cname}".format(**locals()))
    sh___("{docker} run --name={cname} {bind_repo} --detach {image}:{baseversion} sleep 9999".format(**locals()))
    sh___("{docker} exec {cname} mkdir -p /srv/repo/".format(**locals()))
    sh___("{docker} cp {scripts} {cname}:/srv/scripts".format(**locals()))
    oss = "repo-oss"  # Opensuse 15.x main repo
    if bind_repo:
        oss = "local-repo"
        sh___("{docker} exec {cname} zypper ar --no-gpgcheck file:///base-repo {oss}".format(**locals()))
    if True:
        sh___("{docker} exec {cname} zypper install -y -r {oss} python".format(**locals()))
        sh___("{docker} exec {cname} zypper install -y -r {oss} python-xml".format(**locals()))
    if leap in XXLEAP:
        sh___("{docker} exec {cname} zypper install -y -r {oss} createrepo".format(**locals()))
    if bind_repo:
        sh___("{docker} exec {cname} zypper rr {oss}".format(**locals()))
    CMD = str(opensuserepo_CMD).replace("'", '"')
    PORT = opensuserepo_PORT
    base = "base"
    cmd = "{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' -m {base} {cname} {imagesrepo}/opensuse-repo/{base}:{leap}"
    sh___(cmd.format(**locals()))
    dists: Dict[str, List[str]] = OrderedDict()
    # dists["mini"] = ["distribution", "-games"]
    dists["main"] = ["distribution"]
    dists["update"] = ["update"]
    for dist in dists:
        sx___("{docker} rm --force {cname}".format(**locals()))
        sh___("{docker} run --name={cname} --detach {imagesrepo}/opensuse-repo/{base}:{leap} sleep 9999".format(**locals()))
        clean: Dict[str, str] = {}
        for subdir in dists[dist]:
            basedir = "{repodir}/opensuse.{leap}/.".format(**locals())
            pooldir = "{repodir}/opensuse.{leap}/{subdir}".format(**locals())
            if subdir.startswith("-"):
                gamesfile = "{repodir}/opensuse.{leap}{subdir}.json".format(**locals())
                clean = json.load(open(gamesfile))
                if not clean:
                    continue
                logg.info("loaded %s files from %s", len(clean), gamesfile)
                remove: Dict[str, str] = {}
                for dirpath, dirfiles, filenames in os.walk(basedir):
                    for filename in filenames:
                        if filename in clean:
                            repopath = dirpath.replace(basedir, "/srv/repo")
                            filepath = path.join(repopath, filename)
                            remove[filepath] = filename
                logg.info("removing %s files from %s", len(remove), subdir)
                removes = " ".join(remove.keys())
                sh___("{docker} exec {cname} rm -f {removes}".format(**locals()), debugs=False)
            elif path.isdir(pooldir):
                sh___("{docker} cp {pooldir} {cname}:/srv/repo/".format(**locals()))
                base = dist
                sh___("{docker} exec {cname} bash -c \"find /srv/repo/{subdir} -name repomd.xml -exec python /srv/scripts/repodata-fix.py {{}} -v ';'\" ".format(**locals()))
        if dist in ["update"]:
            # sh___("{docker} exec {cname} rm -r /srv/repo/{dist}/{leap}".format(**locals()))
            sh___("{docker} exec {cname} ln -s /srv/repo/{dist}/leap/{leap}/oss /srv/repo/{dist}/{leap}".format(**locals()))
            if leap in XXLEAP:
                cmd = """ {docker} exec {cname} bash -c "cd /srv/repo/{dist}/leap/{leap}/oss && createrepo ." """
                sh___(cmd.format(**locals()))
        if base == dist:
            cmd = "{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' -m {base} {cname} {imagesrepo}/opensuse-repo/{base}:{leap}"
            sh___(cmd.format(**locals()))
    sh___("{docker} rm --force {cname}".format(**locals()))
    sh___("{docker} tag {imagesrepo}/opensuse-repo/{base}:{leap} {imagesrepo}/opensuse-repo:{leap}".format(**locals()))
    sh___("{docker} rmi {imagesrepo}/opensuse-repo/base:{leap}".format(**locals()))  # untag non-packages base

def opensuse_test() -> None:
    leap = LEAP
    # cat opensuse-compose.yml | sed \
    #    -e 's|opensuse-repo:.*"|opensuse/repo:$(LEAP)"|' \
    #    -e 's|opensuse:.*"|$(OPENSUSE):$(LEAP)"|' \
    #    > opensuse-compose.yml.tmp
    # - docker-compose -p $@ -f opensuse-compose.yml.tmp down
    # docker-compose -p $@ -f opensuse-compose.yml.tmp up -d
    # docker exec $@_host_1 zypper install -y firefox
    # docker-compose -p $@ -f opensuse-compose.yml.tmp down

def opensuse_scripts() -> None:
    print(repo_scripts())
def repo_scripts() -> str:
    me = os.path.dirname(sys.argv[0])
    dn = os.path.join(me, "scripts")
    if os.path.isdir(dn): return dn
    dn = os.path.join(me, "docker_mirror/scripts")
    if os.path.isdir(dn): return dn
    dn = os.path.join(me, "../docker_mirror/scripts")
    if os.path.isdir(dn): return dn
    dn = os.path.join(me, "../share/docker_mirror/scripts")
    if os.path.isdir(dn): return dn
    return "scripts"

#############################################################################

def decodes(text: Union[bytes, str]) -> str:
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

def sh___(cmd: Union[str, List[str]], shell: bool = True, debugs: bool = True) -> int:
    if isinstance(cmd, basestring):
        if debugs:
            logg.info(": %s", cmd)
    else:
        if debugs:
            logg.info(": %s", " ".join(["'%s'" % item for item in cmd]))
    return subprocess.check_call(cmd, shell=shell)

def sx___(cmd: Union[str, List[str]], shell: bool = True, debugs: bool = True) -> int:
    if isinstance(cmd, basestring):
        if debugs:
            logg.info(": %s", cmd)
    else:
        if debugs:
            logg.info(": %s", " ".join(["'%s'" % item for item in cmd]))
    return subprocess.call(cmd, shell=shell)
def output(cmd: Union[str, List[str]], shell: bool = True, debugs: bool = True) -> str:
    if isinstance(cmd, basestring):
        if debugs:
            logg.info(": %s", cmd)
    else:
        if debugs:
            logg.info(": %s", " ".join(["'%s'" % item for item in cmd]))
    run = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE)
    out, err = run.communicate()
    return decodes(out)
def output2(cmd: Union[str, List[str]], shell: bool = True, debugs: bool = True) -> Tuple[str, int]:
    if isinstance(cmd, basestring):
        if debugs:
            logg.info(": %s", cmd)
    else:
        if debugs:
            logg.info(": %s", " ".join(["'%s'" % item for item in cmd]))
    run = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE)
    out, err = run.communicate()
    return decodes(out), run.returncode
def output3(cmd: Union[str, List[str]], shell: bool = True, debugs: bool = True) -> Tuple[str, str, int]:
    if isinstance(cmd, basestring):
        if debugs:
            logg.info(": %s", cmd)
    else:
        if debugs:
            logg.info(": %s", " ".join(["'%s'" % item for item in cmd]))
    run = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = run.communicate()
    return decodes(out), decodes(err), run.returncode

#############################################################################

def path_find(base: str, name: str) -> Optional[str]:
    for dirpath, dirnames, filenames in os.walk(base):
        if name in filenames:
            return path.join(dirpath, name)
    return None

def opensuse_commands_() -> None:
    print(commands())
def commands() -> str:
    cmds: List[str] = []
    for name in sorted(globals()):
        if name.startswith("opensuse_"):
            if "_sync_" in name: continue
            if name.endswith("_"): continue
            func = globals()[name]
            if callable(func):
                cmd = name.replace("opensuse_", "")
                cmds += [cmd]
    return "|".join(cmds)

def LEAP_set(leap: str) -> str:
    global LEAP
    if len(leap) <= 2:
        LEAP = max([os for os in BASE if os.startswith(leap) and not os.startswith("42")])
        return LEAP
    if leap not in BASE:
        logg.warning("%s is not a known os version", leap)
    LEAP = leap
    return LEAP

def config_globals(settings: List[str]) -> None:
    for setting in settings:
        nam, val = setting, "1"
        if "=" in setting:
            nam, val = setting.split("=", 1)
        elif nam.startswith("no-") or nam.startswith("NO-"):
            nam, val = nam[3:], "0"
        elif nam.startswith("No") or nam.startswith("NO"):
            nam, val = nam[2:], "0"
        if nam in globals():
            old = globals()[nam]
            if old is False or old is True:
                globals()[nam] = (val in ("true", "True", "TRUE", "yes", "y", "Y", "YES", "1"))
            elif isinstance(old, float):
                globals()[nam] = float(val)
            elif isinstance(old, int):
                globals()[nam] = int(val)
            elif isinstance(old, basestring):
                globals()[nam] = val.strip()
            elif isinstance(old, list):
                globals()[nam] = val.strip().split(",")
            else:
                nam_type = type(old)
                logg.warning("(ignored) unknown target type -c '{nam}' : {nam_type}".format(**locals()))
        else:
            logg.warning("(ignored) unknown target config -c '{nam}' : no such variable".format(**locals()))

if __name__ == "__main__":
    from optparse import OptionParser
    _o = OptionParser("%%prog [-options] [%s]" % commands(),
                      epilog=re.sub("\\s+", " ", __doc__).strip())
    _o.add_option("-v", "--verbose", action="count", default=0,
                  help="increase logging level [%default]")
    _o.add_option("-D", "--docker", metavar="EXE", default=DOCKER,
                  help="use other docker exe or podman [%default]")
    _o.add_option("-V", "--ver", metavar="NUM", default=LEAP,
                  help="use other opensuse/leap version [%default]")
    _o.add_option("-c", "--config", metavar="NAME=VAL", action="append", default=[],
                  help="override globals (REPODIR, REPODATADIRS, IMAGESREPO)")
    opt, args = _o.parse_args()
    logging.basicConfig(level=logging.WARNING - opt.verbose * 10)
    config_globals(opt.config)
    DOCKER = opt.docker
    LEAP_set(opt.ver)
    #
    if not args: args = ["make"]
    for arg in args:
        if arg[0] in "123456789":
            LEAP_set(arg)
            continue
        funcname = "opensuse_" + arg.replace("-", "_")
        allnames = globals()
        if funcname in globals():
            func = globals()[funcname]
            if callable(func):
                func()
            else:
                logg.error("%s is not callable", funcname)
                sys.exit(1)
        else:
            logg.error("%s does not exist", funcname)
            sys.exit(1)
