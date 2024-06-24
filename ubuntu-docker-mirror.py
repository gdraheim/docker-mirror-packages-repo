#! /usr/bin/python3
""" sync packages repo to disk and make docker mirror images from it.
    Try to run 'sync' followed be 'repo'. If a command starts with a
    number then it changes the version to be handled. A usual command
    would be 'mirror.py 19.10 sync repo -v'. If no argument is given
    then 'make' the last version = 'sync repo test'."""

__copyright__ = "(C) 2024 Guido Draheim"
__contact__ = "https://github.com/gdraheim/docker-mirror-packages-repo"
__license__ = "CC0 Creative Commons Zero (Public Domain)"
__version__ = "1.7.6261"

# from __future__ import literal_string_interpolation # PEP498 Python3.6
from typing import Optional, Dict, List, Tuple, Union
import os
import os.path as path
import sys
import re
import subprocess
import shutil
from fnmatch import fnmatchcase as fnmatch
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

PYTHON = "python3"
DISTRO = "ubuntu"
UBUNTU = "24.04"
RSYNC_UBUNTU = "rsync://ftp5.gwdg.de/pub/linux/debian/ubuntu"

MIRRORS: Dict[str, List[str]] = {}
MIRRORS["ubuntu"] = [RSYNC_UBUNTU]

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

MAIN_REPOS = ["main"]
UPDATES_REPOS = ["main", "restricted"]
UNIVERSE_REPOS = ["main", "restricted", "universe"]
MULTIVERSE_REPOS = ["main", "restricted", "universe", "multiverse"]
AREAS = {"1": "", "2": "-updates", "3": "-backports", "4": "-security"}

nolinux = ["linux-image*.deb", "linux-module*.deb", "linux-objects*.deb", "linux-source*.deb"]
nolinux += ["linux-restricted*.deb", "linux-signed*.deb", "linux-buildinfo*.deb", ]
nolinux += ["linux-oracle*.deb", "linux-headers*.deb", "linux-virtual*.deb", "linux-cloud*.deb"]
nolinux += ["linux-lowlatency*.deb", "linux-kvm*.deb", "linux-generic*.deb", "linux-crashdump*.deb"]
nolinux += ["linux-risc*.deb", "linux-meta*.deb", "linux-doc*.deb", "linux-tools*.deb"]
nolinux += ["linux-gcp*.deb", "linux-gke*.deb", "linux-azure*.deb", "linux-oem*.deb", ]
nolinux += ["linux-hwe*.deb", "linux-aws*.deb", "linux-intel*.deb", "linux-ibm*.deb", ]
nodrivers = ["nvidia-*.deb", "libnvidia*.deb"]

REPOS = UPDATES_REPOS
DOCKER = "docker"
RSYNC = "rsync"

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

######################################################################

# the Ubuntu package repository has the deb packages of all version and all repos
# and almost all areas in the same ./pool subdirectory. It is only the package lists
# that are hosted in different subdirectories. However the 4/-security area is on
# a different download host (not archive.ubuntu.com but security.ubuntu.com) which
# is enabled by default. Don't ask.
# .... since docker-py requires "universe" we better default to mirror the repos for
# "main updates universe" which can be achived by running 'make xxx REPOS=universe'
# but that changes making the docker repo image size from about 18Gi to 180Gi

def ubuntu_make() -> None:
    ubuntu_sync()
    ubuntu_repo()
    ubuntu_test()

def ubuntu_sync() -> None:
    ubuntu_dir()
    # release files:
    ubuntu_sync_base_1()
    ubuntu_sync_base_2()
    ubuntu_sync_base_3()
    ubuntu_sync_base_4()
    # main:
    ubuntu_sync_main_1()
    ubuntu_sync_restricted_1()
    ubuntu_sync_universe_1()
    ubuntu_sync_multiverse_1()
    # updates:
    ubuntu_sync_main_2()
    ubuntu_sync_restricted_2()
    ubuntu_sync_universe_2()
    ubuntu_sync_multiverse_2()
    # backports:
    ubuntu_sync_main_3()
    ubuntu_sync_restricted_3()
    ubuntu_sync_universe_3()
    ubuntu_sync_multiverse_3()
    # security:
    ubuntu_sync_main_4()
    ubuntu_sync_restricted_4()
    ubuntu_sync_universe_4()
    ubuntu_sync_multiverse_4()

def ubuntu_dir(suffix: str = "") -> str:
    distro = DISTRO
    ubuntu = UBUNTU
    repodir = REPODIR
    dirname = F"{distro}.{ubuntu}{suffix}"
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

def ubuntu_du(suffix: str = "") -> str:
    distro = DISTRO
    ubuntu = UBUNTU
    repodir = REPODIR
    dirpath = F"{repodir}/{distro}.{ubuntu}{suffix}/."
    logg.info(F"dirpath {dirpath}")
    if os.path.isdir(dirpath):
        sh___(F"du -sh {dirpath}")
    return dirpath

def ubuntu_nolinux(suffix: str = "") -> str:
    distro = DISTRO
    ubuntu = UBUNTU
    repodir = REPODIR
    dirpath = F"{repodir}/{distro}.{ubuntu}{suffix}/."
    logg.info(F"dirpath {dirpath}")
    for root, dirs, files in os.walk(dirpath):
        for name in files:
            if name.startswith("linux"):
                filename = os.path.join(root, name)
                skip = False
                for parts in nolinux:
                    if fnmatch(filename, parts): skip = True
                    if fnmatch(filename, "*/" + parts): skip = True
                if skip:
                    logg.warning("remove %s", filename)
                    os.unlink(filename)
    return ""

def ubuntu_sync_base_1() -> None: ubuntu_sync_base(dist=DIST[UBUNTU])
def ubuntu_sync_base_2() -> None: ubuntu_sync_base(dist=DIST[UBUNTU] + "-updates")
def ubuntu_sync_base_3() -> None: ubuntu_sync_base(dist=DIST[UBUNTU] + "-backports")
def ubuntu_sync_base_4() -> None: ubuntu_sync_base(dist=DIST[UBUNTU] + "-security")
def ubuntu_sync_base(dist: str) -> None:
    logg.info("dist = %s", dist)
    cache = ubuntu_cache()
    distro = DISTRO
    ubuntu = UBUNTU
    repodir = REPODIR
    distdir = F"{repodir}/{distro}.{ubuntu}/dists/{dist}"
    if not path.isdir(distdir):
        os.makedirs(distdir)
    tmpfile = F"{cache}/Release.{dist}.base.tmp"
    with open(tmpfile, "w") as f:
        print("Release", file=f)
        print("InRelease", file=f)
    rsync = RSYNC
    distro = DISTRO
    mirror = MIRRORS[distro][0]
    options = "--ignore-times --files-from=" + tmpfile
    # excludes = " ".join(["--exclude '%s'" % parts for parts in nolinux])
    sh___(F"{rsync} -v {mirror}/dists/{dist} {repodir}/{distro}.{ubuntu}/dists/{dist} {options}")

def when(levels: str, repos: List[str]) -> List[str]: return [item for item in levels.split(",") if item and item in repos]
def ubuntu_sync_main_1() -> None: ubuntu_sync_main(dist=DIST[UBUNTU], main="main", when=when("updates,restricted,universe,multiverse", REPOS))
def ubuntu_sync_restricted_1() -> None: ubuntu_sync_main(dist=DIST[UBUNTU], main="restricted", when=when("restricted,universe,multiverse", REPOS))
def ubuntu_sync_universe_1() -> None: ubuntu_sync_main(dist=DIST[UBUNTU], main="universe", when=when("universe,multiverse", REPOS))
def ubuntu_sync_multiverse_1() -> None: ubuntu_sync_main(dist=DIST[UBUNTU], main="multiverse", when=when("multiverse", REPOS))
def ubuntu_sync_main_2() -> None: ubuntu_sync_main(dist=DIST[UBUNTU] + "-updates", main="main", when=when("updates,restricted,universe,multiverse", REPOS))
def ubuntu_sync_restricted_2() -> None: ubuntu_sync_main(dist=DIST[UBUNTU] + "-updates", main="restricted", when=when("restricted,universe,multiverse", REPOS))
def ubuntu_sync_universe_2() -> None: ubuntu_sync_main(dist=DIST[UBUNTU] + "-updates", main="universe", when=when("universe,multiverse", REPOS))
def ubuntu_sync_multiverse_2() -> None: ubuntu_sync_main(dist=DIST[UBUNTU] + "-updates", main="multiverse", when=when("multiverse", REPOS))
def ubuntu_sync_main_3() -> None: ubuntu_sync_main(dist=DIST[UBUNTU] + "-backports", main="main", when=when("updates,restricted,universe,multiverse", REPOS))
def ubuntu_sync_restricted_3() -> None: ubuntu_sync_main(dist=DIST[UBUNTU] + "-backports", main="restricted", when=when("restricted,universe,multiverse", REPOS))
def ubuntu_sync_universe_3() -> None: ubuntu_sync_main(dist=DIST[UBUNTU] + "-backports", main="universe", when=when("universe,multiverse", REPOS))
def ubuntu_sync_multiverse_3() -> None: ubuntu_sync_main(dist=DIST[UBUNTU] + "-backports", main="multiverse", when=when("multiverse", REPOS))
def ubuntu_sync_main_4() -> None: ubuntu_sync_main(dist=DIST[UBUNTU] + "-security", main="main", when=when("updates,restricted,universe,multiverse", REPOS))
def ubuntu_sync_restricted_4() -> None: ubuntu_sync_main(dist=DIST[UBUNTU] + "-security", main="restricted", when=when("restricted,universe,multiverse", REPOS))
def ubuntu_sync_universe_4() -> None: ubuntu_sync_main(dist=DIST[UBUNTU] + "-security", main="universe", when=when("universe,multiverse", REPOS))
def ubuntu_sync_multiverse_4() -> None: ubuntu_sync_main(dist=DIST[UBUNTU] + "-security", main="multiverse", when=when("multiverse", REPOS))

downloads = ["universe"]
def ubuntu_check() -> None:
    print(": %s" % when("update,universe", downloads))

def ubuntu_sync_main(dist: str, main: str, when: List[str]) -> None:
    distro = DISTRO
    ubuntu = UBUNTU
    repodir = REPODIR
    maindir = F"{repodir}/{distro}.{ubuntu}/dists/{dist}/{main}"
    if not path.isdir(maindir): os.makedirs(maindir)
    rsync = RSYNC
    mirror = MIRRORS[distro][0]
    # excludes = " ".join(["--exclude '%s'" % parts for parts in nolinux])
    options = "--ignore-times"
    sh___(F"{rsync} -rv {mirror}/dists/{dist}/{main}/binary-amd64 {maindir} {options}")
    sh___(F"{rsync} -rv {mirror}/dists/{dist}/{main}/binary-i386  {maindir} {options}")
    sh___(F"{rsync} -rv {mirror}/dists/{dist}/{main}/source       {maindir} {options}")
    gz1 = F"{maindir}/binary-amd64/Packages.gz"
    gz2 = F"{maindir}/binary-i386/Packages.gz"
    cache = ubuntu_cache()
    tmpfile = F"{cache}/Packages.{dist}.{main}.tmp"
    if outdated(tmpfile, gz1, gz2):
        packages = output(F"zcat {gz1} {gz2}")
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
                if True:
                    for parts in nodrivers:
                        if fnmatch(filename, parts): skip = True
                        if fnmatch(filename, "*/" + parts): skip = True
                if not skip:
                    print(filename, file=f)
                    syncing += 1
        logg.info("syncing %s of %s filenames in %s", syncing, filenames, gz1)
    pooldir = F"{repodir}/{distro}.{ubuntu}/pools/{dist}/{main}/pool"
    if not path.isdir(pooldir): os.makedirs(pooldir)
    if when:
        # instead of {exlude} we have nolinux filtered in the Packages above
        options = "--size-only"
        sh___(F"{rsync} -rv {mirror}/pool {pooldir} {options} --files-from={tmpfile}")

def ubuntu_pool() -> None:
    distro = DISTRO
    ubuntu = UBUNTU
    repodir = REPODIR
    pooldir = F"{repodir}/{distro}.{UBUNTU}/pool"
    if path.isdir(pooldir):
        shutil.rmtree(pooldir)
    os.makedirs(pooldir)

def ubuntu_poolcount() -> None:
    distro = DISTRO
    ubuntu = UBUNTU
    repodir = REPODIR
    sh___(F"echo `find {repodir}/{distro}.{ubuntu}/pool -type f | wc -l` pool files")

def ubuntu_http_port() -> str:
    return "80"
def ubuntu_http_cmd() -> List[str]:
    python = PYTHON
    if "/" not in python:
        python = F"/usr/bin/{python}"
    return [python, "/srv/scripts/filelist.py", "--data", "/srv/repo"]
def ubuntu_repo() -> None:
    docker = DOCKER
    distro = DISTRO
    ubuntu = UBUNTU
    repodir = REPODIR
    baseimage = ubuntu_baseimage(distro, ubuntu)
    imagesrepo = IMAGESREPO
    python = PYTHON
    scripts = repo_scripts()
    cname = F"{distro}-repo-{ubuntu}"  # container name
    sx___(F"{docker} rm --force {cname}")
    sh___(F"{docker} run --name={cname} --detach {baseimage} sleep 9999")
    sh___(F"{docker} exec {cname} mkdir -p /srv/repo/ubuntu")
    sh___(F"{docker} exec {cname} mkdir -p /srv/repo/ubuntu")
    sh___(F"{docker} cp {scripts} {cname}:/srv/scripts")
    sh___(F"{docker} cp {repodir}/{distro}.{ubuntu}/dists {cname}:/srv/repo/ubuntu")
    sh___(F"{docker} exec {cname} apt-get update")
    sh___(F"{docker} exec {cname} apt-get install -y {python}")
    sh___(F"{docker} exec {cname} mkdir -p /srv/repo/ubuntu/pool")
    base = "base"
    PORT = ubuntu_http_port()
    CMD = str(ubuntu_http_cmd()).replace("'", '"')
    sh___(F"{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' -m {base} {cname} {imagesrepo}/{distro}-repo/{base}:{ubuntu}")
    for main in REPOS:
        sh___(F"{docker} rm --force {cname}")
        sh___(F"{docker} run --name={cname} --detach {imagesrepo}/{distro}-repo/{base}:{ubuntu} sleep 9999")
        for dist in [DIST[ubuntu], DIST[ubuntu] + "-updates", DIST[ubuntu] + "-backports", DIST[ubuntu] + "-security"]:
            pooldir = F"{repodir}/{distro}.{ubuntu}/pools/{dist}/{main}/pool"
            if path.isdir(pooldir):
                sh___(F"{docker} cp {pooldir}  {cname}:/srv/repo/ubuntu/")
                base = main
        if base == main:
            sh___(F"{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' -m {base} {cname} {imagesrepo}/{distro}-repo/{base}:{ubuntu}")
    sh___(F"{docker} tag {imagesrepo}/{distro}-repo/{base}:{ubuntu} {imagesrepo}/{distro}-repo:{ubuntu}")
    sh___(F"{docker} rm --force {cname}")
    sx___(F"{docker} rmi {imagesrepo}/{distro}-repo/base:{ubuntu}")  # untag base image

def ubuntu_test() -> None:
    distro = DISTRO
    ubuntu = UBUNTU
    # cat ubuntu-compose.yml | sed \
    #    -e 's|ubuntu-repo:.*"|ubuntu/repo:$(UBUNTU)"|' \
    #    -e 's|ubuntu:.*"|$(DISTRO):$(UBUNTU)"|' \
    #    > ubuntu-compose.yml.tmp
    # - docker-compose -p $@ -f ubuntu-compose.yml.tmp down
    # docker-compose -p $@ -f ubuntu-compose.yml.tmp up -d
    # docker exec $@_host_1 apt-get install -y firefox
    # docker-compose -p $@ -f ubuntu-compose.yml.tmp down

def ubuntu_scripts() -> None:
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
    cachedir = xdg_cache_home()
    basedir = F"{cachedir}/docker_mirror"
    maindir = F"{cachedir}/docker_mirror/{distro}.{ubuntu}"
    if not os.path.isdir(maindir):
        os.makedirs(maindir)
    return maindir

def path_find(base: str, name: str) -> Optional[str]:
    for dirpath, dirnames, filenames in os.walk(base):
        if name in filenames:
            return path.join(dirpath, name)
    return None

def ubuntu_commands_() -> None:
    print(commands())
def commands() -> str:
    cmds: List[str] = []
    for name in sorted(globals()):
        if name.startswith("ubuntu_"):
            if "_sync_" in name: continue
            if name.endswith("_"): continue
            func = globals()[name]
            if callable(func):
                cmd = name.replace("ubuntu_", "")
                cmds += [cmd]
    return "|".join(cmds)

def ubuntu_image(distro: str = NIX, ubuntu: str = NIX) -> str:
    image = distro or DISTRO
    version = ubuntu or UBUNTU
    return F"{image}:{version}"
def ubuntu_baseimage(distro: str = NIX, ubuntu: str = NIX) -> str:
    image = distro or DISTRO
    version = ubuntu or UBUNTU
    if version in BASEVERSION:
        version = BASEVERSION[version]
    return F"{image}:{version}"

def UBUNTU_set(ubuntu: str) -> str:
    global UBUNTU, DISTRO
    distro = ""
    if ":" in ubuntu:
        distro, ubuntu = ubuntu.split(":", 1)
        DISTRO = distro
    if len(ubuntu) <= 2:
        UBUNTU = max([os for os in DIST if os.startswith(ubuntu)])
        logg.info(F"UBUNTU:={UBUNTU} (max {ubuntu})")
        return UBUNTU
    if ubuntu in DIST.values():
        for version, dist in DIST.items():
            if dist == ubuntu:
                UBUNTU = version
                logg.info("UBUNTU {dist} -> {version}", dist, version)
                break
    elif ubuntu not in DIST:
        logg.warning("UBUNTU=%s is not a known os version", ubuntu)
        UBUNTU = ubuntu
    else:
        logg.debug("UBUNTU=%s override", ubuntu)
        UBUNTU = ubuntu
    return UBUNTU

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
    _o.add_option("-V", "--ver", metavar="NUM", default=UBUNTU,
                  help="use other ubuntu version [%default]")
    _o.add_option("-m", "--main", action="store_true", default=False,
                  help="only sync main packages [%default]")
    _o.add_option("-u", "--updates", action="store_true", default=False,
                  help="only main and updates packages [%default]")
    _o.add_option("-U", "--universe", action="store_true", default=False,
                  help="include universe packages [%default]")
    _o.add_option("-M", "--multiverse", action="store_true", default=False,
                  help="include all packages [%default]")
    _o.add_option("-c", "--config", metavar="NAME=VAL", action="append", default=[],
                  help="override globals (REPODIR, REPODATADIRS, IMAGESREPO)")
    opt, args = _o.parse_args()
    logging.basicConfig(level=logging.WARNING - opt.verbose * 10)
    config_globals(opt.config)
    DOCKER = opt.docker
    UBUNTU_set(opt.ver)
    if opt.main:
        REPOS = MAIN_REPOS
    if opt.updates:
        REPOS = UPDATES_REPOS  # this is the default
    if opt.universe:
        REPOS = UNIVERSE_REPOS  # includes restricted-repos
    if opt.multiverse:
        REPOS = MULTIVERSE_REPOS
    #
    if not args: args = ["make"]
    for arg in args:
        if arg[0] in "123456789":
            UBUNTU_set(arg)
            continue
        funcname = "ubuntu_" + arg.replace("-", "_")
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
