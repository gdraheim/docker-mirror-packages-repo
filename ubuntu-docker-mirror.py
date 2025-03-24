#! /usr/bin/python3
# pylint: disable=unused-variable,unused-argument,line-too-long
""" sync packages repo to disk and make docker mirror images from it.
    Try to run 'sync' followed be 'repo'. If a command starts with a
    number then it changes the version to be handled. A usual command
    would be 'mirror.py 19.10 sync repo -v'. If no argument is given
    then 'make' the last version = 'sync repo test'."""

__copyright__ = "(C) 2025 Guido Draheim"
__contact__ = "https://github.com/gdraheim/docker-mirror-packages-repo"
__license__ = "CC0 Creative Commons Zero (Public Domain)"
__version__ = "1.7.7112"

from typing import Dict, List, Union, Tuple, Any, Set, Optional
import os
import os.path as path
import sys
import re
import subprocess
import shutil
from fnmatch import fnmatchcase as fnmatch
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

DISTROPYTHON = "python3"
BASELAYER = "base"
DISTRO = "ubuntu"
UBUNTU = "24.04"
DISKSUFFIX = "disk" # suffix
VARIANT = ""

ARCHLIST = ["amd64", "i386", "arm64", "armhf"]
ARCHS = ["amd64", "i386"]
NOARCHS = ["source"]

RSYNC_UBUNTU = "rsync://ftp5.gwdg.de/pub/linux/debian/ubuntu"
RSYNC_DEBIAN = "rsync://ftp5.gwdg.de/pub/linux/debian/debian"


MIRRORS: Dict[str, List[str]] = {}
MIRRORS["ubuntu"] = [RSYNC_UBUNTU]
MIRRORS["debian"] = [RSYNC_DEBIAN]
MIRRORS["debian-security"] = [RSYNC_DEBIAN+"-security"]


UBUNTU_TMP = "ubuntu.tmp"

LTS = ["14.04", "16.04", "18.04", "20.04", "22.04", "24.04"]
DIST: Dict[str, str] = {}
DIST["12.04"] = "precise"  # Precise Pangolin
DIST["12.10"] = "quantal"  # Quntal Quetzal
DIST["14.04"] = "trusty"   # Trusty Tahr LTS    (April 2022)
DIST["14.10"] = "utopic"   # Utopic Unicorn
DIST["16.04"] = "xenial"   # Xenial Xerus LTS   (April 2024)
DIST["16.10"] = "yaketty"  # Yaketty Yak
DIST["17.10"] = "artful"   # Artful Aardvark
DIST["18.04"] = "bionic"   # Bionic Beaver LTS  (April 2028)
DIST["18.10"] = "cosmic"   # Cosmic Cuttlefish  (x)
DIST["19.04"] = "disco"    # Disco Dingo
DIST["19.10"] = "eoan"     # Eoan Ermine
DIST["20.04"] = "focal"    # Focal Fossa LTS    (April 2030)
DIST["20.10"] = "groovy"   # Groovy Gorilla
DIST["21.04"] = "hirsute"  # Hirsute Hippo
DIST["21.10"] = "impish"   # Impish Indri
DIST["22.04"] = "jammy"    # Jammy Jellyfish    (April 2027)
DIST["22.10"] = "kinetic"  # Kinetic Kudu
DIST["23.04"] = "lunatic"  # Lunatic Lobster
DIST["23.10"] = "mantic"   # Mantic Minotaur
DIST["24.04"] = "noble"    # Noble Numbat       (April 2029)
DIST["24.10"] = "oracular" # Oracular Oriole
DIST["25.04"] = "plucky"   # Plucky Puffin
DIST["25.10"] = "qbeta"    # Beta Q             (April 2031)

DEBIANDIST: Dict[str, str] = {}
DEBIANDIST["6"] = "squeeze"
DEBIANDIST["7"] = "wheezy"
DEBIANDIST["8"] = "jessie"
DEBIANDIST["9"] = "stretch"
DEBIANDIST["10"] = "buster"
DEBIANDIST["11"] = "bullseye"
DEBIANDIST["12"] = "bookworm"
DEBIANDIST["13"] = "trixie"
DEBIANDIST["13"] = "forky"

DEBIANDATE: Dict[str, str] = {}
DEBIANDATE["10.1"] = "201909"
DEBIANDATE["10.2"] = "201911"
DEBIANDATE["10.3"] = "202002"
DEBIANDATE["10.4"] = "202005"
DEBIANDATE["10.5"] = "202008"
DEBIANDATE["10.6"] = "202009"
DEBIANDATE["10.7"] = "202012"
DEBIANDATE["10.8"] = "202102"
DEBIANDATE["10.9"] = "202103"
DEBIANDATE["10.10"] = "202103"
DEBIANDATE["10.11"] = "202110"
DEBIANDATE["10.12"] = "202203"
DEBIANDATE["10.13"] = "202209"
DEBIANDATE["11.1"] = "202101"
DEBIANDATE["11.2"] = "202112"
DEBIANDATE["11.3"] = "202203"
DEBIANDATE["11.4"] = "202207"
DEBIANDATE["11.5"] = "202209"
DEBIANDATE["11.6"] = "202212"
DEBIANDATE["11.7"] = "202304"
DEBIANDATE["11.8"] = "202310"
DEBIANDATE["11.9"] = "202402"
DEBIANDATE["11.10"] = "202406"
DEBIANDATE["11.11"] = "202408"
DEBIANDATE["12.1"] = "202307"
DEBIANDATE["12.2"] = "202310"
DEBIANDATE["12.4"] = "202312"
DEBIANDATE["12.5"] = "202402"
DEBIANDATE["12.6"] = "202406"
DEBIANDATE["12.7"] = "202408"
DEBIANDATE["12.8"] = "202409"
DEBIANDATE["12.9"] = "202501"
DEBIANDATE["12.10"] = "202503"
DEBIANDATE["13.1"] = "202506" # TODO: in the future

ONLYREPOS = []
SKIPREPOS = ["universe", "multiverse", "contrib", "non-free"]
UBUNTUREPOS = ["main", "restricted", "universe", "multiverse"]
DEBIANREPOS = ["main", "non-free", "contrib"]
DISTRODIST: Dict[str, Tuple[str, str]] = {}
DISTRODIST["buster-security"] = ("debian-security", "buster/updates")
DISTRODIST["bookworm-security"] = ("debian-security", "bookworm-security")
DISTRODIST["bullseye-security"] = ("debian-security", "bullseye-security")
DISTRODIST["trixie-security"] = ("debian-security", "trixie-security")
AREAS = {"1": "", "2": "-updates", "3": "-backports", "4": "-security"}

nolinux = ["linux-image*.deb", "linux-module*.deb", "linux-objects*.deb", "linux-source*.deb"]
nolinux += ["linux-restricted*.deb", "linux-signed*.deb", "linux-buildinfo*.deb", ]
nolinux += ["linux-oracle*.deb", "linux-headers*.deb", "linux-virtual*.deb", "linux-cloud*.deb"]
nolinux += ["linux-lowlatency*.deb", "linux-kvm*.deb", "linux-generic*.deb", "linux-crashdump*.deb"]
nolinux += ["linux-risc*.deb", "linux-meta*.deb", "linux-doc*.deb", "linux-tools*.deb"]
nolinux += ["linux-gcp*.deb", "linux-gke*.deb", "linux-azure*.deb", "linux-oem*.deb", ]
nolinux += ["linux-hwe*.deb", "linux-aws*.deb", "linux-intel*.deb", "linux-ibm*.deb", ]
nodrivers = ["nvidia-*.deb", "libnvidia*.deb"]

DUMMYPACKAGES = """
Filename: pool/dummy/linux-image.deb
Filename: pool/dummy/nvidia-driver.deb
"""

BASEVERSION: Dict[str, str] = {}  # image:ubuntu/base
BASEVERSION["23.04"] = "22.04"
BASEVERSION["22.10"] = "22.04"  # previous LTS
BASEVERSION["22.04"] = "22.04"
BASEVERSION["21.10"] = "20.04"
BASEVERSION["21.04"] = "20.04"
BASEVERSION["20.10"] = "20.04"
BASEVERSION["19.10"] = "18.04"
BASEVERSION["19.04"] = "18.04"
BASEVERSION["18.10"] = "18.04"
BASEVERSION["16.10"] = "16.04"

def _iterable(x: Any) -> bool:
    return hasattr(x, "__iter__")

def ubuntu_allrepos(distro: str = NIX, ubuntu: str = NIX) -> List[str]:
    distro = distro or DISTRO
    if distro in ["debian"]:
        return DEBIANREPOS
    else:
        return UBUNTUREPOS
def ubuntu_distdirs(distro: str = NIX, ubuntu: str = NIX) -> List[str]:
    distro = distro or DISTRO
    ubuntu = ubuntu or UBUNTU
    if distro in ["debian"]:
        return [DEBIANDIST[ubuntu], DEBIANDIST[ubuntu] + "-updates", DEBIANDIST[ubuntu] + "-security"]
    else:
        return [DIST[ubuntu], DIST[ubuntu] + "-updates", DIST[ubuntu] + "-backports", DIST[ubuntu] + "-security"]

def ubuntu_distros(distro: str = NIX, ubuntu: str = NIX) -> List[str]:
    distro = distro or DISTRO
    ubuntu = ubuntu or UBUNTU
    values: Set[str] = set()
    for dist in ubuntu_distdirs(distro, ubuntu):
        distrodir, distdir = distro, dist
        if dist in DISTRODIST:
            distrodir, distdir = DISTRODIST[dist]
        values.add(distrodir)
    return list(sorted(values))

######################################################################

# the Ubuntu package repository has the deb packages of all version and all repos
# and almost all areas in the same ./pool subdirectory. It is only the package lists
# that are hosted in different subdirectories. However the 4/-security area is on
# a different download host (not archive.ubuntu.com but security.ubuntu.com) which
# is enabled by default. Don't ask.
# .... since docker-py requires "universe" we better default to mirror the repos for
# "main updates universe" which can be achived by running 'make xxx REPOS=universe'
# but that changes making the docker repo image size from about 18Gi to 180Gi

def ubuntu_sync() -> None:
    ubuntu_dir()
    if DISTRO in ["ubuntu"]:
        # release files:
        ubuntu_sync_base(DIST[UBUNTU])
        ubuntu_sync_base(DIST[UBUNTU] + "-updates")
        ubuntu_sync_base(DIST[UBUNTU] + "-backports")
        ubuntu_sync_base(DIST[UBUNTU] + "-security")
        # main:
        ubuntu_sync_dist_main(DIST[UBUNTU])
        ubuntu_sync_dist_main(DIST[UBUNTU] + "-updates")
        ubuntu_sync_dist_main(DIST[UBUNTU] + "-backports")
        ubuntu_sync_dist_main(DIST[UBUNTU] + "-security")
        restricted = "restricted"
        ubuntu_sync_dist_main(DIST[UBUNTU], restricted)
        ubuntu_sync_dist_main(DIST[UBUNTU] + "-updates", restricted)
        ubuntu_sync_dist_main(DIST[UBUNTU] + "-backports", restricted)
        ubuntu_sync_dist_main(DIST[UBUNTU] + "-security", restricted)
        restricted = "universe"
        ubuntu_sync_dist_main(DIST[UBUNTU], restricted)
        ubuntu_sync_dist_main(DIST[UBUNTU] + "-updates", restricted)
        ubuntu_sync_dist_main(DIST[UBUNTU] + "-backports", restricted)
        ubuntu_sync_dist_main(DIST[UBUNTU] + "-security", restricted)
        if "multiverse" not in SKIPREPOS or "multiverse" in ONLYREPOS:
            restricted = "muiltiverse"
            ubuntu_sync_dist_main(DIST[UBUNTU], restricted)
            ubuntu_sync_dist_main(DIST[UBUNTU] + "-updates", restricted)
            ubuntu_sync_dist_main(DIST[UBUNTU] + "-backports", restricted)
            ubuntu_sync_dist_main(DIST[UBUNTU] + "-security", restricted)
    elif DISTRO in ["debian"]:
        # release files:
        ubuntu_sync_base(DEBIANDIST[UBUNTU])
        ubuntu_sync_base(DEBIANDIST[UBUNTU] + "-updates")
        ubuntu_sync_base(DEBIANDIST[UBUNTU] + "-security")
        # main:
        ubuntu_sync_dist_main(DEBIANDIST[UBUNTU])
        ubuntu_sync_dist_main(DEBIANDIST[UBUNTU] + "-updates")
        ubuntu_sync_dist_main(DEBIANDIST[UBUNTU] + "-security")
    else:
        logg.error("unknown distro %s", DISTRO)
        raise UserWarning("unknown distro")

def ubuntu_datadir() -> str:
    for data in reversed(DATADIRS):
        logg.debug(".. check %s", data)
        if path.isdir(data):
            return data
    return REPODIR

def ubuntu_dir(distro: str = NIX, ubuntu: str = NIX, variant: str = NIX) -> str:
    distro = distro or DISTRO
    ubuntu = ubuntu or UBUNTU
    repodir = REPODIR
    variant = variant or VARIANT
    version = F"{ubuntu}.{variant}" if variant else ubuntu
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

def ubuntu_sync_base(dist: str) -> None:
    logg.info("dist = %s", dist)
    cache = ubuntu_cache()
    distro = DISTRO
    ubuntu = UBUNTU
    distrodir, distdir = distro, dist
    if dist in DISTRODIST:
        distrodir, distdir = DISTRODIST[dist]
    rootdir = ubuntu_dir(distrodir, ubuntu, VARIANT)
    savedir = F"{rootdir}/dists/{distdir}"
    if not path.isdir(savedir):
        os.makedirs(savedir)
    tmpfile = F"{cache}/Release.{dist}.base.tmp"
    with open(tmpfile, "w") as f:
        print("Release", file=f)
        print("Release.gpg", file=f)
        print("InRelease", file=f)
    rsync = RSYNC
    distro = DISTRO
    mirror = MIRRORS[distrodir][0]
    options = "--ignore-times --files-from=" + tmpfile
    options +=" --copy-links"
    # excludes = " ".join(["--exclude '%s'" % parts for parts in nolinux])
    sh___(F"{rsync} -v {mirror}/dists/{distdir} {rootdir}/dists/{distdir} {options}")

def ubuntu_sync_dist_main(dist: str, main: str = "main") -> None:
    nopackages = False
    if ONLYREPOS and main not in ONLYREPOS:
        logg.info(" -- skip [%s] repo -- not in ONLYREPOS %s", main, ONLYREPOS)
        nopackages = True
    if SKIPREPOS and main in SKIPREPOS:
        logg.info(" -- skip [%s] repo -- was in SKIPREPOS %s", main, SKIPREPOS)
        nopackages = True
    return _sync_dist_main(NIX, NIX, dist, main, nopackages=nopackages)
def _sync_dist_main(distro: str, ubuntu: str, dist: str, main: str, nopackages: bool = False) -> None: # pylint: disable=redefined-outer-name
    distro = distro or DISTRO
    ubuntu = ubuntu or UBUNTU
    distrodir, distdir = distro, dist
    if dist in DISTRODIST:
        distrodir, distdir = DISTRODIST[dist]
    rootdir = ubuntu_dir(distrodir, ubuntu, VARIANT)
    maindir = F"{rootdir}/dists/{distdir}/{main}"
    if not path.isdir(maindir):
        os.makedirs(maindir)
    rsync = RSYNC
    mirror = MIRRORS[distrodir][0]
    # excludes = " ".join(["--exclude '%s'" % parts for parts in nolinux])
    options = "--ignore-times --exclude=.~tmp~"
    for arch in ARCHS:
        sh___(F"{rsync} -rv {mirror}/dists/{distdir}/{main}/binary-{arch} {maindir} {options} --copy-links")
    for source in NOARCHS:
        sh___(F"{rsync} -rv {mirror}/dists/{distdir}/{main}/{source}      {maindir} {options} --copy-links")
    gzlist: List[str] = []
    for arch in ARCHS:
        packages_gz = F"{maindir}/binary-{arch}/Packages.gz"
        packages_xz = F"{maindir}/binary-{arch}/Packages.xz"
        if os.path.isfile(packages_gz):
            gzlist.append(packages_gz)
        elif os.path.isfile(packages_xz):
            gzlist.append(packages_xz) # buster-updates only has *.xz
        else:
            logg.warning("Packages.gz missing: %s & %s", packages_gz, packages_xz)
    cache = ubuntu_cache()
    tmpfile = F"{cache}/Packages.{dist}.{main}.tmp"
    if outdated(tmpfile, *gzlist):
        packages = ""
        for gz in gzlist:
            if gz.endswith(".xz"):
                packages += output(F"xzcat {gz}")
            else:
                packages += output(F"zcat {gz}")
            packages += "\n"
        if "--dry-run" in rsync:
            packages = DUMMYPACKAGES # should be removed from sync list below
        filenames, syncing = 0, 0
        with open(tmpfile, "w") as f:
            for line in packages.split("\n"):
                if not line.startswith("Filename:"):
                    continue
                filename = re.sub("Filename: *pool/", "", line)
                filenames += 1
                skip = False
                if "/linux" in filename:
                    for parts in nolinux:
                        if fnmatch(filename, parts): skip = True
                        if fnmatch(filename, "*/" + parts): skip = True
                if TRUE:
                    for parts in nodrivers:
                        if fnmatch(filename, parts): skip = True
                        if fnmatch(filename, "*/" + parts): skip = True
                if not skip:
                    print(filename, file=f)
                    syncing += 1
        logg.info("syncing %s of %s filenames in %s", syncing, filenames, " & ".join(gzlist))
    pooldir = F"{rootdir}/pools/{distdir}/{main}/pool"
    if not path.isdir(pooldir):
        os.makedirs(pooldir)
    # instead of {exlude} we have nolinux filtered in the Packages above
    if not nopackages:
        options = "--size-only --copy-links "
        sh___(F"{rsync} -rv {mirror}/pool {pooldir} {options} --files-from={tmpfile}")

def ubuntu_http_port() -> str:
    return "80"
def ubuntu_http_cmd() -> List[str]:
    python = DISTROPYTHON
    if "/" not in python:
        python = F"/usr/bin/{python}"
    return [python, "/srv/scripts/filelist.py", "--data", "/srv/repo"]
def ubuntu_base(distro: str = NIX, ubuntu: str = NIX) -> str:
    return repo_image(distro, ubuntu, [])
def ubuntu_repo(distro: str = NIX, ubuntu: str = NIX) -> str:
    distro = distro or DISTRO
    ubuntu = ubuntu or UBUNTU
    allrepos = ubuntu_allrepos(distro, ubuntu)
    repos = []
    for repo in allrepos:
        if ONLYREPOS and repo not in ONLYREPOS:
            continue
        if repo not in SKIPREPOS:
            repos += [ repo ]
    if not repos:
        logg.warning("no %s repo layers selected with ONLYREPOS %s SKIPREPOS %s", distro, ONLYREPOS, SKIPREPOS)
    else:
        logg.info("image repo layers = %s", repos)
    return repo_image(distro, ubuntu, repos, allrepos)
def repo_image(distro: str = NIX, ubuntu: str = NIX, repos: Optional[List[str]] = None, allrepos: Optional[List[str]] = None) -> str:
    docker = DOCKER
    distro = distro or DISTRO
    ubuntu = ubuntu or UBUNTU
    allrepos = allrepos if allrepos is not None else ubuntu_allrepos(distro, ubuntu)
    repos = repos if repos is not None else allrepos
    # repodir = REPODIR
    baseimage = ubuntu_baseimage(distro, ubuntu)
    imagesrepo = IMAGESREPO
    python = DISTROPYTHON
    scripts = ubuntu_scripts()
    rootdir = ubuntu_dir(distro, ubuntu, VARIANT)
    version = F"{ubuntu}.{VARIANT}" if VARIANT else ubuntu
    cname = F"{distro}-repo-{version}"  # container name
    sx___(F"{docker} rm --force {cname}")
    sh___(F"{docker} run --name={cname} --detach {baseimage} sleep 9999")
    sh___(F"{docker} cp {scripts} {cname}:/srv/scripts")
    dists = ubuntu_distdirs(distro, ubuntu)
    if TRUE:  # base layer needs all Release info files even when pool files are not copied
        for dist in dists:
            distrodir, distdir = distro, dist
            if dist in DISTRODIST:
                distrodir, distdir = DISTRODIST[dist]
            rootdir = ubuntu_dir(distrodir, ubuntu, variant=F"{VARIANT}")
            relsdir = F"{rootdir}/dists/{distdir}"
            relsdir_srv = F"/srv/repo/{distrodir}/dists/{distdir}"
            releasefiles = []
            for relfile in ["Release", "Release.gpg", "InRelease"]:
                releasefile = os.path.join(relsdir, relfile)
                if os.path.isfile(releasefile):
                    releasefiles += [ releasefile ]
            if releasefiles:
                sh___(F"{docker} exec {cname} bash -c 'test -d {relsdir_srv} || mkdir -vp {relsdir_srv}'")
                for releasefile in releasefiles:
                    sh___(F"{docker} cp {releasefile} {cname}:{relsdir_srv}/")
            for main in allrepos:
                for arch in ARCHS:
                    packdir = F"{relsdir}/{main}/binary-{arch}"
                    packagesfiles = []
                    for packages_gz in ["Packages.gz", "Packages.xz"]:
                        packagesfile = os.path.join(packdir, packages_gz)
                        if os.path.isfile(packagesfile):
                            packagesfiles += [ packagesfile ]
                    if packagesfiles:
                        sh___(F"{docker} exec {cname} bash -c 'test -d {relsdir_srv}/{main} || mkdir -vp {relsdir_srv}/{main}'")
                        sh___(F"{docker} cp {packdir} {cname}:/{relsdir_srv}/{main}/")
                for source in NOARCHS:
                    packdir = F"{relsdir}/{source}"
                    packagesfiles = []
                    for packages_gz in ["Packages.gz", "Packages.xz"]:
                        packagesfile = os.path.join(packdir, packages_gz)
                        if os.path.isfile(packagesfile):
                            packagesfiles += [ packagesfile ]
                    if packagesfiles:
                        sh___(F"{docker} exec {cname} bash -c 'test -d {relsdir_srv}/{main} || mkdir -vp {relsdir_srv}/{main}'")
                        sh___(F"{docker} cp {packdir} {cname}:/{relsdir_srv}/{main}/")
    sh___(F"{docker} exec {cname} apt-get update")
    sh___(F"{docker} exec {cname} apt-get install -y {python}")
    sh___(F"{docker} exec {cname} mkdir -p /srv/repo/{distro}/pool")
    base = BASELAYER
    PORT = ubuntu_http_port()
    CMD = str(ubuntu_http_cmd()).replace("'", '"')
    sh___(F"{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' -m {base} {cname} {imagesrepo}/{distro}-repo/{base}:{version}")
    for main in repos:
        if ONLYREPOS and main not in ONLYREPOS:
            logg.info("'%s' not in ONLYREPOS %s", main, ONLYREPOS)
            continue
        if SKIPREPOS and main in SKIPREPOS:
            logg.info("'%s' in SKIPREPOS %s", main, ONLYREPOS)
            continue
        sh___(F"{docker} rm --force {cname}")
        sh___(F"{docker} run --name={cname} --detach {imagesrepo}/{distro}-repo/{base}:{version} sleep 9999")
        dists = ubuntu_distdirs(distro, ubuntu)
        for dist in dists:
            distrodir, distdir = distro, dist
            if dist in DISTRODIST:
                distrodir, distdir = DISTRODIST[dist]
            rootdir = ubuntu_dir(distrodir, ubuntu, variant=F"{VARIANT}")
            pooldir = F"{rootdir}/pools/{distdir}/{main}/pool"
            if path.isdir(pooldir):
                sh___(F"{docker} cp {pooldir}  {cname}:/srv/repo/{distrodir}/")
                base = main
        if base == main:
            sh___(F"{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' -m {base} {cname} {imagesrepo}/{distro}-repo/{base}:{version}")
    if base != BASELAYER:
        sh___(F"{docker} tag {imagesrepo}/{distro}-repo/{base}:{version} {imagesrepo}/{distro}-repo:{version}")
    sh___(F"{docker} rm --force {cname}")
    if NOBASE:
        sx___(F"{docker} rmi {imagesrepo}/{distro}-repo/base:{version}")  # untag base image
    return F"\n[{baseimage}]\nimage = {imagesrepo}/{distro}-repo/{base}:{version}\n"

def ubuntu_disk() -> str:
    distro = DISTRO
    ubuntu = UBUNTU
    version = F"{ubuntu}.{VARIANT}" if VARIANT else ubuntu
    diskdir = ubuntu_dir(distro, ubuntu, variant=F"{VARIANT}{DISKSUFFIX}")
    srv = F"{diskdir}/srv"
    logg.info("srv = %s", srv)
    sh___(F"test ! -d {srv} || rm -rf {srv}")
    sh___(F"mkdir -p {srv}/repo/{distro}/pool")
    repos = ubuntu_allrepos(distro, ubuntu)
    dists = ubuntu_distdirs(distro, ubuntu)
    if TRUE:  # base layer needs all Release info files even when pool files are not copied
        for dist in dists:
            distrodir, distdir = distro, dist
            if dist in DISTRODIST:
                distrodir, distdir = DISTRODIST[dist]
            rootdir = ubuntu_dir(distrodir, ubuntu, variant=F"{VARIANT}")
            relsdir = F"{rootdir}/dists/{distdir}"
            relsdir_srv = F"{srv}/repo/{distrodir}/dists/{distdir}"
            for relfile in ["Release", "Release.gpg", "InRelease"]:
                releasefile = os.path.join(relsdir, relfile)
                if os.path.isfile(releasefile):
                    if not os.path.isdir(relsdir_srv):
                        os.makedirs(relsdir_srv)
                    sh___(F"cp {releasefile} {relsdir_srv}/")
    for main in repos:
        if ONLYREPOS and main not in ONLYREPOS:
            logg.info("'%s' not in ONLYREPOS %s", main, ONLYREPOS)
            continue
        if SKIPREPOS and main in SKIPREPOS:
            logg.info("'%s' in SKIPREPOS %s", main, ONLYREPOS)
            continue
        for dist in dists:
            distrodir, distdir = distro, dist
            if dist in DISTRODIST:
                distrodir, distdir = DISTRODIST[dist]
            rootdir = ubuntu_dir(distrodir, ubuntu, variant=F"{VARIANT}")
            maindir = F"{rootdir}/dists/{distdir}/{main}"
            maindir_srv = F"{srv}/repo/{distrodir}/dists/{distdir}/{main}"
            if not os.path.isdir(maindir_srv):
                os.makedirs(maindir_srv)
            for arch in ARCHS:
                if os.path.isdir(F"{maindir}/binary-{arch}"):
                    sh___(F"cp -r --link {maindir}/binary-{arch} {maindir_srv}/")
            for source in NOARCHS:
                if os.path.isdir(F"{maindir}/{source}"):
                    sh___(F"cp -r --link {maindir}/{source} {maindir_srv}/")
            pooldir = F"{rootdir}/pools/{distdir}/{main}/pool"
            updates = "" if "/" not in distrodir else "/"+distrodir.split("/", 1)[1]
            if path.isdir(pooldir):
                if not os.path.isdir(F"{srv}/repo/{distrodir}"):
                    os.makedirs(F"{srv}/repo/{distrodir}")
                sh___(F"cp -r --link --no-clobber {pooldir}  {srv}/repo/{distrodir}/")
    host_srv = os.path.realpath(srv)
    return F"\nmount = {host_srv}/repo\n"

def ubuntu_diskpath() -> str:
    rootdir = ubuntu_dir(variant=F"{VARIANT}{DISKSUFFIX}")
    srv = F"{rootdir}/srv"
    path_srv = os.path.realpath(srv)
    return F"{path_srv}/repo\n"

def ubuntu_dropdisk() -> str:
    rootdir = ubuntu_dir(variant=F"{VARIANT}{DISKSUFFIX}")
    srv = F"{rootdir}/srv"
    path_srv = os.path.realpath(srv)
    if os.path.isdir(path_srv):
        shutil.rmtree(path_srv)
    return path_srv

def ubuntu_baserepo(distro: str = NIX, ubuntu: str = NIX, imagesrepo: str = NIX) -> str:
    imagesrepo = imagesrepo or IMAGESREPO
    distro = distro or DISTRO
    leap = ubuntu or UBUNTU
    version = F"{leap}.{VARIANT}" if VARIANT else leap
    base = BASELAYER
    return F"{imagesrepo}/{distro}-repo/{base}:{version}"
def ubuntu_mainrepo(distro: str = NIX, ubuntu: str = NIX, imagesrepo: str = NIX) -> str:
    imagesrepo = imagesrepo or IMAGESREPO
    distro = distro or DISTRO
    leap = ubuntu or UBUNTU
    version = F"{leap}.{VARIANT}" if VARIANT else leap
    base = BASELAYER
    return F"{imagesrepo}/{distro}-repo/{base}:{version}"

def ubuntu_local(distro: str = NIX, centos: str = NIX) -> int:
    """ show ini section for diskpath and --universe """
    mainsection = ubuntu_baseimage(distro, centos)
    mainbaseimage = ubuntu_baserepo(distro, centos)
    maindiskpath = ubuntu_diskpath()
    return F"[{mainsection}]\nimage={mainbaseimage}\nmount={maindiskpath}"

def ubuntu_list(distro: str = NIX, ubuntu: str = NIX) -> int:
    docker = DOCKER
    print(F"REPOSITORY:TAG\tSIZE          # {docker} images {{baseimage}} {{baserepo}} {{mainrepo}}")
    baseimage = ubuntu_baseimage(distro, ubuntu)
    logg.debug("docker image list %s", baseimage)
    cmd = F"{docker} image list {baseimage} -q --format '{{{{.Repository}}}}:{{{{.Tag}}}}\t{{{{.Size}}}}'"
    sx1 = sx___(cmd)
    baserepo = ubuntu_baserepo(distro, ubuntu)
    logg.debug("docker image list %s", baserepo)
    cmd = F"{docker} image list {baserepo} -q --format '{{{{.Repository}}}}:{{{{.Tag}}}}\t{{{{.Size}}}}'"
    sx2 = sx___(cmd)
    mainrepo = ubuntu_mainrepo(distro, ubuntu)
    logg.debug("docker image list %s", mainrepo)
    cmd = F"{docker} image list {mainrepo} -q --format '{{{{.Repository}}}}:{{{{.Tag}}}}\t{{{{.Size}}}}'"
    sx3 = sx___(cmd)
    return min(sx1, sx2, sx3)

def ubuntu_scripts() -> str:
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
def outdated(cachefile: str, *files: str) -> bool:
    if not os.path.exists(cachefile):
        return True
    cached = os.path.getmtime(cachefile)
    for filename in files:
        if not os.path.exists(filename):
            return True
        older = os.path.getmtime(filename)
        if cached < older:
            return True
    return False

def xdg_cache_home() -> str:
    value = os.environ.get("XDG_CACHE_HOME", "~/.cache")
    return os.path.expanduser(value)

def ubuntu_cache() -> str:
    distro = DISTRO
    ubuntu = UBUNTU
    version = F"{ubuntu}.{VARIANT}" if VARIANT else ubuntu
    cachedir = xdg_cache_home()
    basedir = F"{cachedir}/docker_mirror"
    maindir = F"{cachedir}/docker_mirror/{distro}.{version}"
    if not os.path.isdir(maindir):
        os.makedirs(maindir)
    return maindir

def ubuntu_image(distro: str = NIX, ubuntu: str = NIX) -> str:
    image = distro or DISTRO
    ubuntu = ubuntu or UBUNTU
    version = F"{ubuntu}.{VARIANT}" if VARIANT else ubuntu
    return F"{image}:{version}"
def ubuntu_baseimage(distro: str = NIX, ubuntu: str = NIX) -> str:
    image = distro or DISTRO
    ubuntu = ubuntu or UBUNTU
    if ubuntu in BASEVERSION:
        ubuntu = BASEVERSION[ubuntu]
    version = F"{ubuntu}.{VARIANT}" if VARIANT else ubuntu
    return F"{image}:{version}"

def ubuntu_version(distro: str = NIX, ubuntu: str = NIX) -> str:
    distro = distro or DISTRO
    ubuntu = ubuntu or UBUNTU
    if ":" in ubuntu:
        distro, ubuntu = ubuntu.split(":", 1)
    if distro in ["ubuntu"]:
        if len(ubuntu) <= 2:
            found = max([os for os in DIST if os.startswith(ubuntu)])
            logg.info("UBUNTU:=%s (max %s)", found, ubuntu)
            return found
        if ubuntu in DIST.values():
            for version, dist in DIST.items():
                if dist == ubuntu:
                    logg.info("UBUNTU %s -> %s", dist, version)
                    return version
        elif ubuntu not in DIST:
            logg.warning("UBUNTU=%s is not a known os version", ubuntu)
            return ubuntu
        else:
            logg.debug("UBUNTU=%s override", ubuntu)
            return ubuntu
    elif distro in ["debian"]:
        if ubuntu not in DEBIANDIST:
            logg.warning("UBUNTU=%s is not a known os version", ubuntu)
            return ubuntu
        else:
            logg.debug("UBUNTU=%s override", ubuntu)
            return ubuntu
    else:
        logg.error("not a known distro %s", distro)
        raise UserWarning("not a known distro")


def UBUNTU_set(ubuntu: str) -> str:
    global UBUNTU, DISTRO # pylint: disable=global-statement
    distro = ""
    if ubuntu in ["10","11","12","13"]:
        DISTRO = "debian"
    if ":" in ubuntu:
        distro, ubuntu = ubuntu.split(":", 1)
        DISTRO = distro
    UBUNTU = ubuntu_version(ubuntu=ubuntu)
    return UBUNTU

def ubuntu_commands() -> str:
    cmds: List[str] = []
    for name in sorted(globals()):
        if name.startswith("ubuntu_"):
            if "_sync_" in name: continue
            if "_http_" in name: continue
            if name.endswith("_"): continue
            func = globals()[name]
            if callable(func):
                cmd = name.replace("ubuntu_", "")
                cmds += [cmd]
    return "|".join(cmds)

def _main(args: List[str]) -> int:
    for arg in args:
        if arg[0] in "123456789":
            UBUNTU_set(arg)
            continue
        if ":" in arg and arg.split(":", 1)[1][0] in "123456789":
            UBUNTU_set(arg)
            continue
        funcname = "ubuntu_" + arg.replace("-", "_")
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
    cmdline = OptionParser("%%prog [-options] [%s]" % ubuntu_commands(),
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
                       help="set $REPODATADIR -> "+(REPODATADIR if REPODATADIR else ubuntu_datadir()))
    cmdline.add_option("--imagesrepo", metavar="PREFIX", default=IMAGESREPO,
                       help="set $IMAGESREPO [%default]")
    cmdline.add_option("--disksuffix", metavar="NAME", default=DISKSUFFIX,
                       help="use disk suffix for testing [%default]")
    cmdline.add_option("-W", "--variant", metavar="NAME", default=VARIANT,
                       help="use variant suffix for testing [%default]")
    cmdline.add_option("-V", "--ver", metavar="NUM", default=UBUNTU,
                       help="use other ubuntu version [%default]")
    cmdline.add_option("-a", "--arch", metavar="NAME", action="append", default=[],
                       help=F"use other arch list {ARCHS}")
    cmdline.add_option("-n", "--nopackages", action="store_true", default=False,
                       help="only check metadata [%default]")
    cmdline.add_option("-m", "--main", action="store_true", default=False,
                       help="only sync main packages [%default]")
    cmdline.add_option("-u", "--updates", action="store_true", default=False,
                       help="only main and updates packages [%default]")
    cmdline.add_option("-U", "--universe", action="store_true", default=False,
                       help="include universe packages [%default]")
    cmdline.add_option("-M", "--multiverse", action="store_true", default=False,
                       help="include all ubuntu packages [%default]")
    cmdline.add_option("-C", "--contrib", action="store_true", default=False,
                       help="include contrib and free packages [%default]")
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
    DISTROPYTHON = opt.python
    UBUNTU_set(opt.ver)
    if opt.main:
        ONLYREPOS = ["main"]
    if opt.updates:
        ONLYREPOS = ["main", "update"] # this is the effecitve default
    if opt.universe:
        SKIPREPOS = [repo for repo in SKIPREPOS if repo not in ["universe"]]
    if opt.multiverse:
        SKIPREPOS = [repo for repo in SKIPREPOS if repo not in ["universe", "multiverse"]]
    if opt.contrib:
        SKIPREPOS = [repo for repo in SKIPREPOS if repo not in ["non-free", "contrib"]]
    if opt.nopackages:
        ONLYREPOS = ["--nopackages"]
    #
    sys.exit(_main(cmdline_args or ["list"]))
