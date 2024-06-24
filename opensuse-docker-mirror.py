#! /usr/bin/python3
""" sync packages repo to disk and make docker mirror images from it.
    Try to run 'sync' followed be 'repo'. If a command starts with a
    number then it changes the version to be handled. A usual command
    would be 'mirror.py 7.7 sync repo -v'. If no argument is given
    then 'make' the last version = 'sync pull repo test check tags'."""

__copyright__ = "(C) 2024 Guido Draheim"
__contact__ = "https://github.com/gdraheim/docker-mirror-packages-repo"
__license__ = "CC0 Creative Commons Zero (Public Domain)"
__version__ = "1.7.6261"

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

NIX = ""
IMAGESREPO = os.environ.get("IMAGESREPO", "localhost:5000/mirror-packages")
REPODATADIR = os.environ.get("REPODATADIR", "")
REPODIR = os.environ.get("REPODIR", "repo.d")

DATADIRS = [REPODATADIR,
            "/srv/docker-mirror-packages",
            "/data/docker-mirror-packages",
            "/data/docker-centos-repo-mirror",
            "/dock/docker-mirror-packages"]

OPENSUSE: Dict[str, str] = {}
OPENSUSE["13.2"] = "opensuse"  # no docker image
OPENSUSE["42.2"] = "opensuse/leap"  # docker image removed
OPENSUSE["42.3"] = "opensuse/leap"
OPENSUSE["15.0"] = "opensuse/leap"
OPENSUSE["15.1"] = "opensuse/leap"
OPENSUSE["15.2"] = "opensuse/leap"
OPENSUSE["15.3"] = "opensuse/leap"
OPENSUSE["15.4"] = "opensuse/leap"
OPENSUSE["15.5"] = "opensuse/leap"
OPENSUSE["15.6"] = "opensuse/leap"
OPENSUSE["16.0"] = "opensuse/leap"
XXLEAP: List[str] = []  # ["15.2"] # obsolete, using repodata-fix.py now
LEAP: str = "15.5"

RSYNC_SUSE1 = "rsync://suse.uni-leipzig.de/opensuse-full/opensuse"  # incomplete for 15.6
RSYNC_SUSE2 = "rsync://ftp.tu-chemnitz.de/ftp/pub/linux/opensuse"
RSYNC_SUSE3 = "rsync://mirror.cs.upb.de/opensuse"

DISTRO = "opensuse"
MIRRORS: Dict[str, List[str]] = {}
MIRRORS["opensuse"] = [RSYNC_SUSE2, RSYNC_SUSE3]

PYTHON = "python3"
RSYNC = "rsync"
DOCKER = "docker"
LAYER = "base"
RETRY = 3

BASEVERSION: Dict[str, str] = {}
BASEVERSION["15.4"] = "15.3"  # image:opensuse/base

SUBDIRS15: Dict[str, List[str]] = OrderedDict()
SUBDIRS15["distribution"] = ["oss", "non-oss"]
SUBDIRS15["update"] = ["oss", "non-oss", "backports", "sle"]

FILTERS15: Dict[str, List[str]] = OrderedDict()
FILTERS15["non-oss"] = ["strc", "nosrc"]
FILTERS15["sle"] = ["kernel-*", "eclipse-*", "cross-*"]

def opensuse_make() -> None:
    opensuse_sync()
    opensuse_repo()
    opensuse_test()

def opensuse_sync() -> None:
    opensuse_dir()
    for dist in SUBDIRS15:
        for repo in SUBDIRS15[dist]:
            if repo in FILTERS15:
                filters = FILTERS15[repo]
            else:
                filters = []
            if dist in ["distribution"]:
                opensuse_sync_repo_(dist, repo, filters)
            else:
                opensuse_sync_pack_(dist, repo, filters)  # repo may not exist (yet)

def opensuse_dir(suffix: str = "") -> str:
    distro = DISTRO
    leap = LEAP
    repodir = REPODIR
    dirname = F"{distro}.{leap}{suffix}"
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
    distro = DISTRO
    leap = LEAP
    repodir = REPODIR
    src = F"{repodir}/{distro}.{leap}/."
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

skipfiles = [
    "*.src.rpm", "*.29041k"
]

def opensuse_sync_repo_(dist: str, repo: str, filters: List[str] = []) -> None:
    distro = DISTRO
    leap = LEAP
    repodir = REPODIR
    mirror = MIRRORS[distro][0]
    rsync = RSYNC
    excludes = "".join(["""--filter="exclude %s" """ % name for name in skipdirs])
    excludes += "".join(["""--filter="exclude %s" """ % name for name in filters])
    excludes += "".join(["""--filter="exclude %s" """ % name for name in skipfiles])
    excludes += """ --size-only """
    leaprepo = F"{repodir}/{distro}.{leap}/{dist}/leap/{leap}/repo"
    if not path.isdir(leaprepo): os.makedirs(leaprepo)
    # retry:
    cmd = F"{rsync} -rv {mirror}/{dist}/leap/{leap}/repo/{repo} {leaprepo}/ {excludes}"
    logfile = F"{repodir}/{distro}.{leap}.log"
    for attempt in xrange(RETRY):
        try:
            sh___(F"set -o pipefail ; {cmd} |& tee {logfile}")
        except subprocess.CalledProcessError as e:
            logg.warning("[%s] %s", e.returncode, cmd)
            raise

def opensuse_sync_pack_(dist: str, repo: str, filters: List[str] = []) -> None:
    distro = DISTRO
    leap = LEAP
    repodir = REPODIR
    mirror = MIRRORS[distro][0]
    rsync = RSYNC
    excludes = "".join(["""--filter="exclude %s" """ % name for name in skipdirs])
    excludes += "".join(["""--filter="exclude %s" """ % name for name in filters])
    excludes += "".join(["""--filter="exclude %s" """ % name for name in skipfiles])
    excludes += """ --size-only """
    leaprepo = F"{repodir}/{distro}.{leap}/{dist}/leap/{leap}"
    if not path.isdir(leaprepo): os.makedirs(leaprepo)
    # retry:
    cmd = F"{rsync} -rv {mirror}/{dist}/leap/{leap}/{repo} {leaprepo}/ {excludes}"
    logfile = F"{repodir}/{distro}.{leap}.log"
    for attempt in xrange(RETRY):
        try:
            sh___(F"set -o pipefail ; {cmd} |& tee {logfile}")
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
    distro = DISTRO
    leap = LEAP
    repodir = REPODIR
    dirname = F"{repodir}/{distro}.{leap}{suffix}"
    basedir = dirname + "/."
    logg.info("check %s", basedir)
    if path.isdir(basedir):
        for dirpath, dirnames, filenames in os.walk(basedir):
            for filename in filenames:
                if filename.endswith(".rpm"):
                    rpm = path.join(dirpath, filename)
                    # if "tux" not in rpm: continue
                    out, end = output2(F"rpm -q --info {rpm}")
                    for line in out.splitlines():
                        if line.startswith("Group"):
                            if "/Games/" in line:
                                games[filename] = line.split(":", 1)[1].strip()
    gameslist = dirname + "-games.json"
    if games:
        json.dump(games, open(gameslist, "w"), indent=2, ensure_ascii=False, sort_keys=True)
        logg.info("found %s games, written to %s", len(games), gameslist)

opensuserepo_CMD = [F"/usr/bin/{PYTHON}", "/srv/scripts/filelist.py", "--data", "/srv/repo"]
opensuserepo_PORT = "80"
def opensuse_repo() -> None:
    python = PYTHON
    docker = DOCKER
    distro = DISTRO
    leap = LEAP
    repodir = REPODIR
    baseimage = opensuse_baseimage(distro, leap)
    scripts = repo_scripts()
    cname = F"{distro}-repo-{leap}"
    imagesrepo = IMAGESREPO
    bind_repo = ""
    base_repo = F"{repodir}/{distro}.{leap}/distribution/leap/{leap}/repo/oss"
    logg.info("/base-repo -> %s", base_repo)
    if path.isdir(base_repo):
        base_repo_path = path.abspath(base_repo)
        bind_repo = F"-v {base_repo_path}:/base-repo"
    sx___(F"{docker} rm --force {cname}")
    sh___(F"{docker} run --name={cname} {bind_repo} --detach {baseimage} sleep 9999")
    sh___(F"{docker} exec {cname} mkdir -p /srv/repo/")
    sh___(F"{docker} cp {scripts} {cname}:/srv/scripts")
    oss = "repo-oss"  # Opensuse 15.x main repo
    if bind_repo:
        oss = "local-repo"
        sh___(F"{docker} exec {cname} zypper ar --no-gpgcheck file:///base-repo {oss}")
    if True:
        sh___(F"{docker} exec {cname} zypper install -y -r {oss} {python}")
        sh___(F"{docker} exec {cname} zypper install -y -r {oss} {python}-xml")
    if leap in XXLEAP:
        sh___(F"{docker} exec {cname} zypper install -y -r {oss} createrepo")
    if bind_repo:
        sh___(F"{docker} exec {cname} zypper rr {oss}")
    CMD = str(opensuserepo_CMD).replace("'", '"')
    PORT = opensuserepo_PORT
    base = "base"
    sh___(F"{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' -m {base} {cname} {imagesrepo}/{distro}-repo/{base}:{leap}")
    dists: Dict[str, List[str]] = OrderedDict()
    # dists["mini"] = ["distribution", "-games"]
    dists["main"] = ["distribution"]
    dists["update"] = ["update"]
    for dist in dists:
        sx___(F"{docker} rm --force {cname}")
        sh___(F"{docker} run --name={cname} --detach {imagesrepo}/{distro}-repo/{base}:{leap} sleep 9999")
        clean: Dict[str, str] = {}
        for subdir in dists[dist]:
            basedir = F"{repodir}/{distro}.{leap}/."
            pooldir = F"{repodir}/{distro}.{leap}/{subdir}"
            if subdir.startswith("-"):
                gamesfile = F"{repodir}/{distro}.{leap}{subdir}.json"
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
                sh___(F"{docker} exec {cname} rm -f {removes}", debugs=False)
            elif path.isdir(pooldir):
                sh___(F"{docker} cp {pooldir} {cname}:/srv/repo/")
                base = dist
                sh___(F"{docker} exec {cname} bash -c \"find /srv/repo/{subdir} -name repomd.xml -exec {python} /srv/scripts/repodata-fix.py {{}} -v ';'\" ")
        if dist in ["update"]:
            # sh___("{docker} exec {cname} rm -r /srv/repo/{dist}/{leap}".format(**locals()))
            sh___(F"{docker} exec {cname} ln -s /srv/repo/{dist}/leap/{leap}/oss /srv/repo/{dist}/{leap}")
            if leap in XXLEAP:
                sh___(F""" {docker} exec {cname} bash -c "cd /srv/repo/{dist}/leap/{leap}/oss && createrepo ." """)
        if base == dist:
            sh___(F"{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' -m {base} {cname} {imagesrepo}/{distro}-repo/{base}:{leap}")
    sh___(F"{docker} rm --force {cname}")
    sh___(F"{docker} tag {imagesrepo}/{distro}-repo/{base}:{leap} {imagesrepo}/{distro}-repo:{leap}")
    sh___(F"{docker} rmi {imagesrepo}/{distro}-repo/base:{leap}")  # untag non-packages base

def opensuse_test() -> None:
    distro = DISTRO
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

def opensuse_image(distro: str = NIX, leap: str = NIX) -> str:
    # distro is ignored
    leap = leap or LEAP
    image = OPENSUSE[leap]
    return F"{image}:{leap}"
def opensuse_baseimage(distro: str = NIX, leap: str = NIX) -> str:
    # distro is ignored
    leap = leap or LEAP
    image = OPENSUSE[leap]
    if leap in BASEVERSION:
        leap = BASEVERSION[leap]
    return F"{image}:{leap}"

def LEAP_set(leap: str) -> str:
    global LEAP
    if len(leap) <= 2:
        LEAP = max([os for os in OPENSUSE if os.startswith(leap) and not os.startswith("42")])
        return LEAP
    if leap not in OPENSUSE:
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
                logg.warning(F"(ignored) unknown target type -c '{nam}' : {nam_type}")
        else:
            logg.warning(F"(ignored) unknown target config -c '{nam}' : no such variable")

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
                result = func()
                if isinstance(result, str):
                    print(result)
            else:
                logg.error("%s is not callable", funcname)
                sys.exit(1)
        else:
            logg.error("%s does not exist", funcname)
            sys.exit(1)
