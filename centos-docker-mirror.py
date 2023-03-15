#! /usr/bin/python3
""" sync packages repo to disk and make docker mirror images from it.
    Try to run 'sync' followed be 'repo'. If a command starts with a
    number then it changes the version to be handled. A usual command
    would be 'mirror.py 7.7 sync repo -v'. If no argument is given
    then 'make' the last version = 'sync pull repo test check tags'.
    ((with ''epelsync'' and ''epelrepo'' you can also take a snapshot
     from the fedora epel repos (which do not have real releases)))."""

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
import subprocess
import shutil
import datetime
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

OS: Dict[str, str] = {}
OS["8.5"] = "8.5.2111"
OS["8.4"] = "8.4.2105"
OS["8.3"] = "8.3.2011"
OS["8.2"] = "8.2.2004"
OS["8.1"] = "8.1.1911"
OS["8.0"] = "8.0.1905"
OS["7.9"] = "7.9.2009"
OS["7.8"] = "7.8.2003"
OS["7.7"] = "7.7.1908"
OS["7.6"] = "7.6.1810"
OS["7.5"] = "7.5.1804"
OS["7.4"] = "7.4.1708"
OS["7.3"] = "7.3.1611"
OS["7.2"] = "7.2.1511"
OS["7.1"] = "7.1.1503"
OS["7.0"] = "7.0.1406"

ALMA: Dict[str, str] = {}
ALMA["9.1-20230222"] = "9.1"
ALMA["9.1-20221201"] = "9.1"
ALMA["9.1-20221117"] = "9.1"
ALMA["9.0-20221001"] = "9.0"
ALMA["9.0-20220901"] = "9.0"
ALMA["9.0-20220706"] = "9.0"

CENTOS = "8.5.2111"
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
_SUBDIRS["8.5"] = ["AppStream", "BaseOS", "Devel", "extras", "PowerTools", "centosplus",
                   "cloud", "configmanagement", "cr", "fasttrack", "HighAvailibility",
                   "infra", "messages", "nfv", "opstools", "storage", "virt", ]
_SUBDIRS["7.9"] = ["os", "updates", "extras", "sclo", "centosplus", "atomic",
                   "cloud", "configmanagement", "cr", "dotnet", "fasttrack",
                   "infra", "messages", "nfv", "opstools", "paas", "rt", "storage", "virt", ]

# docker-mirror.py can select from "main" to "sclo" which however is the default.

SUBDIRS9: Dict[str, List[str]] = OrderedDict()
SUBDIRS9["main"] = ["BaseOS", "AppStream", "extras"]
SUBDIRS9["plus"] = ["plus"]  # ALMALINUX
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

BASEVERSION: Dict[str, str] = {}
BASEVERSION["8.5.2111"] = "8.4.2105"  # image:centos/base

#############################################################################

def major(version: str) -> str:
    version = version or CENTOS
    if len(version) == 1 or version[1] == ".":
        return version[0]
    return version[:1]

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

def centos_pull() -> None:
    docker = DOCKER
    distro = DISTRO
    centos = CENTOS
    release = centos
    if centos in OS:
        release = OS[centos]
    if release in BASEVERSION:
        release = BASEVERSION[release]
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

def distro_sync_subdir(distro: str, release: str, subdir: str) -> None:
    # distro = DISTRO
    rsync = RSYNC
    mirror = MIRRORS[distro][0]
    excludes = CENTOS_XXX
    repodir = REPODIR
    sh___(F"{rsync} -rv {mirror}/{release}/{subdir}   {repodir}/{distro}.{release}/ {excludes}")

def centos_sync_AppStream() -> None: distro_sync_subdir(DISTRO, CENTOS, "AppStream")
def centos_sync_BaseOS() -> None: distro_sync_subdir(DISTRO, CENTOS, "BaseOS")
def centos_sync_os() -> None: distro_sync_subdir(DISTRO, CENTOS, "os")
def centos_sync_extras() -> None: distro_sync_subdir(DISTRO, CENTOS, "extras")
def centos_sync_PowerTools() -> None: distro_sync_subdir(DISTRO, CENTOS, "PowerTools")
def centos_sync_centosplus() -> None: distro_sync_subdir(DISTRO, CENTOS, "centosplus")
def centos_sync_updates() -> None: distro_sync_subdir(DISTRO, CENTOS, "updates")
def centos_sync_sclo() -> None: distro_sync_subdir(DISTRO, CENTOS, "sclo")

def centos_epelsync() -> None:
    if CENTOS.startswith("9"):
        centos_epelsync9()
    if CENTOS.startswith("8"):
        centos_epelsync8()
    if CENTOS.startswith("7"):
        centos_epelsync7()

def centos_epelsync9() -> None:
    centos_epelsync9()
def centos_epelsync8() -> None:
    rsync = RSYNC
    distro = EPEL
    centos = CENTOS
    mirror = MIRRORS[distro][0]
    epel = major(centos)
    arch = ARCH
    excludes = """ --exclude "*.iso" """
    for subdir in ["Everything", "Modular"]:
        basedir = F"epel.{epel}/{epel}/{subdir}"
        if not path.isdir(basedir):
            os.makedirs(basedir)
        sh___(F"{rsync} -rv {mirror}/{epel}/{subdir}/{arch} {basedir}/ {excludes}")
def centos_epelsync7() -> None:
    rsync = RSYNC
    distro = EPEL
    centos = CENTOS
    mirror = MIRRORS[distro][0]
    epel = major(centos)
    arch = ARCH
    excludes = """ --exclude "*.iso" """
    sh___(F"{rsync} -rv {mirror}/{epel}/{arch} epel.{epel}/{epel}/ {excludes}")

def centos_unpack() -> None:
    """ used while testing if centos had all packages """
    docker = DOCKER
    distro = DISTRO
    centos = CENTOS
    R = major(centos)
    repodir = REPODIR
    cname = "centos-unpack-" + centos  # container name
    image = "localhost:5000/centos-repo"
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

def centos_epelrepo() -> None:
    if CENTOS.startswith("9"):
        centos_epelrepo9()
    if CENTOS.startswith("8"):
        centos_epelrepo8()
    if CENTOS.startswith("7"):
        centos_epelrepo7()

MAKE_EPEL_HTTP = True
def centos_epelrepo9() -> None:
    centos_epelrepo8()
def centos_epelrepo8() -> None:
    docker = DOCKER
    distro = EPEL
    centos = CENTOS
    epel = major(centos)
    arch = ARCH
    scripts = repo_scripts()
    cname = "epel-repo-" + epel  # container name
    out, end = output2(F"./docker_mirror.py start centos:{centos} -a")
    addhosts = out.strip()
    sx___(F"{docker} rm --force {cname}")
    sh___(F"{docker} run --name={cname} {addhosts} --detach centos:{centos} sleep 9999")
    sh___(F"{docker} exec {cname} mkdir -p /srv/repo/epel/{epel}")
    sh___(F"{docker} exec {cname} yum install -y openssl")
    sh___(F"{docker} cp {scripts} {cname}:/srv/scripts")
    if False:
        # instead we use an explicit epelrepo8_CMD
        for script in os.listdir(F"{scripts}/."):
            sh___(F"{docker} exec {cname} sed -i s:/usr/bin/python:/usr/libexec/platform-python: /srv/scripts/{script}")
            sh___(F"{docker} exec {cname} chmod +x /srv/scripts/{script}")
    base = "base"
    CMD = str(epelrepo8_CMD).replace("'", '"')
    PORT = str(epelrepo8_PORT)
    repo = IMAGESREPO
    yymm = datetime.date.today().strftime("%y%m")
    sh___(F"{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' -m {base} {cname} {repo}/epel-repo/{base}:{epel}.x.{yymm}")
    dists: Dict[str, List[str]] = {}
    dists["main"] = ["Everything"]
    dists["plus"] = ["Modular"]
    for dist in dists:
        sx___(F"{docker} rm --force {cname}")
        sh___(F"{docker} run --name={cname} --detach {repo}/epel-repo/{base}:{epel}.x.{yymm} sleep 9999")
        for subdir in dists[dist]:
            sh___(F"{docker} cp epel.{epel}/{epel}/{subdir} {cname}:/srv/repo/epel/{epel}/")
            base = dist  # !!
        if base == dist:
            sh___(F"{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' -m {base} {cname} {repo}/epel-repo/{base}:{epel}.x.{yymm}")
    sh___(F"{docker} tag {repo}/epel-repo/{base}:{epel}.x.{yymm} {repo}/epel-repo:{epel}.x.{yymm}")
    sx___(F"{docker} rm --force {cname}")
    sh___(F"{docker} rmi {repo}/epel-repo/base:{epel}.x.{yymm}")
    if MAKE_EPEL_HTTP:
        # the upstream epel repository runs on https by default but we don't have their certificate anyway
        CMD2 = str(epelrepo8_http_CMD).replace("'", '"')
        PORT2 = str(epelrepo8_http_PORT)
        base2 = "http"  # !!
        sh___(F"{docker} run --name={cname} --detach {repo}/epel-repo:{epel}.x.{yymm} sleep 9999")
        sh___(F"{docker} commit -c 'CMD {CMD2}' -c 'EXPOSE {PORT2}' -m {base2} {cname} {repo}/epel-repo/{base2}:{epel}.x.{yymm}")
        sx___(F"{docker} rm --force {cname}")

def centos_epelrepo7() -> None:
    docker = DOCKER
    distro = EPEL
    centos = CENTOS
    epel = major(centos)
    arch = ARCH
    scripts = repo_scripts()
    cname = "epel-repo-" + epel  # container name
    sx___(F"{docker} rm --force {cname}")
    sh___(F"{docker} run --name={cname} --detach centos:{centos} sleep 9999")
    sh___(F"{docker} exec {cname} mkdir -p /srv/repo/epel")
    sh___(F"{docker} exec {cname} yum install -y openssl")
    sh___(F"{docker} cp {scripts} {cname}:/srv/scripts")
    for script in os.listdir(f"{scripts}/."):
        sh___(F"{docker} exec {cname} chmod +x /srv/scripts/{script}")
    #
    CMD = str(epelrepo7_CMD).replace("'", '"')
    PORT = str(epelrepo7_PORT)
    CMD2 = str(epelrepo7_http_CMD).replace("'", '"')
    PORT2 = str(epelrepo7_http_PORT)
    repo = IMAGESREPO
    yymm = datetime.date.today().strftime("%y%m")
    sh___(F"{docker} cp epel.{epel}/{epel} {cname}:/srv/repo/epel/")
    sh___(F"{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' {cname} {repo}/epel-repo:{epel}.x.{yymm}")
    sh___(F"{docker} rm --force {cname}")
    if MAKE_EPEL_HTTP:
        # the upstream epel repository runs on https by default but we don't have their certificate anyway
        sh___(F"{docker} run --name={cname} --detach {repo}/epel-repo:{epel}.x.{yymm} sleep 999")
        sh___(F"{docker} commit -c 'CMD {CMD2}' -c 'EXPOSE {PORT2}' {cname} {repo}/epel-repo/http:{epel}.x.{yymm}")
        sh___(F"{docker} rm --force {cname}")


epelrepo8_PORT = 443
epelrepo8_CMD = ["/usr/libexec/platform-python", "/srv/scripts/mirrors.fedoraproject.org.py",
                 "--data", "/srv/repo/epel", "--ssl", "https://mirrors.fedoraproject.org"]
epelrepo8_http_PORT = 80
epelrepo8_http_CMD = ["/usr/libexec/platform-python", "/srv/scripts/mirrors.fedoraproject.org.py", "--data", "/srv/repo/epel"]

epelrepo7_PORT = 443
epelrepo7_CMD = ["/usr/bin/python", "/srv/scripts/mirrors.fedoraproject.org.py",
                 "--data", "/srv/repo/epel", "--ssl", "https://mirrors.fedoraproject.org"]
epelrepo7_http_PORT = 80
epelrepo7_http_CMD = ["/usr/bin/python", "/srv/scripts/mirrors.fedoraproject.org.py", "--data", "/srv/repo/epel"]


centosrepo8_CMD = ["/usr/libexec/platform-python", "/srv/scripts/mirrorlist.py", "--data", "/srv/repo"]
centosrepo8_PORT = 80
centosrepo8_http_CMD = ["/usr/libexec/platform-python", "/srv/scripts/mirrorlist.py", "--data", "/srv/repo"]
centosrepo8_http_PORT = 80
centosrepo7_CMD = ["/usr/bin/python", "/srv/scripts/mirrorlist.py", "--data", "/srv/repo"]
centosrepo7_PORT = 80

def centos_repo() -> None:
    if CENTOS.startswith("9"):
        centos_repo9()
    if CENTOS.startswith("8"):
        centos_repo8()
    if CENTOS.startswith("7"):
        centos_repo7()

def centos_repo9() -> None:
    centos_repo8()
def centos_repo8() -> None:
    docker = DOCKER
    distro = DISTRO
    centos = CENTOS
    R = major(centos)
    repodir = REPODIR
    centos_restore()
    centos_cleaner()
    # image version
    version = centos
    if centos in BASEVERSION:
        version = BASEVERSION[centos]
    scripts = repo_scripts()
    cname = "centos-repo-" + centos  # container name
    sx___(F"{docker} rm --force {cname}")
    sh___(F"{docker} run --name={cname} --detach centos:{version} sleep 9999")
    sh___(F"{docker} exec {cname} mkdir -p /srv/repo/{R}")
    sh___(F"{docker} cp {scripts} {cname}:/srv/scripts")
    base = "base"
    CMD = str(centosrepo8_CMD).replace("'", '"')
    PORT = centosrepo8_PORT
    repo = IMAGESREPO
    sh___(F"{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' -m {base} {cname} {repo}/centos-repo/{base}:{centos}")
    dists = SUBDIRS8
    for dist in dists:
        sx___(F"{docker} rm --force {cname}")
        sh___(F"{docker} run --name={cname} --detach {repo}/centos-repo/{base}:{centos} sleep 9999")
        for subdir in dists[dist]:
            pooldir = F"{repodir}/{distro}.{centos}/{subdir}"
            if path.isdir(pooldir):
                sh___(F"{docker} cp {pooldir} {cname}:/srv/repo/{R}/")
                base = dist
        if base == dist:
            sh___(F"{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' -m {base} {cname} {repo}/centos-repo/{base}:{centos}")
    sh___(F"{docker} rm --force {cname}")
    sh___(F"{docker} tag {repo}/centos-repo/{base}:{centos} {repo}/centos-repo:{centos}")
    sh___(F"{docker} rmi {repo}/centos-repo/base:{centos}")  # untag non-packages base
    centos_restore()
def centos_repo7() -> None:
    docker = DOCKER
    distro = DISTRO
    centos = CENTOS
    R = major(centos)
    repodir = REPODIR
    centos_restore()
    centos_cleaner()
    # image version
    baseversion = centos
    if baseversion in BASEVERSION:
        baseversion = BASEVERSION[baseversion]
    scripts = repo_scripts()
    cname = "centos-repo-" + centos  # container name
    sx___(F"{docker} rm --force {cname}")
    sh___(F"{docker} run --name={cname} --detach centos:{baseversion} sleep 9999")
    sh___(F"{docker} exec {cname} mkdir -p /srv/repo/{R}")
    sh___(F"{docker} cp {scripts} {cname}:/srv/scripts")
    base = "base"
    CMD = str(centosrepo7_CMD).replace("'", '"')
    PORT = centosrepo7_PORT
    repo = IMAGESREPO
    sh___(F"{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' -m {base} {cname} {repo}/centos-repo/{base}:{centos}")
    dists = SUBDIRS7
    for dist in dists:
        sx___(F"{docker} rm --force {cname}")
        sh___(F"{docker} run --name={cname} --detach {repo}/centos-repo/{base}:{centos} sleep 9999")
        for subdir in dists[dist]:
            pooldir = F"{repodir}/{distro}.{centos}/{subdir}"
            if path.isdir(pooldir):
                sh___(F"{docker} cp {pooldir} {cname}:/srv/repo/{R}/")
                base = dist
        if base == dist:
            sh___(F"{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' -m {base} {cname} {repo}/centos-repo/{base}:{centos}")
    sh___(F"{docker} rm --force {cname}")
    sh___(F"{docker} tag {repo}/centos-repo/{base}:{centos} {repo}/centos-repo:{centos}")
    sh___(F"{docker} rmi {repo}/centos-repo/base:{centos}")  # untag non-packages base
    centos_restore()

def centos_tags() -> None:
    docker = DOCKER
    distro = DISTRO
    centos = CENTOS
    repo = IMAGESREPO
    name = F"{distro}-repo"
    ver2 = re.sub("[.]\d+$", "", centos)
    if ver2 != centos:
        sh___(F"{docker} tag {repo}/{name}:{centos} {repo}/{name}:{ver2}")
    ver1 = re.sub("[.]\d+$", "", ver2)
    if ver1 != ver2:
        sh___(F"{docker} tag {repo}/{name}:{centos} {repo}/{name}:{ver1}")
        sh___(F"{docker} tag {repo}/{name}:{centos} {repo}/{name}{ver1}:{centos}")
        sh___(F"{docker} tag {repo}/{name}:{centos} {repo}/{name}{ver1}:latest")

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

def CENTOS_set(centos: str) -> str:
    global CENTOS, DISTRO
    if centos in OS:
        CENTOS = OS[centos]
        return CENTOS
    if centos in ALMA.values():
        CENTOS = max([os for os in ALMA if ALMA[os] == centos])
        DISTRO = ALMALINUX
        return CENTOS
    if len(centos) <= 2:
        CENTOS = max([os for os in OS if os.startswith(centos)])
        return CENTOS
    if centos not in OS.values():
        logg.warning("%s is not a known os version", centos)
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
                func()
            else:
                logg.error("%s is not callable", funcname)
                sys.exit(1)
        else:
            logg.error("%s does not exist", funcname)
            sys.exit(1)
