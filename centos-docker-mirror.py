#! /usr/bin/python3
# pylint: disable=unused-variable,unused-argument,line-too-long,too-many-lines,too-many-locals,too-many-return-statements,too-many-branches
# pylint: disable=consider-using-from-import,consider-using-get,consider-using-generator,consider-using-with,consider-using-in,no-else-return
""" sync packages repo to disk and make docker mirror images from it.
    Try to run 'sync' followed be 'repo'. If a command starts with a
    number then it changes the version to be handled. A usual command
    would be 'mirror.py 7.7 sync repo -v'. If no argument is given
    then 'make' the last version = 'sync pull repo test check tags'.
    ((with ''epelsync'' and ''epelrepo'' you can also take a snapshot
     from the fedora epel repos (which do not have real releases)))."""

__copyright__ = "(C) 2025 Guido Draheim"
__contact__ = "https://github.com/gdraheim/docker-mirror-packages-repo"
__license__ = "CC0 Creative Commons Zero (Public Domain)"
__version__ = "1.7.7123"

from typing import Optional, Dict, List, Tuple, Union, Any, Set
from collections import OrderedDict
import os
import os.path as path
import sys
import re
import subprocess
import shutil
import datetime
import configparser
import logging
logg = logging.getLogger("MIRROR")

NIX = ""
NEVER = False
NOBASE = False
IMAGESREPO = os.environ.get("IMAGESREPO", "localhost:5000/mirror-packages")
REPODATADIR = os.environ.get("REPODATADIR", "")
REPODIR = os.environ.get("REPODIR", "repo.d")

DOCKERDEF = os.environ.get("DOCKER_EXE", os.environ.get("DOCKER_BIN", "docker"))
PYTHONDEF = os.environ.get("DOCKER_PYTHON", os.environ.get("DOCKER_PYTHON3", "python3"))
MIRRORDEF = os.environ.get("DOCKER_MIRROR_PY", os.environ.get("DOCKER_MIRROR",  "docker_mirror.py"))
RSYNCDEF= os.environ.get("DOCKER_RSYNC", os.environ.get("DOCKER_RSYNC3", "rsync"))

DISTROPYTHON = NIX # default for repo containers depends on centos version
PYTHON = PYTHONDEF
MIRROR = MIRRORDEF
DOCKER = DOCKERDEF
RSYNC = RSYNCDEF

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
ALMA["9.5-20241118"] = "9.5"
ALMA["9.5-20250307"] = "9.5"

ARCHLIST = ["x86_64", "ppc64le", "aarch64", "s390x"]

CENTOS = "9.3-20240410"
ARCHS = ["x86_64"]
DISKSUFFIX = "disk" # suffix
BASELAYER = "base"
VARIANT = ""


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

def _iterable(x: Any) -> bool: # type: ignore[misc]
    return hasattr(x, "__iter__")

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

def centos_distdirs(distro: str = NIX, centos: str = NIX) -> List[str]:
    distro = distro or DISTRO
    centos = centos or CENTOS
    if distro in ["epel"]:
        if centos.startswith("9"):
            return []
        elif centos.startswith("8"):
            return ["Everything", "Modular"]
        else:
            return ["Everything"]
    else:
        values: Set[str] = set()
        if centos.startswith("6"):
            for layer in SUBDIRS6:
                for subdir in SUBDIRS6[layer]:
                    values.add(subdir)
        elif centos.startswith("7"):
            for layer in SUBDIRS7:
                for subdir in SUBDIRS7[layer]:
                    values.add(subdir)
        elif centos.startswith("8"):
            for layer in SUBDIRS8:
                for subdir in SUBDIRS8[layer]:
                    values.add(subdir)
        else:
            for layer in SUBDIRS9:
                for subdir in SUBDIRS9[layer]:
                    values.add(subdir)
        return list(sorted(values))

def centos_distros(distro: str = NIX, centos: str = NIX) -> List[str]:
    distro = distro or DISTRO
    ubuntu = centos or CENTOS
    epel = EPEL
    return [distro, epel]

#############################################################################


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
        return max([os for os, os_base in BASE.items() if os_base == centos])
    if centos in ALMA.values():
        return max([os for os, os_base in ALMA.items() if os_base == centos])
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

def centos_datadir() -> str:
    for data in reversed(DATADIRS):
        logg.debug(".. check %s", data)
        if path.isdir(data):
            return data
    return REPODIR

def centos_dir(variant: str = NIX) -> str:
    distro = DISTRO
    centos = CENTOS
    return distro_dir(distro, centos, variant)
def centos_epeldir(variant: str = NIX) -> str:
    distro = EPEL
    centos = CENTOS
    rel = major(CENTOS)
    return distro_dir(distro, centos, variant, rel)
def distro_dir(distro: str, release: str, variant: str = NIX, rel: str = NIX) -> str:
    # distro = DISTRO
    repodir = REPODIR
    variant = variant or VARIANT
    rel = rel if rel else release
    version = F"{rel}.{variant}" if variant else rel
    dirname = F"{distro}.{version}"
    dirlink = path.join(repodir, dirname)
    if not path.isdir(repodir):
        os.mkdir(repodir)
    if "-" in release:
        mainrelease, _ = release.split("-", 1)
        version = F"{mainrelease}.{VARIANT}" if VARIANT else mainrelease
        oldname = F"{distro}.{version}"
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
                os.symlink(path.abspath(dirpath), dirlink)
                break
    dircheck = path.join(dirlink, ".")
    if path.isdir(dircheck):
        logg.info("%s -> %s", dirlink, os.readlink(dirlink))
    else:
        os.mkdir(dirlink)  # local dir
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
            logg.info("%s", F"#### [{base}] /{VARIANT}{subdir}")
            distro_sync_subdir(distro, centos, subdir)
            logg.info("%s", F"DONE [{base}] /{VARIANT}{subdir}")

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
    version = F"{centos2}.{VARIANT}" if VARIANT else centos2
    sh___(F"{rsync} -rv {mirror}/{centos2}/{subdir}   {repodir}/{distro}.{version}/ {excludes}")

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
def distro_epelsyncs(distro: str, centos: str, subdirs: Optional[List[str]] = None) -> str:
    subdirs = subdirs if subdirs is not None else []
    distro = distro or EPEL
    centos = centos or CENTOS
    rsync = RSYNC
    mirror = MIRRORS[distro][0]
    epel = major(centos)
    archs = ARCHS
    repo = distro_dir(distro, epel)
    excludes = """ --exclude "*.iso" """
    if subdirs:
        for subdir in subdirs:
            basedir = F"{repo}/{epel}/{subdir}"
            if not path.isdir(basedir):
                os.makedirs(basedir)
            for arch in archs:
                sh___(F"{rsync} -rv {mirror}/{epel}/{subdir}/{arch} {basedir}/ {excludes}")
    else:
        basedir = F"{repo}/{epel}"
        for arch in archs:
            sh___(F"{rsync} -rv {mirror}/{epel}/{arch} {basedir}/ {excludes}")
    centos_epeltimestamp(distro, centos)
    return F"epel.{epel}/{epel}"

def centos_epeltimestamp(distro: str = NIX, centos: str = NIX) -> Optional[str]:
    distro = distro or EPEL
    centos = centos or CENTOS
    epel = major(centos)
    repo = distro_dir(distro, epel)
    timestamp = centos_epeltime(distro, centos)
    if timestamp:
        timestampfile = F"{repo}/timestamp.ini"
        ini = configparser.ConfigParser()
        if os.path.isfile(timestampfile):
            ini.read(timestampfile)
        if epel not in ini:
            ini[epel] = {}
        ini[epel]["distro"] = distro
        ini[epel]["centos"] = centos
        ini[epel]["updated"] = timestamp.isoformat()
        with open(timestampfile, "w") as fp:
            ini.write(fp)
        logg.info("updated %s", timestampfile)
        yyyymmdd = timestamp.strftime("%y%m%d")
        return F"|{yyyymmdd}|{timestampfile}"
    return None

def centos_epelupdated(distro: str = NIX, centos: str = NIX) -> Optional[datetime.datetime]:
    distro = distro or EPEL
    centos = centos or CENTOS
    epel = major(centos)
    repo = distro_dir(distro, epel)
    if not os.path.isdir(repo):
        return None
    timestampfile = F"{repo}/timestamp.ini"
    if not os.path.isfile(timestampfile):
        centos_epeltimestamp(distro, centos)
    if not os.path.isfile(timestampfile):
        return None
    ini = configparser.ConfigParser()
    ini.read(timestampfile)
    if epel in ini:
        updated = _fromisoformat(ini[epel].get("updated", ""))
        logg.info("  epel %s updated = %s", epel, updated)
        return updated
    return None

def centos_epeltime(distro: str = NIX, centos: str = NIX) -> Optional[datetime.datetime]:
    distro = distro or EPEL
    centos = centos or CENTOS
    epel = major(centos)
    repo = distro_dir(distro, epel)
    epeldir = F"{repo}/{epel}"
    logg.debug(" epeltime - walk %s", epeldir)
    latest = None
    for root, _, files in os.walk(epeldir):
        for name in files:
            filename = os.path.join(root, name)
            changed = os.path.getmtime(filename)
            if not latest:
                latest = changed
            elif latest < changed:
                latest = changed
    if not latest:
        logg.warning("epeltime - no files found")
        return None
    else:
        epeltimestamp = datetime.datetime.fromtimestamp(latest)
        logg.info("  epeltime = %s", epeltimestamp)
        return epeltimestamp

def centos_unpack() -> None:
    """ used while testing if centos had all packages """
    docker = DOCKER
    distro = DISTRO
    centos = CENTOS
    version = "F{centos}.{VARIANT}" if VARIANT else centos
    R = major(centos)
    repodir = REPODIR
    cname = "centos-unpack-" + centos  # container name
    image = F"localhost:5000/{distro}-repo"
    sx___(F"{docker} rm --force {cname}")
    sh___(F"{docker} run --name={cname} --detach {image}:{centos} sleep 9999")
    sh___(F"{docker} cp {cname}:/srv/repo/{R}/os {repodir}/{distro}.{version}/")
    sh___(F"{docker} cp {cname}:/srv/repo/{R}/extras {repodir}/{distro}.{version}/")
    sh___(F"{docker} cp {cname}:/srv/repo/{R}/updates {repodir}/{distro}.{version}/")
    sh___(F"{docker} cp {cname}:/srv/repo/{R}/sclo {repodir}/{distro}.{version}/")
    sh___(F"{docker} rm --force {cname}")
    sh___(F"du -sh {repodir}/{distro}.{version}/.")

def centos_clean() -> None:
    """ when moving from centos:7 to centos:8 """
    distro = DISTRO
    centos = CENTOS
    repodir = REPODIR
    version = "F{centos}.{VARIANT}" if VARIANT else centos
    for subdir in ["os", "extras", "updates", "sclo"]:
        sh___(F"rm -rf {repodir}/{distro}.{version}/{subdir}")

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
def centos_epelbase(distro: str = NIX, centos: str = NIX) -> None:
    dists: Dict[str, List[str]] = OrderedDict()
    distro_epelrepos(distro, centos, dists)


def distro_epelrepos(distro: str, centos: str, dists: Dict[str, List[str]]) -> None:
    distro = distro or EPEL
    centos = centos or CENTOS
    repodir = REPODIR
    docker = DOCKER
    epel = major(centos)
    scripts = centos_scripts()
    version = F"{epel}.{VARIANT}" if VARIANT else epel
    cname = F"{distro}-repo-{epel}"
    baseimage = centos_baseimage(DISTRO, centos)
    out =  output(F"{PYTHON} {MIRROR} start {baseimage} -a")
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
    if NEVER:
        # instead we use an explicit epelrepo8_CMD
        for script in os.listdir(F"{scripts}/."):
            sh___(F"{docker} exec {cname} sed -i s:/usr/bin/python3:/usr/libexec/platform-python: /srv/scripts/{script}")
            sh___(F"{docker} exec {cname} chmod +x /srv/scripts/{script}")
    base = BASELAYER
    repo = IMAGESREPO
    latest = centos_epelupdated(distro, centos) or datetime.date.today()
    yymm = latest.strftime("%y%m")
    sh___(F"{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' -m {base} {cname} {repo}/{distro}-repo/{base}:{version}.x.{yymm}")
    for dist in dists:
        sx___(F"{docker} rm --force {cname}")
        sh___(F"{docker} run --name={cname} --detach {repo}/{distro}-repo/{base}:{version}.x.{yymm} sleep 9999")
        for subdir in dists[dist]:
            sh___(F"{docker} cp {repodir}/{distro}.{epel}/{epel}/{subdir} {cname}:/srv/repo/epel/{epel}/")
            base = dist  # !!
        if base == dist:
            sh___(F"{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' -m {base} {cname} {repo}/{distro}-repo/{base}:{version}.x.{yymm}")
    sx___(F"{docker} rm --force {cname}")
    if base != BASELAYER:
        sh___(F"{docker} tag {repo}/{distro}-repo/{base}:{version}.x.{yymm} {repo}/{distro}-repo:{version}.x.{yymm}")
        if NOBASE:
            sh___(F"{docker} rmi {repo}/{distro}-repo/{BASELAYER}:{version}.x.{yymm}")
        PORT2 = centos_epel_http_port(distro, centos)
        CMD2 = str(centos_epel_http_cmd(distro, centos)).replace("'", '"')
        if PORT != PORT2:
            # the upstream epel repository runs on https by default but we don't have their certificate anyway
            base2 = "http"  # !!
            sh___(F"{docker} run --name={cname} --detach {repo}/{distro}-repo:{version}.x.{yymm} sleep 9999")
            sh___(F"{docker} commit -c 'CMD {CMD2}' -c 'EXPOSE {PORT2}' -m {base2} {cname} {repo}/{distro}-repo/{base2}:{version}.x.{yymm}")
            sx___(F"{docker} rm --force {cname}")

def centos_epelrepo7(distro: str = NIX, centos: str = NIX) -> None:
    distro = distro or EPEL
    centos = centos or CENTOS
    repodir = REPODIR
    docker = DOCKER
    epel = major(centos)
    scripts = centos_scripts()
    version = F"{epel}.{VARIANT}" if VARIANT else epel
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
    latest = centos_epelupdated(distro, centos) or datetime.date.today()
    yymm = latest.strftime("%y%m")
    sh___(F"{docker} cp {repodir}/{distro}.{epel}/{epel} {cname}:/srv/repo/epel/")
    sh___(F"{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' {cname} {repo}/{distro}-repo:{version}.x.{yymm}")
    sh___(F"{docker} rm --force {cname}")
    if MAKE_EPEL_HTTP:
        PORT2 = centos_epel_http_port(distro, centos)
        CMD2 = str(centos_epel_http_cmd(distro, centos)).replace("'", '"')
        base2 = "http"  # !!
        # the upstream epel repository runs on https by default but we don't have their certificate anyway
        sh___(F"{docker} run --name={cname} --detach {repo}/{distro}-repo:{version}.x.{yymm} sleep 999")
        sh___(F"{docker} commit -c 'CMD {CMD2}' -c 'EXPOSE {PORT2}' {cname} {repo}/{distro}-repo/{base2}:{version}.x.{yymm}")
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
    if DISTROPYTHON:
        return DISTROPYTHON
    if centos.startswith("7"):
        return "/usr/bin/python"
    if centos.startswith("8"):
        return "/usr/libexec/platform-python"
    if centos.startswith("9"):
        return "/usr/bin/python3"
    raise RuntimeWarning("unknown CENTOS %s" % centos)

def centos_base(distro: str = NIX, centos: str = NIX) -> str:
    dists: Dict[str, List[str]] = {}
    return distro_repos(distro, centos, dists)
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
    scripts = centos_scripts()
    version = F"{rel}.{VARIANT}" if VARIANT else rel
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
    base = BASELAYER
    repo = IMAGESREPO
    sh___(F"{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' -m {base} {cname} {repo}/{distro}-repo/{base}:{version}")
    for dist in dists:
        sx___(F"{docker} rm --force {cname}")
        sh___(F"{docker} run --name={cname} --detach {repo}/{distro}-repo/{base}:{version} sleep 9999")
        for subdir in dists[dist]:
            pooldir = F"{repodir}/{distro}.{centos}/{subdir}"
            if path.isdir(pooldir):
                sh___(F"{docker} cp {pooldir} {cname}:/srv/repo/{R}/")
                base = dist
        if base == dist:
            sh___(F"{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' -m {base} {cname} {repo}/{distro}-repo/{base}:{version}")
    sh___(F"{docker} rm --force {cname}")
    if base != BASELAYER:
        sh___(F"{docker} tag {repo}/{distro}-repo/{base}:{version} {repo}/{distro}-repo:{version}")
        if NOBASE:
            sh___(F"{docker} rmi {repo}/{distro}-repo/{BASELAYER}:{version}")  # untag non-packages base
        PORT2 = centos_http_port(distro, centos)
        CMD2 = str(centos_http_cmd(distro, centos)).replace("'", '"')
        if PORT != PORT2:
            # the upstream almalinux repository runs on https by default but we don't have their certificate anyway
            base2 = "http"  # !!
            sh___(F"{docker} run --name={cname} --detach {repo}/{distro}-repo:{version} sleep 9999")
            sh___(F"{docker} commit -c 'CMD {CMD2}' -c 'EXPOSE {PORT2}' -m {base2} {cname} {repo}/{distro}-repo/{base2}:{version}")
            sx___(F"{docker} rm --force {cname}")
    centos_restore()
    return F"\n[{baseimage}]\nimage = {repo}/{distro}-repo/{base}:{version}\n"

def centos_disk(distro: str = NIX, centos: str = NIX) -> str:
    distro = distro or DISTRO
    centos = centos or CENTOS
    if centos.startswith("9"):
        return centos_disk9(distro)
    if centos.startswith("8"):
        return centos_disk8(distro)
    if centos.startswith("7"):
        return centos_disk7(distro)
    raise RuntimeWarning("unknown CENTOS %s" % centos)

def centos_disk9(distro: str = NIX, centos: str = NIX) -> str:
    return distro_diskmake(distro, centos, SUBDIRS9)
def centos_disk8(distro: str = NIX, centos: str = NIX) -> str:
    return distro_diskmake(distro, centos, SUBDIRS8)
def centos_disk7(distro: str = NIX, centos: str = NIX) -> str:
    return distro_diskmake(distro, centos, SUBDIRS7)
def distro_diskmake(distro: str, centos: str, dists: Dict[str, List[str]]) -> str:
    distro = distro or DISTRO
    centos = centos or CENTOS
    docker = DOCKER
    R = major(centos)
    repodir = REPODIR
    centos_restore()
    centos_cleaner()
    rel = centos_release(distro, centos)
    scripts = centos_scripts()
    # version = F"{rel}.{VARIANT}" if VARIANT else rel
    rootdir = distro_dir(distro, centos, variant=F"{VARIANT}{DISKSUFFIX}")
    srv = F"{rootdir}/srv"
    logg.info("srv = %s", srv)
    sh___(F"mkdir -p {srv}/repo/{R}")
    if R != rel:
        sh___(F"test -L {srv}/repo/{rel} || ln -sv {R} {srv}/repo/{rel}")
    if R != centos and centos != rel:
        sh___(F"test -L {srv}/repo/{centos} || ln -sv {R} {srv}/repo/{centos}")
    for dist in dists:
        for subdir in dists[dist]:
            pooldir = F"{repodir}/{distro}.{centos}/{subdir}"
            if path.isdir(pooldir):
                sh___(F"cp -r --link --no-clobber {pooldir} {srv}/repo/{R}/")
    path_srv = os.path.realpath(srv)
    return F"\nmount = {path_srv}/repo\n"

def centos_epeldisk(distro: str = NIX, centos: str = NIX) -> str:
    dists: Dict[str, List[str]] = OrderedDict()
    dists["main"] = ["Everything"]
    ver = centos or CENTOS
    if ver.startswith("8"):
        dists["plus"] = ["Modular"]
    return distro_epeldisk(distro, centos, dists)
def distro_epeldisk(distro: str, centos: str, dists: Dict[str, List[str]]) -> str:
    distro = "epel"
    centos = centos or CENTOS
    epel = major(centos)
    repodir = REPODIR
    centos_restore()
    centos_cleaner()
    rootdir = centos_epeldir(variant=F"{VARIANT}{DISKSUFFIX}")
    srv = F"{rootdir}/srv"
    logg.info("srv = %s", srv)
    sh___(F"mkdir -p {srv}/repo/epel/{epel}")
    for dist in dists:
        for subdir in dists[dist]:
            sh___(F"cp -r --link --no-clobber {repodir}/{distro}.{epel}/{epel}/{subdir} {srv}/repo/epel/{epel}/")
    path_srv = os.path.realpath(srv)
    return F"\nmount = {path_srv}/repo\n"


def centos_diskpath(distro: str = NIX, centos: str = NIX) -> str:
    rootdir = centos_dir(variant=F"{VARIANT}{DISKSUFFIX}")
    srv = F"{rootdir}/srv"
    path_srv = os.path.realpath(srv)
    return F"{path_srv}/repo\n"

def centos_dropdisk(distro: str = NIX, centos: str = NIX) -> str:
    rootdir = centos_dir(variant=F"{VARIANT}{DISKSUFFIX}")
    srv = F"{rootdir}/srv"
    path_srv = os.path.realpath(srv)
    if os.path.isdir(path_srv):
        shutil.rmtree(path_srv)
    return path_srv

def centos_epeldiskpath(distro: str = NIX, centos: str = NIX) -> str:
    rootdir = centos_epeldir(variant=F"{VARIANT}{DISKSUFFIX}")
    logg.info("epel rootdir %s", rootdir)
    # latest = centos_epelupdated(distro, centos) or datetime.date.today()
    # yymm = latest.strftime("%y%m")
    # logg.info(" yymm %s", yymm)
    srv = F"{rootdir}/srv"
    path_srv = os.path.realpath(srv)
    return F"{path_srv}/repo\n"

def centos_epeldropdisk() -> str:
    rootdir = centos_epeldir(variant=F"{VARIANT}{DISKSUFFIX}")
    srv = F"{rootdir}/srv"
    path_srv = os.path.realpath(srv)
    if os.path.isdir(path_srv):
        shutil.rmtree(path_srv)
    return path_srv

def centos_epelsection(distro: str = NIX, centos: str = NIX, imagesrepo: str = NIX) -> str:
    imagesrepo = imagesrepo or IMAGESREPO
    distro = "epel"
    rel = major(centos_release(distro, centos or CENTOS))
    ver = F"{rel}.{VARIANT}" if VARIANT else rel
    base = BASELAYER
    latest = centos_epelupdated(distro, centos) or datetime.date.today()
    yymm = latest.strftime("%y%m")
    return F"{distro}-repo.x.{yymm}"

def centos_epelbaserepo(distro: str = NIX, centos: str = NIX, imagesrepo: str = NIX) -> str:
    imagesrepo = imagesrepo or IMAGESREPO
    distro = "epel"
    rel = major(centos_release(distro, centos or CENTOS))
    ver = F"{rel}.{VARIANT}" if VARIANT else rel
    base = BASELAYER
    latest = centos_epelupdated(distro, centos) or datetime.date.today()
    yymm = latest.strftime("%y%m")
    return F"{imagesrepo}/{distro}-repo/{base}:{ver}.x.{yymm}"
def centos_baserepo(distro: str = NIX, centos: str = NIX, imagesrepo: str = NIX) -> str:
    imagesrepo = imagesrepo or IMAGESREPO
    distro = distro or DISTRO
    rel = centos_release(distro, centos or CENTOS)
    version = F"{rel}.{VARIANT}" if VARIANT else rel
    base = BASELAYER
    return F"{imagesrepo}/{distro}-repo/{base}:{version}"
def centos_mainrepo(distro: str = NIX, centos: str = NIX, imagesrepo: str = NIX) -> str:
    imagesrepo = imagesrepo or IMAGESREPO
    distro = distro or DISTRO
    rel = centos_release(distro, centos or CENTOS)
    version = F"{rel}.{VARIANT}" if VARIANT else rel
    base = BASELAYER
    return F"{imagesrepo}/{distro}-repo/{base}:{version}"

def centos_local(distro: str = NIX, centos: str = NIX) -> str:
    """ show ini section for diskpath and --epel """
    mainsection = centos_baseimage(distro, centos)
    mainbaseimage = centos_baserepo(distro, centos)
    maindiskpath = centos_diskpath()
    epelsection = centos_epelsection(distro, centos)
    epelbaseimage = centos_epelbaserepo(distro, centos)
    epeldiskpath = centos_epeldiskpath(distro, centos)
    return F"[{mainsection}]\nimage={mainbaseimage}\nmount={maindiskpath}\n\n[{epelsection}]\nimage={epelbaseimage}\nmount={epeldiskpath}"

def centos_list(distro: str = NIX, centos: str = NIX) -> int:
    docker = DOCKER
    print(F"REPOSITORY:TAG\tSIZE          # {docker} images {{baseimage}} {{baserepo}} {{mainrepo}}")
    baseimage = centos_baseimage(distro, centos)
    logg.debug("docker image list %s", baseimage)
    cmd = F"{docker} image list {baseimage} -q --format '{{{{.Repository}}}}:{{{{.Tag}}}}\t{{{{.Size}}}}'"
    sx1 = sx___(cmd)
    baserepo = centos_baserepo(distro, centos)
    logg.debug("docker image list %s", baserepo)
    cmd = F"{docker} image list {baserepo} -q --format '{{{{.Repository}}}}:{{{{.Tag}}}}\t{{{{.Size}}}}'"
    sx2 = sx___(cmd)
    mainrepo = centos_mainrepo(distro, centos)
    logg.debug("docker image list %s", mainrepo)
    cmd = F"{docker} image list {mainrepo} -q --format '{{{{.Repository}}}}:{{{{.Tag}}}}\t{{{{.Size}}}}'"
    sx3 = sx___(cmd)
    return min(sx1, sx2, sx3)


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
    archs = ARCHS
    for subdir in ["updates", "extras"]:
        for arch in archs:
            orig = F"{repodir}/{distro}.{centos}/{subdir}/{arch}/drpms"
            save = F"{repodir}/{distro}.{centos}/{subdir}.{arch}.drpms"
            if path.isdir(orig):
                shutil.move(orig, save)

def centos_restore() -> None:
    distro = DISTRO
    centos = CENTOS
    repodir = REPODIR
    archs = ARCHS
    for subdir in ["updates", "extras"]:
        for arch in archs:
            orig = F"{repodir}/{distro}.{centos}/{subdir}/{arch}/drpms"
            save = F"{repodir}/{distro}.{centos}/{subdir}.{arch}.drpms"
            if path.isdir(save):
                shutil.move(save, orig)

def centos_scripts() -> str:
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

def _fromisoformat(time: str) -> Optional[datetime.datetime]:
    try:
        if hasattr(datetime.datetime, "fromisoformat"):
            return datetime.datetime.fromisoformat(time)
        elif "T" in time:
            return datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%f")
        elif "." in time:
            return datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%f")
        elif time.count(":") == 2:
            return datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
        elif time.count(":") == 1:
            return datetime.datetime.strptime(time, "%Y-%m-%d %H:%M")
        elif "-" in time:
            return datetime.datetime.strptime(time, "%Y-%m-%d")
        else:
            return datetime.datetime.strptime(time, "%Y%m%d")
    except ValueError:
        logg.info("not a iso datetime: %s", time)
        return None

def decodes(text: Union[bytes, str]) -> str:
    if text is None: return None
    if isinstance(text, bytes):
        encoded = sys.getdefaultencoding()
        if encoded in ["ascii"]:
            encoded = "utf-8"
        try:
            return text.decode(encoded)
        except UnicodeEncodeError:
            return text.decode("latin-1")
    return text

def sh___(cmd: Union[str, List[str]], shell: bool = True) -> int:
    if isinstance(cmd, str):
        logg.info(": %s", cmd)
    else:
        logg.info(": %s", " ".join(["'%s'" % item for item in cmd]))
    return subprocess.check_call(cmd, shell=shell)

def sx___(cmd: Union[str, List[str]], shell: bool = True) -> int:
    if isinstance(cmd, str):
        logg.info(": %s", cmd)
    else:
        logg.info(": %s", " ".join(["'%s'" % item for item in cmd]))
    return subprocess.call(cmd, shell=shell)
def output(cmd: Union[str, List[str]], shell: bool = True) -> str:
    if isinstance(cmd, str):
        logg.info(": %s", cmd)
    else:
        logg.info(": %s", " ".join(["'%s'" % item for item in cmd]))
    run = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE)
    out, err = run.communicate()
    return decodes(out)

#############################################################################

def path_find(base: str, name: str) -> Optional[str]:
    for dirpath, _, filenames in os.walk(base):
        if name in filenames:
            return path.join(dirpath, name)
    return None

def centos_epelimage(distro: str = NIX, centos: str = NIX) -> str:
    distro = "epel"
    centos = centos or CENTOS
    rel = major(centos)
    updated = centos_epelupdated(distro, centos)
    yymm = updated.strftime("%y%m") if updated else ""
    xx = F"x.{yymm}" if yymm else "x"
    return F"{distro}-repo:{rel}.{xx}"
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

def centos_version2(distro: str = NIX, centos: str = NIX) -> Tuple[str, str]:
    # distro = distro or DISTRO
    centos = centos or CENTOS
    if ":" in centos:
        distro, centos = centos.split(":", 1)
    if centos in BASE:
        distro = distro or "centos"
        return distro, centos
    if centos in BASE.values():
        distro = distro or "centos"
        release = max([os for os, os_base in BASE.items() if os_base == centos])
        return distro, release
    if centos in ALMA:
        return ALMALINUX, centos
    if centos in ALMA.values():
        distro = ALMALINUX
        release = max([os for os, os_base in ALMA.items() if os_base == centos])
        return distro, release
    if len(centos) <= 2:
        release = NIX
        last = [os for os in BASE if os.startswith(centos)]
        if last:
            release = max(last)
            distro = "centos"
        last = [os for os in ALMA if os.startswith(centos)]
        if last:
            release = max(last)
            distro = ALMALINUX
        return distro, (release or centos)
    if centos not in BASE.values():
        logg.warning("%s is not a known os version", centos)
    return distro, centos

def centos_version(distro: str = NIX, centos: str = NIX) -> str:
    release = centos_version2(distro, centos)[1]
    logg.debug("release version %s", release)
    return release

def CENTOS_set(centos: str) -> str:
    global CENTOS, DISTRO  # pylint: disable=global-statement
    distro, release = centos_version2(NIX, centos)
    logg.debug("centos %s -> %s/%s", centos, distro, release)
    CENTOS = release or centos
    DISTRO = distro or DISTRO
    logg.info(" centos %s -> %s/%s -> DISTRO=%s CENTOS=%s", centos, distro, release, DISTRO, CENTOS)
    return CENTOS

def centos_commands() -> str:
    cmds: List[str] = []
    for name in sorted(globals()):
        if name.startswith("centos_"):
            if "_sync_" in name: continue
            if "_http_" in name: continue
            if name and name[-1].isnumeric(): continue
            if name.endswith("_"): continue
            func = globals()[name]
            if callable(func):
                cmd = name.replace("centos_", "")
                cmds += [cmd]
    return "|".join(cmds)

def _main(args: List[str]) -> int:
    for arg in args:
        if arg[0] in "123456789":
            CENTOS_set(arg)
            continue
        if ":" in arg and arg.split(":", 1)[1][0] in "123456789":
            CENTOS_set(arg)
            continue
        funcname = "centos_" + arg.replace("-", "_")
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
    cmdline = OptionParser("%%prog [-options] [%s]" % centos_commands(),
                      epilog=re.sub("\\s+", " ", __doc__).strip())
    cmdline.formatter.max_help_position = 30
    cmdline.add_option("-v", "--verbose", action="count", default=0, help="more logging level [%default]")
    cmdline.add_option("-^", "--quiet", action="count", default=0, help="less verbose logging [%default]")
    cmdline.add_option("->", "--mirror", metavar="PY", default=MIRROR, help="different path to [%default]")
    cmdline.add_option("-P", "--python", metavar="EXE", default=PYTHON, help="alternative to [%default] (=python3.11)")
    cmdline.add_option("-D", "--docker", metavar="EXE", default=DOCKER,   help="alternative to [%default] (e.g. podman)")
    cmdline.add_option("--rsync", metavar="EXE", default=RSYNC, help="alternative to [%default]")
    cmdline.add_option("--distropython", metavar="EXE", default=DISTROPYTHON, help="alternative to ./scripts [%default] runner")
    cmdline.add_option("-R", "--nobase", action="store_true", default=NOBASE,
                       help="rm */base when repo image is ready [%default]")
    cmdline.add_option("--repodir", metavar="DIR", default=REPODIR,
                       help="set $REPODIR [%default]")
    cmdline.add_option("--datadir", metavar="DIR", default=REPODATADIR,
                       help="set $REPODATADIR -> "+(REPODATADIR if REPODATADIR else centos_datadir()))
    cmdline.add_option("--imagesrepo", metavar="PREFIX", default=IMAGESREPO,
                       help="set $IMAGESREPO [%default]")
    cmdline.add_option("--disksuffix", metavar="NAME", default=DISKSUFFIX,
                       help="use disk suffix for testing [%default]")
    cmdline.add_option("-W", "--variant", metavar="NAME", default=VARIANT,
                       help="use variant suffix for testing [%default]")
    cmdline.add_option("-V", "--ver", metavar="NUM", default=CENTOS,
                       help="use other centos version [%default]")
    cmdline.add_option("-a", "--arch", metavar="NAME", action="append", default=[],
                       help=F"use other arch list {ARCHS}")
    opt, cmdline_args = cmdline.parse_args()
    logging.basicConfig(level=logging.WARNING - opt.verbose * 10 + opt.quiet * 10)
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
    DISTROPYTHON = opt.distropython
    PYTHON = opt.python
    MIRROR = opt.mirror
    CENTOS_set(opt.ver)
    #
    sys.exit(_main(cmdline_args or ["list"]))
