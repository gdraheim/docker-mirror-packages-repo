#! /usr/bin/python3
""" sync packages repo to disk and make docker mirror images from it.
    Try to run 'sync' followed be 'repo'. If a command starts with a
    number then it changes the version to be handled. A usual command
    would be 'mirror.py 7.7 sync repo -v'. If no argument is given
    then 'make' the last version = 'sync pull repo test check tags'.
    ((with ''epelsync'' and ''epelrepo'' you can also take a snapshot
     from the fedora epel repos (which do not have real releases)))."""

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
import subprocess
import shutil
import datetime
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

BASE: Dict[str, str] = {}
BASE["8.5.2111"] = "8.5"
BASE["8.4.2105"] = "8.4"
BASE["8.3.2011"] = "8.3"
BASE["8.2.2004"] = "8.2"
BASE["8.1.1911"] = "8.1"
BASE["8.0.1905"] = "8.0"
BASE["7.9.2009"] = "7.9"
BASE["7.8.2003"] = "7.8"
BASE["7.7.1908"] = "7.7"
BASE["7.6.1810"] = "7.6"
BASE["7.5.1804"] = "7.5"
BASE["7.4.1708"] = "7.4"
BASE["7.3.1611"] = "7.3"
BASE["7.2.1511"] = "7.2"
BASE["7.1.1503"] = "7.1"
BASE["7.0.1406"] = "7.0"

ALMA: Dict[str, str] = {}
ALMA["8.8-20230524"] = "8.8"
ALMA["8.8-20230718"] = "8.8"
ALMA["8.9-20231124"] = "8.9"
ALMA["8.9-20240410"] = "8.9"
ALMA["8.10-20240528"] = "8.10"
ALMA["9.0-20220706"] = "9.0"
ALMA["9.0-20220901"] = "9.0"
ALMA["9.0-20221001"] = "9.0"
ALMA["9.0-20221102"] = "9.0"
ALMA["9.1-20221117"] = "9.1"
ALMA["9.1-20221201"] = "9.1"
ALMA["9.1-20230222"] = "9.1"
ALMA["9.1-20230407"] = "9.1"
ALMA["9.2-20230512"] = "9.2"
ALMA["9.2-20230718"] = "9.2"
ALMA["9.3-20231124"] = "9.3"
ALMA["9.3-20240410"] = "9.3"
ALMA["9.4-20240506"] = "9.4"
ALMA["9.4-20240530"] = "9.4"

CENTOS = "9.3-20240410"
ARCH = "x86_64"

DOCKER = "docker"
RSYNC = "rsync"

CENTOS_MIRROR = "rsync://rsync.hrz.tu-chemnitz.de/ftp/pub/linux/centos"
# "http://ftp.tu-chemnitz.de/pub/linux/centos/"

# #### basearch=x86_64
# ##baseurl=http://download.fedoraproject.org/pub/epel/7/$basearch
# #metalink=https://mirrors.fedoraproject.org/metalink?repo=epel-7&arch=$basearch
#  http://fedora.tu-chemnitz.de/pub/linux/fedora-epel/7/x86_64/debug/repodata/repomd.xml
# rsync://fedora.tu-chemnitz.de/ftp/pub/linux/fedora-epel/7/x86_64/debug/repodata/repomd.xml
EPEL_MIRROR = "rsync://fedora.tu-chemnitz.de/ftp/pub/linux/fedora-epel"

# https://mirrors.almalinux.org/isos/x86_64/9.0.html
ALMALINUX_MIRROR = "rsync://ftp.gwdg.de/almalinux"

MIRRORS: Dict[str, List[str]] = {}
MIRRORS["centos"] = [CENTOS_MIRROR]
MIRRORS["epel"] = [EPEL_MIRROR]
MIRRORS["almalinux"] = [ALMALINUX_MIRROR]
DISTRO = "centos"
EPEL = "epel"
ALMALINUX = "almalinux"

_SUBDIRS: Dict[str, List[str]] = {}
_SUBDIRS["9.3"] = ["AppStream", "BaseOS", "devel", "extras", "plus", "CRB",
                   "cloud", "HighAvailibility",
                   "NFV", "RT", "ResilientStorage", "SAP", "SAPHANA", "rasperrypi", "synergy"]
_SUBDIRS["8.5"] = ["AppStream", "BaseOS", "Devel", "extras", "PowerTools", "centosplus",
                   "cloud", "configmanagement", "cr", "fasttrack", "HighAvailibility",
                   "infra", "messages", "nfv", "opstools", "storage", "virt", ]
_SUBDIRS["7.9"] = ["os", "updates", "extras", "sclo", "centosplus", "atomic",
                   "cloud", "configmanagement", "cr", "dotnet", "fasttrack",
                   "infra", "messages", "nfv", "opstools", "paas", "rt", "storage", "virt", ]

# docker-mirror.py can select from "main" to "sclo" which however is the default.

SUBDIRS9: Dict[str, List[str]] = OrderedDict()
SUBDIRS9["main"] = ["BaseOS", "AppStream", "extras"]
SUBDIRS9["plus"] = ["CRB", "plus"]  # ALMALINUX
#SUBDIRS9["dev"] = ["devel", "HighAvailibility"]

SUBDIRS8: Dict[str, List[str]] = OrderedDict()
SUBDIRS8["main"] = ["BaseOS", "AppStream", "extras"]
SUBDIRS8["plus"] = ["PowerTools", "centosplus"]
#SUBDIRS8["dev"] = ["Devel", "HighAvailibility"]

SUBDIRS7: Dict[str, List[str]] = OrderedDict()
SUBDIRS7["main"] = ["os", "extras", "updates"]
SUBDIRS7["plus"] = ["centosplus"]
SUBDIRS7["sclo"] = ["sclo"]

SUBDIRS6: Dict[str, List[str]] = OrderedDict()
SUBDIRS6["main"] = ["os", "updates"]
SUBDIRS6["sclo"] = ["sclo"]

BASEVERSIONS: Dict[str, str] = {}
BASEVERSIONS["8.5.2111"] = "8.4.2105"  # image:centos/base

#############################################################################

def major(version: str) -> str:
    version = version or CENTOS
    if len(version) == 1 or version[1] in ".-":
        return version[0]
    return version[:1]
def majorminor(version: str) -> str:
    version = version or CENTOS
    if len(version) == 3 or version[3] in ".-":
        return version[:3]
    if len(version) == 4 or version[4] in ".-":
        return version[:4]
    return version[:3]

def centos_epel() -> None:
    centos_epeldir()
    centos_epelsync()
    centos_epelrepo()

def centos_make() -> None:
    centos_sync()
    centos_pull()
    centos_repo()
    centos_test()
    centos_check()
    centos_tags()

def centos_release(distro: str = NIX, centos: str = NIX) -> str:
    """ this is a short version for the repo image"""
    distro = distro or DISTRO
    centos = centos or CENTOS
    if "-" in centos:
        release, _ = centos.split("-", 1)
        return release
    return centos

def centos_baseversion(distro: str = NIX, centos: str = NIX) -> str:
    """ this is a long version for the base image"""
    distro = distro or DISTRO
    centos = centos or CENTOS
    if centos in BASE:
        return centos
    if centos in BASE.values():
        return max([os for os in BASE if BASE[os] == centos])
    if centos in ALMA.values():
        return max([os for os in ALMA if ALMA[os] == centos])
    return centos

def centos_pull() -> None:
    docker = DOCKER
    distro = DISTRO
    centos = CENTOS
    release = centos_baseversion(docker, centos)
    if release in BASEVERSIONS:
        release = BASEVERSIONS[release]
    if release.startswith("7"):
        sh___(F"{docker} pull centos:{release}")
        if release != centos:
            sh___(f"{docker} tag centos:{release} centos:{centos}")
    if release.startswith("8"):
        sh___(F"{docker} pull centos:{release}")
        if release != centos:
            sh___(f"{docker} tag centos:{release} centos:{centos}")
    if release.startswith("9"):
        sh___(F"{docker} pull almalinux:{release}")
        if release in ALMA:
            centos = ALMA[release]
        if release != centos:
            sh___(f"{docker} tag almalinux:{release} almalinux:{centos}")

def centos_dir(suffix: str = "") -> str:
    distro = DISTRO
    centos = CENTOS
    return distro_dir(distro, centos, suffix)
def centos_epeldir(suffix: str = "") -> str:
    distro = EPEL
    centos = CENTOS
    return distro_dir(distro, centos, suffix)
def distro_dir(distro: str, release: str, suffix: str = "") -> str:
    # distro = DISTRO
    repodir = REPODIR
    dirname = F"{distro}.{release}{suffix}"
    dirlink = path.join(repodir, dirname)
    if not path.isdir(repodir):
        os.mkdir(repodir)
    if "-" in release:
        major, dated = release.split("-", 1)
        oldname = F"{distro}.{major}{suffix}"
        oldlink = path.join(repodir, oldname)
        if path.isdir(oldlink) and not path.exists(dirlink):
            logg.info("%s >> %s", oldlink, dirlink)
            os.symlink(oldname, dirlink)
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

CENTOS_XXX = " ".join([
    "--exclude ppc64le",
    "--exclude aarch64",
    "--exclude s390x",
    "--exclude EFI",
    "--exclude images",
    "--exclude isolinux",
    "--exclude '*.iso'",
])

def centos_sync() -> None:
    distro = DISTRO
    centos = CENTOS
    centos_dir()
    subdirs: Dict[str, List[str]] = OrderedDict()
    if centos.startswith("6"):
        subdirs = SUBDIRS6
    if centos.startswith("7"):
        subdirs = SUBDIRS7
    if centos.startswith("8"):
        subdirs = SUBDIRS8
    if centos.startswith("9"):
        subdirs = SUBDIRS9
    for base in subdirs:
        for subdir in subdirs[base]:
            logg.info(F"#### [{base}] /{subdir}")
            distro_sync_subdir(distro, centos, subdir)
            logg.info(F"DONE [{base}] /{subdir}")

def centos_mirror(distro: str = NIX, centos: str = NIX) -> str:
    return distro_mirror(distro, centos)
def distro_mirror(distro: str, centos: str) -> str:
    distro = distro or DISTRO
    centos = centos or CENTOS
    return MIRRORS[distro][0]

def distro_sync_subdir(distro: str, centos: str, subdir: str) -> None:
    # distro = DISTRO
    rsync = RSYNC
    distro = distro or DISTRO
    centos = centos or CENTOS
    centos2 = majorminor(centos)
    mirror = distro_mirror(distro, centos)
    excludes = CENTOS_XXX
    repodir = REPODIR
    sh___(F"{rsync} -rv {mirror}/{centos2}/{subdir}   {repodir}/{distro}.{centos2}/ {excludes}")

def centos_sync_AppStream() -> None: distro_sync_subdir(DISTRO, CENTOS, "AppStream")
def centos_sync_BaseOS() -> None: distro_sync_subdir(DISTRO, CENTOS, "BaseOS")
def centos_sync_os() -> None: distro_sync_subdir(DISTRO, CENTOS, "os")
def centos_sync_extras() -> None: distro_sync_subdir(DISTRO, CENTOS, "extras")
def centos_sync_PowerTools() -> None: distro_sync_subdir(DISTRO, CENTOS, "PowerTools")
def centos_sync_centosplus() -> None: distro_sync_subdir(DISTRO, CENTOS, "centosplus")
def centos_sync_updates() -> None: distro_sync_subdir(DISTRO, CENTOS, "updates")
def centos_sync_sclo() -> None: distro_sync_subdir(DISTRO, CENTOS, "sclo")

def centos_epelsync(distro: str = NIX, centos: str = NIX) -> None:
    distro = distro or DISTRO
    centos = centos or CENTOS
    if centos.startswith("9"):
        return centos_epelsync9()
    if centos.startswith("8"):
        return centos_epelsync8()
    if centos.startswith("7"):
        return centos_epelsync7()
    raise RuntimeWarning("unknown CENTOS %s" % centos)

def centos_epelsync9(distro: str = NIX, centos: str = NIX) -> None:
    distro = distro or EPEL
    centos = centos or CENTOS
    distro_epelsyncs(distro, centos, ["Everything"])
def centos_epelsync8(distro: str = NIX, centos: str = NIX) -> None:
    distro = distro or EPEL
    centos = centos or CENTOS
    distro_epelsyncs(distro, centos, ["Everything", "Modular"])
def centos_epelsync7(distro: str = NIX, centos: str = NIX) -> None:
    distro = distro or EPEL
    centos = centos or CENTOS
    distro_epelsyncs(distro, centos, [])
def distro_epelsyncs(distro: str, centos: str, subdirs: List[str] = []) -> str:
    distro = distro or EPEL
    centos = centos or CENTOS
    rsync = RSYNC
    mirror = MIRRORS[distro][0]
    epel = major(centos)
    arch = ARCH
    repo = distro_dir(distro, epel)
    excludes = """ --exclude "*.iso" """
    if subdirs:
        for subdir in subdirs:
            basedir = F"{repo}/{epel}/{subdir}"
            if not path.isdir(basedir):
                os.makedirs(basedir)
            sh___(F"{rsync} -rv {mirror}/{epel}/{subdir}/{arch} {basedir}/ {excludes}")
    else:
        basedir = F"{repo}/{epel}"
        sh___(F"{rsync} -rv {mirror}/{epel}/{arch} {basedir}/ {excludes}")
    return F"epel.{epel}/{epel}"

def centos_unpack() -> None:
    """ used while testing if centos had all packages """
    docker = DOCKER
    distro = DISTRO
    centos = CENTOS
    R = major(centos)
    repodir = REPODIR
    cname = "centos-unpack-" + centos  # container name
    image = F"localhost:5000/{distro}-repo"
    sx___(F"{docker} rm --force {cname}")
    sh___(F"{docker} run --name={cname} --detach {image}:{centos} sleep 9999")
    sh___(F"{docker} cp {cname}:/srv/repo/{R}/os {repodir}/{distro}.{centos}/")
    sh___(F"{docker} cp {cname}:/srv/repo/{R}/extras {repodir}/{distro}.{centos}/")
    sh___(F"{docker} cp {cname}:/srv/repo/{R}/updates {repodir}/{distro}.{centos}/")
    sh___(F"{docker} cp {cname}:/srv/repo/{R}/sclo {repodir}/{distro}.{centos}/")
    sh___(F"{docker} rm --force {cname}")
    sh___(F"du -sh {repodir}/{distro}.{centos}/.")

def centos_clean() -> None:
    """ when moving from centos:7 to centos:8 """
    distro = DISTRO
    centos = CENTOS
    repodir = REPODIR
    for subdir in ["os", "extras", "updates", "sclo"]:
        sh___(F"rm -rf {repodir}/{distro}.{centos}/{subdir}")

def centos_epelrepo(distro: str = NIX, centos: str = NIX) -> None:
    distro = distro or EPEL
    centos = centos or CENTOS
    if centos.startswith("9"):
        return centos_epelrepo9(distro, centos)
    if centos.startswith("8"):
        return centos_epelrepo8(distro, centos)
    if centos.startswith("7"):
        return centos_epelrepo7(distro, centos)
    raise RuntimeWarning("unknown CENTOS %s" % centos)

MAKE_EPEL_HTTP = True
def centos_epelrepo9(distro: str = NIX, centos: str = NIX) -> None:
    distro = distro or EPEL
    centos = centos or CENTOS
    dists: Dict[str, List[str]] = OrderedDict()
    dists["main"] = ["Everything"]
    distro_epelrepos(distro, centos, dists)
def centos_epelrepo8(distro: str = NIX, centos: str = NIX) -> None:
    distro = distro or EPEL
    centos = centos or CENTOS
    dists: Dict[str, List[str]] = OrderedDict()
    dists["main"] = ["Everything"]
    dists["plus"] = ["Modular"]
    distro_epelrepos(distro, centos, dists)

def centos_epeldate(distro: str = "", centos: str = "", repodir: str = "") -> Optional[datetime.datetime]:
    distro = distro or EPEL
    centos = centos or CENTOS
    epel = major(centos)
    repodir = repodir or REPODIR
    epeldir = F"{repodir}/{distro}.{epel}/{epel}"
    latest = None
    for root, dirs, files in os.walk(epeldir):
        for name in files:
            filename = os.path.join(root, name)
            changed = os.path.getmtime(filename)
            if not latest:
                latest = changed
            elif latest < changed:
                latest = changed
    if not latest:
        return None
    else:
        epeldate = datetime.datetime.fromtimestamp(latest)
        logg.info("epeldate = %s", epeldate)
        return epeldate

def distro_epelrepos(distro: str, centos: str, dists: Dict[str, List[str]]) -> None:
    distro = distro or EPEL
    centos = centos or CENTOS
    repodir = REPODIR
    docker = DOCKER
    epel = major(centos)
    arch = ARCH
    scripts = repo_scripts()
    cname = F"{distro}-repo-{epel}"
    baseimage = centos_baseimage(DISTRO, centos)
    out, end = output2(F"./docker_mirror.py start {baseimage} -a")
    addhosts = out.strip()
    PORT = centos_epel_port(distro, centos)
    CMD = str(centos_epel_cmd(distro, centos)).replace("'", '"')
    sx___(F"{docker} rm --force {cname}")
    sh___(F"{docker} run --name={cname} {addhosts} --detach {baseimage} sleep 9999")
    if PORT != 80:
        sh___(F"{docker} exec {cname} bash -c 'echo sslverify=false >> /etc/yum.conf'")
        sh___(F"{docker} exec {cname} yum install -y openssl")
    sh___(F"{docker} exec {cname} mkdir -p /srv/repo/epel/{epel}")
    sh___(F"{docker} cp {scripts} {cname}:/srv/scripts")
    if False:
        # instead we use an explicit epelrepo8_CMD
        for script in os.listdir(F"{scripts}/."):
            sh___(F"{docker} exec {cname} sed -i s:/usr/bin/python3:/usr/libexec/platform-python: /srv/scripts/{script}")
            sh___(F"{docker} exec {cname} chmod +x /srv/scripts/{script}")
    base = "base"
    repo = IMAGESREPO
    latest = centos_epeldate(distro, centos, repodir) or datetime.date.today()
    yymm = latest.strftime("%y%m")
    sh___(F"{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' -m {base} {cname} {repo}/{distro}-repo/{base}:{epel}.x.{yymm}")
    for dist in dists:
        sx___(F"{docker} rm --force {cname}")
        sh___(F"{docker} run --name={cname} --detach {repo}/{distro}-repo/{base}:{epel}.x.{yymm} sleep 9999")
        for subdir in dists[dist]:
            sh___(F"{docker} cp {repodir}/{distro}.{epel}/{epel}/{subdir} {cname}:/srv/repo/epel/{epel}/")
            base = dist  # !!
        if base == dist:
            sh___(F"{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' -m {base} {cname} {repo}/{distro}-repo/{base}:{epel}.x.{yymm}")
    sh___(F"{docker} tag {repo}/{distro}-repo/{base}:{epel}.x.{yymm} {repo}/{distro}-repo:{epel}.x.{yymm}")
    sx___(F"{docker} rm --force {cname}")
    sh___(F"{docker} rmi {repo}/{distro}-repo/base:{epel}.x.{yymm}")
    PORT2 = centos_epel_http_port(distro, centos)
    CMD2 = str(centos_epel_http_cmd(distro, centos)).replace("'", '"')
    if PORT != PORT2:
        # the upstream epel repository runs on https by default but we don't have their certificate anyway
        base2 = "http"  # !!
        sh___(F"{docker} run --name={cname} --detach {repo}/{distro}-repo:{epel}.x.{yymm} sleep 9999")
        sh___(F"{docker} commit -c 'CMD {CMD2}' -c 'EXPOSE {PORT2}' -m {base2} {cname} {repo}/{distro}-repo/{base2}:{epel}.x.{yymm}")
        sx___(F"{docker} rm --force {cname}")

def centos_epelrepo7(distro: str = NIX, centos: str = NIX) -> None:
    distro = distro or EPEL
    centos = centos or CENTOS
    repodir = REPODIR
    docker = DOCKER
    epel = major(centos)
    arch = ARCH
    scripts = repo_scripts()
    cname = F"{distro}-repo-{epel}"  # container name
    PORT = centos_epel_port(distro, centos)
    CMD = str(centos_epel_cmd(distro, centos)).replace("'", '"')
    sx___(F"{docker} rm --force {cname}")
    sh___(F"{docker} run --name={cname} --detach centos:{centos} sleep 9999")
    sh___(F"{docker} exec {cname} mkdir -p /srv/repo/epel")
    if PORT != 80:
        sh___(F"{docker} exec {cname} yum install -y openssl")
    sh___(F"{docker} cp {scripts} {cname}:/srv/scripts")
    for script in os.listdir(f"{scripts}/."):
        sh___(F"{docker} exec {cname} chmod +x /srv/scripts/{script}")
    #
    repo = IMAGESREPO
    latest = centos_epeldate(distro, centos, repodir) or datetime.date.today()
    yymm = latest.strftime("%y%m")
    sh___(F"{docker} cp {repodir}/{distro}.{epel}/{epel} {cname}:/srv/repo/epel/")
    sh___(F"{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' {cname} {repo}/{distro}-repo:{epel}.x.{yymm}")
    sh___(F"{docker} rm --force {cname}")
    if MAKE_EPEL_HTTP:
        PORT2 = centos_epel_http_port(distro, centos)
        CMD2 = str(centos_epel_http_cmd(distro, centos)).replace("'", '"')
        base2 = "http"  # !!
        # the upstream epel repository runs on https by default but we don't have their certificate anyway
        sh___(F"{docker} run --name={cname} --detach {repo}/{distro}-repo:{epel}.x.{yymm} sleep 999")
        sh___(F"{docker} commit -c 'CMD {CMD2}' -c 'EXPOSE {PORT2}' {cname} {repo}/{distro}-repo/{base2}:{epel}.x.{yymm}")
        sh___(F"{docker} rm --force {cname}")

def centos_epel_port(distro: str = NIX, centos: str = NIX) -> int:
    distro = distro or DISTRO
    centos = centos or CENTOS
    return 443
def centos_epel_cmd(distro: str = NIX, centos: str = NIX) -> List[str]:
    distro = distro or DISTRO
    centos = centos or CENTOS
    python = centos_python(distro, centos)
    return [python, "/srv/scripts/mirrors.fedoraproject.org.py", "--data", "/srv/repo/epel", "--ssl", "https://mirrors.fedoraproject.org"]
def centos_epel_http_port(distro: str = NIX, centos: str = NIX) -> int:
    distro = distro or DISTRO
    centos = centos or CENTOS
    return 80
def centos_epel_http_cmd(distro: str = NIX, centos: str = NIX) -> List[str]:
    distro = distro or DISTRO
    centos = centos or CENTOS
    python = centos_python(distro, centos)
    return [python, "/srv/scripts/mirrors.fedoraproject.org.py", "--data", "/srv/repo/epel"]

def centos_main_port(distro: str = NIX, centos: str = NIX) -> int:
    distro = distro or DISTRO
    centos = centos or CENTOS
    if distro == "almalinux":
        return 443
    return 80
def centos_main_cmd(distro: str = NIX, centos: str = NIX) -> List[str]:
    distro = distro or DISTRO
    centos = centos or CENTOS
    python = centos_python(distro, centos)
    if distro == "almalinux":
        return [python, "/srv/scripts/mirrorlist.py", "--data", "/srv/repo", "--ssl", "https://mirrors.almalinux.org"]
    else:
        return [python, "/srv/scripts/mirrorlist.py", "--data", "/srv/repo"]

def centos_http_port(distro: str = NIX, centos: str = NIX) -> int:
    distro = distro or DISTRO
    centos = centos or CENTOS
    return 80
def centos_http_cmd(distro: str = NIX, centos: str = NIX) -> List[str]:
    distro = distro or DISTRO
    centos = centos or CENTOS
    python = centos_python(distro, centos)
    return [python, "/srv/scripts/mirrorlist.py", "--data", "/srv/repo"]

def centos_python(distro: str = NIX, centos: str = NIX) -> str:
    distro = distro or DISTRO
    centos = centos or CENTOS
    if centos.startswith("7"):
        return "/usr/bin/python"
    if centos.startswith("8"):
        return "/usr/libexec/platform-python"
    if centos.startswith("9"):
        return "/usr/bin/python3"
    raise RuntimeWarning("unknown CENTOS %s" % centos)

def centos_repo(distro: str = NIX, centos: str = NIX) -> str:
    distro = distro or DISTRO
    centos = centos or CENTOS
    if centos.startswith("9"):
        return centos_repo9(distro)
    if centos.startswith("8"):
        return centos_repo8(distro)
    if centos.startswith("7"):
        return centos_repo7(distro)
    raise RuntimeWarning("unknown CENTOS %s" % centos)

def centos_repo9(distro: str = NIX, centos: str = NIX) -> str:
    return distro_repos(distro, centos, SUBDIRS9)
def centos_repo8(distro: str = NIX, centos: str = NIX) -> str:
    return distro_repos(distro, centos, SUBDIRS8)
def centos_repo7(distro: str = NIX, centos: str = NIX) -> str:
    return distro_repos(distro, centos, SUBDIRS7)
def distro_repos(distro: str, centos: str, dists: Dict[str, List[str]]) -> str:
    distro = distro or DISTRO
    centos = centos or CENTOS
    docker = DOCKER
    R = major(centos)
    repodir = REPODIR
    centos_restore()
    centos_cleaner()
    baseimage = centos_baseimage(distro, centos)
    rel = centos_release(distro, centos)
    scripts = repo_scripts()
    cname = F"{distro}-repo-{centos}"
    PORT = centos_main_port(distro, centos)
    CMD = str(centos_main_cmd(distro, centos)).replace("'", '"')
    sx___(F"{docker} rm --force {cname}")
    sh___(F"{docker} run --name={cname} --detach {baseimage} sleep 9999")
    if PORT != 80:
        sh___(F"{docker} exec {cname} yum install -y openssl")
    sh___(F"{docker} exec {cname} mkdir -p /srv/repo/{R}")
    if R != rel:
        sh___(F"{docker} exec {cname} ln -sv {R} /srv/repo/{rel}")
    if R != centos and centos != rel:
        sh___(F"{docker} exec {cname} ln -sv {R} /srv/repo/{centos}")
    sh___(F"{docker} cp {scripts} {cname}:/srv/scripts")
    base = "base"
    repo = IMAGESREPO
    sh___(F"{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' -m {base} {cname} {repo}/{distro}-repo/{base}:{rel}")
    for dist in dists:
        sx___(F"{docker} rm --force {cname}")
        sh___(F"{docker} run --name={cname} --detach {repo}/{distro}-repo/{base}:{rel} sleep 9999")
        for subdir in dists[dist]:
            pooldir = F"{repodir}/{distro}.{centos}/{subdir}"
            if path.isdir(pooldir):
                sh___(F"{docker} cp {pooldir} {cname}:/srv/repo/{R}/")
                base = dist
        if base == dist:
            sh___(F"{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' -m {base} {cname} {repo}/{distro}-repo/{base}:{rel}")
    sh___(F"{docker} rm --force {cname}")
    sh___(F"{docker} tag {repo}/{distro}-repo/{base}:{rel} {repo}/{distro}-repo:{rel}")
    sh___(F"{docker} rmi {repo}/{distro}-repo/base:{rel}")  # untag non-packages base
    PORT2 = centos_http_port(distro, centos)
    CMD2 = str(centos_http_cmd(distro, centos)).replace("'", '"')
    if PORT != PORT2:
        # the upstream almalinux repository runs on https by default but we don't have their certificate anyway
        base2 = "http"  # !!
        sh___(F"{docker} run --name={cname} --detach {repo}/{distro}-repo:{rel} sleep 9999")
        sh___(F"{docker} commit -c 'CMD {CMD2}' -c 'EXPOSE {PORT2}' -m {base2} {cname} {repo}/{distro}-repo/{base2}:{rel}")
        sx___(F"{docker} rm --force {cname}")
    centos_restore()
    return F"{repo}/{distro}-repo:{rel}"

def centos_tags(distro: str = NIX, centos: str = NIX) -> None:
    distro = distro or DISTRO
    centos = centos or CENTOS
    docker = DOCKER
    repo = IMAGESREPO
    name = F"{distro}-repo"
    rel = centos_release(distro, centos)
    ver2 = majorminor(centos)
    if ver2 != rel:
        sh___(F"{docker} tag {repo}/{name}:{rel} {repo}/{name}:{ver2}")
    ver1 = major(ver2)
    if ver1 != ver2:
        sh___(F"{docker} tag {repo}/{name}:{rel} {repo}/{name}:{ver1}")
        # sh___(F"{docker} tag {repo}/{name}:{rel} {repo}/{name}{ver1}:{centos}")
        # sh___(F"{docker} tag {repo}/{name}:{rel} {repo}/{name}{ver1}:latest")

def centos_cleaner() -> None:
    distro = DISTRO
    centos = CENTOS
    repodir = REPODIR
    arch = "x86_64"
    for subdir in ["updates", "extras"]:
        orig = F"{repodir}/{distro}.{centos}/{subdir}/{arch}/drpms"
        save = F"{repodir}/{distro}.{centos}/{subdir}.{arch}.drpms"
        if path.isdir(orig):
            shutil.move(orig, save)

def centos_restore() -> None:
    distro = DISTRO
    centos = CENTOS
    repodir = REPODIR
    arch = "x86_64"
    for subdir in ["updates", "extras"]:
        orig = F"{repodir}/{distro}.{centos}/{subdir}/{arch}/drpms"
        save = F"{repodir}/{distro}.{centos}/{subdir}.{arch}.drpms"
        if path.isdir(save):
            shutil.move(save, orig)

def centos_test() -> None:
    distro = DISTRO
    centos = CENTOS
    logg.error("not implemented")
    # sed -e "s|centos:centos7|centos:$(CENTOS)|" -e "s|centos-repo:7|centos-repo:$(CENTOS)|" \
    #    centos-compose.yml > centos-compose.tmp
    # - docker-compose -p $@ -f centos-compose.tmp down
    # docker-compose -p $@ -f centos-compose.tmp up -d
    # docker exec centosworks_host_1 yum install -y firefox
    # docker-compose -p $@ -f centos-compose.tmp down

def centos_check() -> None:
    docker = DOCKER
    distro = DISTRO
    centos = CENTOS
    repodir = REPODIR
    cname = "centos-check-" + centos  # container name
    sx___(F"{docker} rm --force {cname}")
    sh___(F"{docker} run --name={cname} --detach centos:{centos} sleep 9999")
    centosdir = F"{repodir}/{distro}.{centos}"
    out, end = output2(F"{docker} exec {cname} rpm -qa")
    for f in out.split("\n"):
        found = path_find(centosdir, f + ".rpm")
        if found:
            print(F"OK {f}.rpm        {found}")
    for f in out.split("\n"):
        found = path_find(centosdir, f + ".rpm")
        if not found:
            print(F"?? {f}.rpm")
    sh___(F"{docker} rm --force {cname}")

def centos_scripts() -> None:
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

def sh___(cmd: Union[str, List[str]], shell: bool = True) -> int:
    if isinstance(cmd, basestring):
        logg.info(": %s", cmd)
    else:
        logg.info(": %s", " ".join(["'%s'" % item for item in cmd]))
    return subprocess.check_call(cmd, shell=shell)

def sx___(cmd: Union[str, List[str]], shell: bool = True) -> int:
    if isinstance(cmd, basestring):
        logg.info(": %s", cmd)
    else:
        logg.info(": %s", " ".join(["'%s'" % item for item in cmd]))
    return subprocess.call(cmd, shell=shell)
def output(cmd: Union[str, List[str]], shell: bool = True) -> str:
    if isinstance(cmd, basestring):
        logg.info(": %s", cmd)
    else:
        logg.info(": %s", " ".join(["'%s'" % item for item in cmd]))
    run = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE)
    out, err = run.communicate()
    return decodes(out)
def output2(cmd: Union[str, List[str]], shell: bool = True) -> Tuple[str, int]:
    if isinstance(cmd, basestring):
        logg.info(": %s", cmd)
    else:
        logg.info(": %s", " ".join(["'%s'" % item for item in cmd]))
    run = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE)
    out, err = run.communicate()
    return decodes(out), run.returncode
def output3(cmd: Union[str, List[str]], shell: bool = True) -> Tuple[str, str, int]:
    if isinstance(cmd, basestring):
        logg.info(": %s", cmd)
    else:
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

def centos_commands_() -> None:
    print(commands())
def commands() -> str:
    cmds: List[str] = []
    for name in sorted(globals()):
        if name.startswith("centos_"):
            if "_sync_" in name: continue
            if name.endswith("_"): continue
            func = globals()[name]
            if callable(func):
                cmd = name.replace("centos_", "")
                cmds += [cmd]
    return "|".join(cmds)

def centos_image(distro: str = NIX, centos: str = NIX) -> str:
    distro = distro or DISTRO
    centos = centos or CENTOS
    return F"{distro}:{centos}"
def centos_baseimage(distro: str = NIX, centos: str = NIX) -> str:
    distro = distro or DISTRO
    centos = centos or CENTOS
    baseversion = centos
    if baseversion in BASEVERSIONS:
        baseversion = BASEVERSIONS[baseversion]
    return F"{distro}:{baseversion}"

def CENTOS_set(centos: str) -> str:
    global CENTOS, DISTRO
    distro = ""
    if ":" in centos:
        distro, centos = centos.split(":", 1)
        DISTRO = distro
    if centos in BASE:
        DISTRO = distro or "centos"
        CENTOS = centos
        logg.debug("SET CENT1: %s %s [%s]", DISTRO, CENTOS, centos)
        return CENTOS
    if centos in BASE.values():
        DISTRO = distro or "centos"
        CENTOS = max([os for os in BASE if BASE[os] == centos])
        logg.debug("SET CENT2: %s %s [%s]", DISTRO, CENTOS, centos)
        return CENTOS
    if centos in ALMA:
        CENTOS = centos
        DISTRO = distro or ALMALINUX
        logg.debug("SET ALMA1: %s %s [%s]", DISTRO, CENTOS, centos)
        return CENTOS
    if centos in ALMA.values():
        CENTOS = max([os for os in ALMA if ALMA[os] == centos])
        DISTRO = distro or ALMALINUX
        logg.debug("SET ALMA2: %s %s [%s]", DISTRO, CENTOS, centos)
        return CENTOS
    if len(centos) <= 2:
        last = [os for os in BASE if os.startswith(centos)]
        if last:
            CENTOS = max(last)
            # DISTRO = "centos"
        last = [os for os in ALMA if os.startswith(centos)]
        if last:
            CENTOS = max(last)
            DISTRO = distro or ALMALINUX
        return CENTOS
    if centos not in BASE.values():
        logg.warning("SET: %s is not a known os version", centos)
    CENTOS = centos
    return CENTOS

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
    _o.add_option("-V", "--ver", metavar="NUM", default=CENTOS,
                  help="use other centos version [%default]")
    _o.add_option("-c", "--config", metavar="NAME=VAL", action="append", default=[],
                  help="override globals (REPODIR, REPODATADIRS, IMAGESREPO)")
    opt, args = _o.parse_args()
    logging.basicConfig(level=logging.WARNING - opt.verbose * 10)
    config_globals(opt.config)
    DOCKER = opt.docker
    CENTOS_set(opt.ver)
    #
    if not args: args = ["make"]
    for arg in args:
        if arg[0] in "123456789":
            CENTOS_set(arg)
            continue
        funcname = "centos_" + arg.replace("-", "_")
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
