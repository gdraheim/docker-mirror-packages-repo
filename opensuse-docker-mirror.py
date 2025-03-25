#! /usr/bin/python3
# pylint: disable=possibly-unused-variable,unused-variable,line-too-long,too-many-lines,too-many-locals,too-many-return-statements,too-many-branches,too-many-statements
# pylint: disable=consider-using-from-import,consider-using-get,consider-using-generator,consider-using-with,consider-using-in,no-else-return

""" sync packages repo to disk and make docker mirror images from it.
    Try to run 'sync' followed be 'repo'. If a command starts with a
    number then it changes the version to be handled. A usual command
    would be 'mirror.py 7.7 sync repo -v'. If no argument is given
    then 'make' the last version = 'sync pull repo test check tags'."""

__copyright__ = "(C) 2025 Guido Draheim"
__contact__ = "https://github.com/gdraheim/docker-mirror-packages-repo"
__license__ = "CC0 Creative Commons Zero (Public Domain)"
__version__ = "1.7.7121"

from typing import Optional, Dict, List, Union, Any
from collections import OrderedDict
import os
import os.path as path
import sys
import re
import subprocess
import shutil
import logging
logg = logging.getLogger("MIRROR")

NIX = ""
TRUE = 1
NOBASE = False
IMAGESREPO = os.environ.get("IMAGESREPO", "localhost:5000/mirror-packages")
REPODATADIR = os.environ.get("REPODATADIR", "")
REPODIR = os.environ.get("REPODIR", "repo.d")

DOCKERDEF = os.environ.get("DOCKER_EXE", os.environ.get("DOCKER_BIN", "docker"))
PYTHONDEF = os.environ.get("DOCKER_PYTHON", os.environ.get("DOCKER_PYTHON3", "python3"))
MIRRORDEF = os.environ.get("DOCKER_MIRROR_PY", os.environ.get("DOCKER_MIRROR",  "docker_mirror.py"))
RSYNCDEF= os.environ.get("DOCKER_RSYNC", os.environ.get("DOCKER_RSYNC3", "rsync"))

DOCKER = DOCKERDEF
PYTHON = PYTHONDEF
MIRROR = MIRRORDEF
RSYNC = RSYNCDEF

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
NEEDCREATEREPO: List[str] = []  # ["15.2"] # obsolete, using repodata-fix.py now
LEAP: str = "15.5"
VARIANT = ""

RSYNC_SUSE1 = "rsync://suse.uni-leipzig.de/opensuse-full/opensuse"  # incomplete for 15.6
RSYNC_SUSE2 = "rsync://ftp.tu-chemnitz.de/ftp/pub/linux/opensuse"
RSYNC_SUSE3 = "rsync://mirror.cs.upb.de/opensuse"

DISTRO = "opensuse"
MIRRORS: Dict[str, List[str]] = {}
MIRRORS["opensuse"] = [RSYNC_SUSE2, RSYNC_SUSE3]

# excludes [arch for arch in ARCHLIST if arch not in ARCHS]
ARCHLIST = [ "x86_64", "aarch64", "s390x", "ppc", "ppc64le" ]
ARCHS = ["x86_64"]

DISTROPYTHON = "python3"
BASELAYER = "base"
MAKEMINI = False
CREATEREPO = 0
DISKSUFFIX = "disk" # suffix
RETRY = 3

BASEVERSION: Dict[str, str] = {}
BASEVERSION["16.0"] = "15.6"  # image:opensuse/base

SUBDIRS15: Dict[str, List[str]] = OrderedDict()
SUBDIRS15["distribution"] = ["oss", "non-oss"]
SUBDIRS15["update"] = ["oss", "non-oss", "backports", "sle"]

FILTERS15: Dict[str, List[str]] = OrderedDict()
FILTERS15["oss"] = ["tftpboot-installation-*"]
FILTERS15["non-oss"] = ["strc", "nosrc"]
FILTERS15["sle"] = ["kernel-*", "eclipse-*", "cross-*"]

skipdirs = [
    "boot", "EFI", "*-boot"]

skipfiles = [
    "*.src.rpm", "*.29041k"
]

def _iterable(x: Any) -> bool: # type: ignore[misc]
    return hasattr(x, "__iter__")

def opensuse_distdirs(distro: str = NIX, leap: str = NIX) -> List[str]:  # pylint: disable=unused-argument
    return ["distribution", "update"]

def opensuse_distros(distro: str = NIX, leap: str = NIX) -> List[str]:  # pylint: disable=unused-argument
    return ["opensuse"]

######################################################

def opensuse_sync(*, variant:str = NIX) -> None:
    opensuse_dir(variant=variant)
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

def opensuse_datadir() -> str:
    for data in reversed(DATADIRS):
        logg.debug(".. check %s", data)
        if path.isdir(data):
            return data
    return REPODIR

def opensuse_dir(variant: str = "") -> str:
    distro = DISTRO
    leap = LEAP
    repodir = REPODIR
    variant = variant or VARIANT
    version = F"{leap}.{variant}" if variant else leap
    dirname = F"{distro}.{version}"
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
                os.symlink(path.abspath(dirpath), dirlink)
                break
    dircheck = path.join(dirlink, ".")
    if path.isdir(dircheck):
        logg.info("%s -> %s", dirlink, os.readlink(dirlink))
    else:
        os.mkdir(dirlink)  # local dir
        logg.warning("%s/. local dir", dirlink)
    return dirlink

def opensuse_sync_repo_(dist: str, repo: str, filters: Optional[List[str]] = None) -> None:
    filters = [] if filters is None else filters
    distro = DISTRO
    leap = LEAP
    repodir = REPODIR
    version = F"{leap}.{VARIANT}" if VARIANT else leap
    mirror = MIRRORS[distro][0]
    rsync = RSYNC
    excludes = "".join(["""--filter="exclude %s" """ % name for name in skipdirs])
    excludes += "".join(["""--filter="exclude %s" """ % name for name in filters])
    excludes += "".join(["""--filter="exclude %s" """ % name for name in skipfiles])
    excludes += "".join(["""--filter="exclude %s" """ % arch for arch in ARCHLIST if arch not in ARCHS])
    excludes += """ --size-only --copy-links """
    excludes += """ --delete"""
    leaprepo = F"{repodir}/{distro}.{version}/{dist}/leap/{leap}/repo"
    if not path.isdir(leaprepo): os.makedirs(leaprepo)
    # retry:
    cmd = F"{rsync} -rv {mirror}/{dist}/leap/{leap}/repo/{repo} {leaprepo}/ {excludes}"
    logfile = F"{repodir}/{distro}.{version}.log"
    for _attempt in range(RETRY):
        try:
            sh___(F"set -o pipefail ; {cmd} |& tee {logfile}")
        except subprocess.CalledProcessError as e:
            logg.warning("[%s] %s", e.returncode, cmd)
            raise

def opensuse_sync_pack_(dist: str, repo: str, filters: Optional[List[str]] = None) -> None:
    filters = [] if filters is None else filters
    distro = DISTRO
    leap = LEAP
    repodir = REPODIR
    version = F"{leap}.{VARIANT}" if VARIANT else leap
    mirror = MIRRORS[distro][0]
    rsync = RSYNC
    excludes = "".join(["""--filter="exclude %s" """ % name for name in skipdirs])
    excludes += "".join(["""--filter="exclude %s" """ % name for name in filters])
    excludes += "".join(["""--filter="exclude %s" """ % name for name in skipfiles])
    excludes += "".join(["""--filter="exclude %s" """ % arch for arch in ARCHLIST if arch not in ARCHS])
    excludes += """ --size-only --copy-links """
    # excludes += """ --delete"""
    leaprepo = F"{repodir}/{distro}.{version}/{dist}/leap/{leap}"
    if not path.isdir(leaprepo): os.makedirs(leaprepo)
    # retry:
    cmd = F"{rsync} -rv {mirror}/{dist}/leap/{leap}/{repo} {leaprepo}/ {excludes}"
    logfile = F"{repodir}/{distro}.{version}.log"
    for _attempt in range(RETRY):
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

opensuserepo_CMD = [F"/usr/bin/{DISTROPYTHON}", "/srv/scripts/filelist.py", "--data", "/srv/repo"]
opensuserepo_PORT = "80"
def opensuse_base() -> str:
    return opensuse_repo(True)
def opensuse_repo(onlybase: bool = False) -> str:
    python = DISTROPYTHON
    docker = DOCKER
    distro = DISTRO
    leap = LEAP
    repodir = REPODIR
    version = F"{leap}.{VARIANT}" if VARIANT else leap
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
    if TRUE:
        sh___(F"{docker} exec {cname} zypper install -y -r {oss} {python}")
        sh___(F"{docker} exec {cname} zypper install -y -r {oss} {python}-xml")
    if CREATEREPO or leap in NEEDCREATEREPO:
        sh___(F"{docker} exec {cname} bash -c 'zypper install -y -r {oss} createrepo || zypper install -y -r {oss} createrepo_c'")
    if bind_repo:
        sh___(F"{docker} exec {cname} zypper rr {oss}")
    CMD = str(opensuserepo_CMD).replace("'", '"')
    PORT = opensuserepo_PORT
    base = BASELAYER
    sh___(F"{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' -m {base} {cname} {imagesrepo}/{distro}-repo/{base}:{version}")
    dists: Dict[str, List[str]] = OrderedDict()
    if not onlybase:
        dists["main"] = ["distribution"]
        dists["update"] = ["update"]
    for dist in dists:
        sx___(F"{docker} rm --force {cname}")
        sh___(F"{docker} run --name={cname} --detach {imagesrepo}/{distro}-repo/{base}:{version} sleep 9999")
        for subdir in dists[dist]:
            basedir = F"{repodir}/{distro}.{version}/."
            pooldir = F"{repodir}/{distro}.{version}/{subdir}"
            if path.isdir(pooldir):
                sh___(F"{docker} cp {pooldir} {cname}:/srv/repo/")
                base = dist
                sh___(F"{docker} exec {cname} bash -c \"find /srv/repo/{subdir} -name repomd.xml -exec {python} /srv/scripts/repodata-fix.py {{}} -v ';'\" ")
            else:
                logg.warning("did not find pooldir %s", pooldir)
        if dist in ["update"]:
            # sh___("{docker} exec {cname} rm -r /srv/repo/{dist}/{leap}".format(**locals()))
            sh___(F"{docker} exec {cname} ln -s /srv/repo/{dist}/leap/{leap}/oss /srv/repo/{dist}/{leap}")
            if CREATEREPO or leap in NEEDCREATEREPO:
                sh___(F""" {docker} exec {cname} bash -c "cd /srv/repo/{dist}/leap/{leap}/oss && rm -rv repodata" """)
                sh___(F""" {docker} exec {cname} bash -c "cd /srv/repo/{dist}/leap/{leap}/oss && createrepo ." """)
        if base == dist:
            sh___(F"{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' -m {base} {cname} {imagesrepo}/{distro}-repo/{base}:{version}")
    sh___(F"{docker} rm --force {cname}")
    if base != BASELAYER:
        sh___(F"{docker} tag {imagesrepo}/{distro}-repo/{base}:{version} {imagesrepo}/{distro}-repo:{version}")
    if NOBASE:
        sh___(F"{docker} rmi {imagesrepo}/{distro}-repo/base:{version}")  # untag non-packages base
    return F"\n[{baseimage}]\nimage = {imagesrepo}/{distro}-repo/{base}:{version}\n"

def opensuse_baserepo(distro: str = NIX, leap: str = NIX, imagesrepo: str = NIX) -> str:
    imagesrepo = imagesrepo or IMAGESREPO
    distro = distro or DISTRO
    leap = leap or LEAP
    version = F"{leap}.{VARIANT}" if VARIANT else leap
    base = BASELAYER
    return F"{imagesrepo}/{distro}-repo/{base}:{version}"
def opensuse_mainrepo(distro: str = NIX, leap: str = NIX, imagesrepo: str = NIX) -> str:
    imagesrepo = imagesrepo or IMAGESREPO
    distro = distro or DISTRO
    leap = leap or LEAP
    version = F"{leap}.{VARIANT}" if VARIANT else leap
    base = BASELAYER
    return F"{imagesrepo}/{distro}-repo/{base}:{version}"

def opensuse_local(distro: str = NIX, centos: str = NIX) -> str:
    """ show ini section for diskpath and --epel """
    mainsection = opensuse_baseimage(distro, centos)
    mainbaseimage = opensuse_baserepo(distro, centos)
    maindiskpath = opensuse_diskpath()
    return F"[{mainsection}]\nimage={mainbaseimage}\nmount={maindiskpath}"

def opensuse_list(distro: str = NIX, leap: str = NIX) -> int:
    docker = DOCKER
    print(F"REPOSITORY:TAG\tSIZE          # {docker} images {{baseimage}} {{baserepo}} {{mainrepo}}")
    baseimage = opensuse_baseimage(distro, leap)
    logg.debug("docker image list %s", baseimage)
    cmd = F"{docker} image list {baseimage} -q --format '{{{{.Repository}}}}:{{{{.Tag}}}}\t{{{{.Size}}}}'"
    sx1 = sx___(cmd)
    baserepo = opensuse_baserepo(distro, leap)
    logg.debug("docker image list %s", baserepo)
    cmd = F"{docker} image list {baserepo} -q --format '{{{{.Repository}}}}:{{{{.Tag}}}}\t{{{{.Size}}}}'"
    sx2 = sx___(cmd)
    mainrepo = opensuse_mainrepo(distro, leap)
    logg.debug("docker image list %s", mainrepo)
    cmd = F"{docker} image list {mainrepo} -q --format '{{{{.Repository}}}}:{{{{.Tag}}}}\t{{{{.Size}}}}'"
    sx3 = sx___(cmd)
    return min(sx1, sx2, sx3)

def opensuse_disk(onlybase: bool = False) -> str:
    createrepo = find_path("createrepo")
    docker = DOCKER
    distro = DISTRO
    leap = LEAP
    repodir = REPODIR
    imagesrepo = IMAGESREPO
    scripts = repo_scripts()
    version = F"{leap}.{VARIANT}" if VARIANT else leap
    rootdir = opensuse_dir(variant=F"{VARIANT}{DISKSUFFIX}")
    srv = F"{rootdir}/srv"
    logg.info("srv = %s", srv)
    dists: Dict[str, List[str]] = OrderedDict()
    if not onlybase:
        # dists["mini"] = ["distribution", "-games"]
        dists["main"] = ["distribution"]
        dists["update"] = ["update"]
    sh___(F"test ! -d {srv} || rm -rf {srv}")
    sh___(F"mkdir -p {srv}/repo")
    for dist in dists:
        for subdir in dists[dist]:
            pooldir = F"{repodir}/{distro}.{version}/{subdir}"
            if path.isdir(pooldir):
                sh___(F"cp -r --link --no-clobber {pooldir} {srv}/repo/")
                sh___(F"find {srv}/repo/{subdir} -name repomd.xml -exec {scripts}/repodata-fix.py {{}} -v ';' ")
            else:
                logg.warning("no such pooldir: %s", pooldir)
            if CREATEREPO > 1:
                logg.info("running createrepo for main parts is about fixing upstream bugs")
                if createrepo:
                    sh___(F" cd {srv}/repo/{subdir}/leap/{leap}/oss && {createrepo} . -v ")
        if dist in ["update"]:
            # sh___("{docker} exec {cname} rm -r /srv/repo/{dist}/{leap}".format(**locals()))
            sh___(F"ln -s {srv}/repo/{dist}/leap/{leap}/oss {srv}/repo/{dist}/{leap}")
            logg.info("running createrepo is obsolete as repodata-fix.py can handle everything (except %s)", NEEDCREATEREPO)
            if CREATEREPO or leap in NEEDCREATEREPO:
                if createrepo:
                    sh___(F" cd {srv}/repo/{dist}/leap/{leap}/oss && {createrepo} . ")
                else:
                    baseimage = F"{imagesrepo}/{distro}-repo/base:{version}"
                    host_uid = os.getuid()
                    host_srv = os.path.abspath(srv)
                    sh___(F""" rm  -rv {host_srv}/repo/{dist}/leap/{leap}/oss/repodata """)
                    sh___(F"""{docker} run --rm=true -t -v {host_srv}:/srv -u {host_uid} --userns=host {baseimage} bash -c "cd /srv/repo/{dist}/leap/{leap}/oss && createrepo --workers=1 --verbose ." """)
    path_srv = os.path.realpath(srv)
    return F"\nmount = {path_srv}/repo\n"

def opensuse_diskpath() -> str:
    rootdir = opensuse_dir(variant=F"{VARIANT}{DISKSUFFIX}")
    srv = F"{rootdir}/srv"
    path_srv = os.path.realpath(srv)
    return F"{path_srv}/repo\n"

def opensuse_dropdisk() -> str:
    rootdir = opensuse_dir(variant=F"{VARIANT}{DISKSUFFIX}")
    srv = F"{rootdir}/srv"
    path_srv = os.path.realpath(srv)
    if os.path.isdir(path_srv):
        shutil.rmtree(path_srv)
    return path_srv

def find_path(exe: str, default: str = NIX) -> str:
    for dirpath in os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"):
        filepath = os.path.join(dirpath, exe)
        if os.path.exists(filepath):
            return filepath
    return default

def opensuse_scripts() -> None:
    print(repo_scripts())
def repo_scripts() -> str:
    me = os.path.dirname(sys.argv[0]) or "."
    dn = os.path.join(me, "scripts")
    if os.path.isdir(dn): return dn
    dn = os.path.join(me, "docker_mirror/scripts")
    if os.path.isdir(dn): return dn
    dn = os.path.join(me, "../docker_mirror/scripts")
    if os.path.isdir(dn): return dn
    dn = os.path.join(me, "../share/docker_mirror/scripts")
    if os.path.isdir(dn): return dn
    logg.error("%s -> %s", sys.argv[0], me)
    return "scripts"

#############################################################################

def sh___(cmd: Union[str, List[str]], debugs: bool = True) -> int:
    """ shell=True if string (and raises signal on returncode) """
    shell = False
    if isinstance(cmd, str):
        shell = True
        if debugs:
            logg.info(": %s", cmd)
    else:
        if debugs:
            logg.info(": %s", " ".join(["'%s'" % item for item in cmd]))
    return -(subprocess.check_call(cmd, shell=shell)) # does only return 0

def sx___(cmd: Union[str, List[str]], debugs: bool = True) -> int:
    """ shell=True if string and returns negative returncode """
    shell = False
    if isinstance(cmd, str):
        shell = True
        if debugs:
            logg.info(": %s", cmd)
    else:
        if debugs:
            logg.info(": %s", " ".join(["'%s'" % item for item in cmd]))
    return -(subprocess.call(cmd, shell=shell))

#############################################################################

def path_find(base: str, name: str) -> Optional[str]:
    for dirpath, _dirnames, filenames in os.walk(base):
        if name in filenames:
            return path.join(dirpath, name)
    return None

def opensuse_image(distro: str = NIX, leap: str = NIX) -> str:
    distro = distro or DISTRO # distro is ignored
    leap = leap or LEAP
    image = OPENSUSE[leap]
    return F"{image}:{leap}"
def opensuse_baseimage(distro: str = NIX, leap: str = NIX) -> str:
    distro = distro or DISTRO # distro is ignored
    leap = leap or LEAP
    image = OPENSUSE[leap]
    if leap in BASEVERSION:
        leap = BASEVERSION[leap]
    return F"{image}:{leap}"
def opensuse_pull(distro: str = NIX, leap: str = NIX) -> str:
    docker = DOCKER
    baseimage = opensuse_baseimage(distro, leap)
    sh___(F"""{docker} pull {baseimage} """)
    return baseimage

def opensuse_version(distro: str = NIX, leap: str = NIX) -> str:
    distro = distro or DISTRO  # distro is (almost) ignored
    leap = leap or LEAP
    if distro not in MIRRORS:
        logg.warning("unknown distro '%s'", distro)
    if len(leap) <= 2:
        return max([os for os in OPENSUSE if os.startswith(leap) and not os.startswith("42")])
    if leap not in OPENSUSE:
        logg.warning("%s is not a known os version", leap)
    return leap
def LEAP_set(leap: str) -> str:
    global LEAP # pylint: disable=global-statement
    LEAP = opensuse_version(leap=leap)
    return LEAP

def opensuse_commands() -> str:
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

def _main(args: List[str]) -> int:
    for arg in args:
        if arg[0] in "123456789":
            LEAP_set(arg)
            continue
        if ":" in arg and arg.split(":", 1)[1][0] in "123456789":
            LEAP_set(arg)
            continue
        funcname = "opensuse_" + arg.replace("-", "_")
        allnames = globals()
        if funcname in allnames:
            funcdefinition = globals()[funcname]
            if callable(funcdefinition):
                funcresult = funcdefinition()
                if isinstance(funcresult, str):
                    print(funcresult)
                elif isinstance(funcresult, int):
                    print(" %i2" % funcresult)
                    if funcresult < 0:
                        return -funcresult
                elif _iterable(funcresult):
                    for item in funcresult:
                        print(str(item))
            else: # pragma: nocover
                logg.error("%s is not callable", funcname)
                return 1
        else:
            logg.error("%s does not exist", funcname)
            return 1
    return 0

if __name__ == "__main__":
    from optparse import OptionParser # allow_abbrev=False, pylint: disable=deprecated-module
    cmdline = OptionParser("%%prog [-options] [%s]" % opensuse_commands(),
                      epilog=re.sub("\\s+", " ", __doc__).strip())
    cmdline.formatter.max_help_position = 30
    cmdline.add_option("-v", "--verbose", action="count", default=0, help="more logging level [%default]")
    cmdline.add_option("-^", "--quiet", action="count", default=0, help="less verbose logging [%default]")
    cmdline.add_option("->", "--mirror", metavar="PY", default=MIRROR, help="different path to [%default]")
    cmdline.add_option("-P", "--python", metavar="EXE", default=PYTHON, help="alternative to [%default] (=python3.11)")
    cmdline.add_option("-D", "--docker", metavar="EXE", default=DOCKER,   help="alternative to [%default] (e.g. podman)")
    cmdline.add_option("--rsync", metavar="EXE", default=RSYNC, help="alternative to [%default]")
    cmdline.add_option("--distropython", metavar="EXE", default=DISTROPYTHON,  help="alternative to ./scripts [%default] runner")
    cmdline.add_option("-R", "--nobase", action="store_true", default=NOBASE,
                       help="rm */base when repo image is ready [%default]")
    cmdline.add_option("--repodir", metavar="DIR", default=REPODIR,
                       help="set $REPODIR [%default]")
    cmdline.add_option("--datadir", metavar="DIR", default=REPODATADIR,
                       help="set $REPODATADIR -> "+(REPODATADIR if REPODATADIR else opensuse_datadir()))
    cmdline.add_option("--imagesrepo", metavar="PREFIX", default=IMAGESREPO,
                       help="set $IMAGESREPO [%default]")
    cmdline.add_option("--disksuffix", metavar="NAME", default=DISKSUFFIX,
                       help="use disk suffix for testing [%default]")
    cmdline.add_option("-W", "--variant", metavar="NAME", default=VARIANT,
                       help="use variant suffix for testing [%default]")
    cmdline.add_option("-V", "--ver", metavar="NUM", default=LEAP,
                       help="use other opensuse/leap version [%default]")
    cmdline.add_option("-a", "--arch", metavar="NAME", action="append", default=[],
                       help=F"use other arch list {ARCHS}")
    cmdline.add_option("--createrepo", action="count", default=CREATEREPO,
                       help="force createrepo on 'update' packages [%default]")
    cmdline.add_option("--mini", action="store_true", default=MAKEMINI,
                       help="make /mini repo layer [%default]")
    opt, cmdline_args = cmdline.parse_args()
    logging.basicConfig(level=logging.WARNING - opt.verbose * 10 + opt.quiet * 10)
    CREATEREPO = opt.createrepo
    MAKEMINI = opt.mini
    if opt.arch:
        cmdline_badarchs = [arch for arch in opt.arch if arch not in ARCHLIST]
        if cmdline_badarchs:
            logg.error("unknown arch %s (from known %s)", cmdline_badarchs, ARCHLIST)
            sys.exit(1)
        ARCHS = opt.arch
    REPODIR = opt.repodir
    if opt.datadir:
        REPODATADIR = opt.datadir
        DATADIRS = [ REPODATADIR ]
    IMAGESREPO = opt.imagesrepo
    DISKSUFFIX = opt.disksuffix
    VARIANT = opt.variant
    NOBASE = opt.nobase
    DOCKER = opt.docker
    RSYNC = opt.rsync
    DISTROPYTHON = opt.python
    LEAP_set(opt.ver)
    sys.exit(_main(cmdline_args or ["list"]))
