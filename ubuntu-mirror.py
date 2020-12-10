#! /usr/bin/python3
""" sync packages repo to disk and make docker mirror images from it.
    Try to run 'sync' followed be 'repo'. If a command starts with a
    number then it changes the version to be handled. A usual command
    would be 'mirror.py 19.10 sync repo -v'. If no argument is given
    then 'make' the last version = 'sync pool repo test tags'."""

# from __future__ import literal_string_interpolation # PEP498 Python3.6
from typing import Optional, Dict, List, Tuple, Union
import os
import os.path as path
import sys
import re
import subprocess
import shutil
import logging
logg = logging.getLogger("MIRROR")

if sys.version[0] == '3':
    basestring = str
    xrange = range

IMAGESREPO = os.environ.get("IMAGESREPO", "localhost:5000/mirror-packages")
REPODATADIR = os.environ.get("REPODATADIR", "")

DATADIRS= [ REPODATADIR,
    "/srv/docker-mirror-packages",
    "/data/docker-mirror-packages",
    "/data/docker-centos-repo-mirror",
    "/dock/docker-mirror-packages"]


UBUNTU_OS = "ubuntu"
UBUNTU = "20.04"
RSYNC_UBUNTU = "rsync://ftp5.gwdg.de/pub/linux/debian/ubuntu"

UBUNTU_TMP = "ubuntu.tmp"

LTS = [ "14.04", "16.04", "18.04", "20.04" ]
DIST: Dict[str, str] = {}
DIST["20.10"] = "groovy"
DIST["20.04"] = "focal"
DIST["19.10"] = "eoan"
DIST["19.04"] = "disco"
DIST["18.10"] = "cosmic"
DIST["18.04"] = "bionic"
DIST["17.10"] = "artful"
DIST["16.04"] = "xenial"
DIST["14.04"] = "trusty"
DIST["12.04"] = "precise"

REPOS = ["main", "updates"]
UNI_REPOS = ["main", "updates", "restricted", "universe"]
ALL_REPOS = ["main", "updates", "restricted", "universe", "multiverse"]
AREAS = {"1": "", "2": "-updates", "3": "-backports", "4": "-security"}

DOCKER = "docker"
RSYNC = "rsync"

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
    ubuntu_pool() # backard compat
    ubuntu_repo()
    ubuntu_test()
    ubuntu_tags()

def ubuntu_sync() -> None:
    ubuntu_dir()
    ubuntu_sync_base_1()
    ubuntu_sync_base_2()
    ubuntu_sync_base_3()
    ubuntu_sync_base_4()
    ubuntu_sync_main_1()
    ubuntu_sync_restricted_1()
    ubuntu_sync_universe_1()
    ubuntu_sync_multiverse_1()
    ubuntu_sync_main_2()
    ubuntu_sync_restricted_2()
    ubuntu_sync_universe_2()
    ubuntu_sync_multiverse_2()
    ubuntu_sync_main_3()
    ubuntu_sync_restricted_3()
    ubuntu_sync_universe_3()
    ubuntu_sync_multiverse_3()
    ubuntu_sync_main_4()
    ubuntu_sync_restricted_4()
    ubuntu_sync_universe_4()
    ubuntu_sync_multiverse_4()

def ubuntu_dir() -> None:
    ubuntu = UBUNTU
    dirname = "ubuntu.{ubuntu}".format(**locals())
    if path.isdir(dirname):
        if path.islink(dirname):
            os.unlink(dirname)
        else:
            shutil.rmtree(dirname) # local dir
    # we want to put the mirror data on an external disk
    for data in reversed(DATADIRS):
        logg.debug(".. check %s", data)
        if path.isdir(data):
            dirpath = path.join(data, dirname)
            if not path.isdir(dirpath):
                os.makedirs(dirpath)
            os.symlink(dirpath, dirname)
            break
    dircheck = path.join(dirname, ".")
    if path.isdir(dircheck):
        logg.info("%s -> %s", dirname, dirpath)
    else:
        os.mkdir(dirname) # local dir
        logg.warning("%s/. local dir", dirname)


def ubuntu_sync_base_1() -> None: ubuntu_sync_base(dist=DIST[UBUNTU])
def ubuntu_sync_base_2() -> None: ubuntu_sync_base(dist=DIST[UBUNTU]+"-updates")
def ubuntu_sync_base_3() -> None: ubuntu_sync_base(dist=DIST[UBUNTU]+"-backports")
def ubuntu_sync_base_4() -> None: ubuntu_sync_base(dist=DIST[UBUNTU]+"-security")
def ubuntu_sync_base(dist: str) -> None:
    logg.info("dist = %s", dist)
    tmpdir = UBUNTU_TMP
    ubuntu = UBUNTU
    distdir = "ubuntu.{ubuntu}/dists/{dist}".format(**locals())
    if not path.isdir(distdir):
        os.makedirs(distdir)
    if not path.isdir(tmpdir):
        os.makedirs(tmpdir)
    tmpfile = "{tmpdir}/Release.{dist}.base.tmp".format(**locals())
    with open(tmpfile, "w") as f:
         print("Release", file=f)
         print("InRelease", file=f)
    rsync = RSYNC
    mirror = RSYNC_UBUNTU
    options = "--ignore-times --files-from="+tmpfile
    sh___("{rsync} -v {mirror}/dists/{dist} ubuntu.{ubuntu}/dists/{dist} {options}".format(**locals()))

def when(levels: str, repos: List[str]) -> List[str]: return [ item for item in levels.split(",") if item and item in repos ]
def ubuntu_sync_main_1() -> None:       ubuntu_sync_main(dist=DIST[UBUNTU], main="main", when=when("updates,restricted,universe,multiverse", REPOS))
def ubuntu_sync_restricted_1() -> None: ubuntu_sync_main(dist=DIST[UBUNTU], main="restricted", when=when("restricted,universe,multiverse", REPOS))
def ubuntu_sync_universe_1() -> None:   ubuntu_sync_main(dist=DIST[UBUNTU], main="universe", when=when("universe,multiverse", REPOS))
def ubuntu_sync_multiverse_1() -> None: ubuntu_sync_main(dist=DIST[UBUNTU], main="multiverse", when=when("multiverse", REPOS))
def ubuntu_sync_main_2() -> None:       ubuntu_sync_main(dist=DIST[UBUNTU]+"-updates", main="main", when=when("updates,restricted,universe,multiverse", REPOS))
def ubuntu_sync_restricted_2() -> None: ubuntu_sync_main(dist=DIST[UBUNTU]+"-updates", main="restricted", when=when("restricted,universe,multiverse", REPOS))
def ubuntu_sync_universe_2() -> None:   ubuntu_sync_main(dist=DIST[UBUNTU]+"-updates", main="universe", when=when("universe,multiverse", REPOS))
def ubuntu_sync_multiverse_2() -> None: ubuntu_sync_main(dist=DIST[UBUNTU]+"-updates", main="multiverse", when=when("multiverse", REPOS))
def ubuntu_sync_main_3() -> None:       ubuntu_sync_main(dist=DIST[UBUNTU]+"-backports", main="main", when=when("updates,restricted,universe,multiverse", REPOS))
def ubuntu_sync_restricted_3() -> None: ubuntu_sync_main(dist=DIST[UBUNTU]+"-backports", main="restricted", when=when("restricted,universe,multiverse", REPOS))
def ubuntu_sync_universe_3() -> None:   ubuntu_sync_main(dist=DIST[UBUNTU]+"-backports", main="universe", when=when("universe,multiverse", REPOS))
def ubuntu_sync_multiverse_3() -> None: ubuntu_sync_main(dist=DIST[UBUNTU]+"-backports", main="multiverse", when=when("multiverse", REPOS))
def ubuntu_sync_main_4() -> None:       ubuntu_sync_main(dist=DIST[UBUNTU]+"-security", main="main",  when=when("updates,restricted,universe,multiverse", REPOS))
def ubuntu_sync_restricted_4() -> None: ubuntu_sync_main(dist=DIST[UBUNTU]+"-security", main="restricted", when=when("restricted,universe,multiverse", REPOS))
def ubuntu_sync_universe_4() -> None:   ubuntu_sync_main(dist=DIST[UBUNTU]+"-security", main="universe", when=when("universe,multiverse", REPOS))
def ubuntu_sync_multiverse_4() -> None: ubuntu_sync_main(dist=DIST[UBUNTU]+"-security", main="multiverse", when=when("multiverse", REPOS))

downloads=["universe"]
def ubuntu_check() -> None:
        print(": %s" % when("update,universe", downloads))

def ubuntu_sync_main(dist: str, main: str, when: List[str]) -> None:
    ubuntu = UBUNTU
    maindir= "ubuntu.{ubuntu}/dists/{dist}/{main}".format(**locals())
    if not path.isdir(maindir): os.makedirs(maindir)
    rsync = RSYNC
    mirror = RSYNC_UBUNTU
    sh___("{rsync} -rv {mirror}/dists/{dist}/{main}/binary-amd64 {maindir} --ignore-times".format(**locals()))
    sh___("{rsync} -rv {mirror}/dists/{dist}/{main}/binary-i386  {maindir} --ignore-times".format(**locals()))
    sh___("{rsync} -rv {mirror}/dists/{dist}/{main}/source       {maindir} --ignore-times".format(**locals()))
    gz1 = "{maindir}/binary-amd64/Packages.gz".format
    packages=output("zcat {maindir}/binary-amd64/Packages.gz {maindir}/binary-i386/Packages.gz".format(**locals()))
    tmpdir = UBUNTU_TMP
    if not path.isdir(tmpdir): os.makedirs(tmpdir)
    tmpfile = "{tmpdir}/Packages.{dist}.{main}.tmp".format(**locals())
    with open(tmpfile, "w") as f:
        for line in packages.split("\n"):
            if not line.startswith("Filename:"):
                continue
            filename = re.sub("Filename: *pool/", "", line)
            print(filename, file=f)
    pooldir= "ubuntu.{ubuntu}/pools/{dist}/{main}/pool".format(**locals())
    if not path.isdir(pooldir): os.makedirs(pooldir)
    if when:
      	sh___("{rsync} -rv {mirror}/pool {pooldir} --size-only --files-from={tmpfile}".format(**locals()))

def ubuntu_pool() -> None:
    ubuntu = UBUNTU
    pooldir = "ubuntu.{UBUNTU}/pool".format(**locals())
    if path.isdir(pooldir): shutil.rmtree(pooldir)
    os.makedirs(pooldir)
   # find ubuntu.$(UBUNTU)/pools/$(dist) -name pool -type d \
   # | { while read pool; do (cd $$pool && find . -type f) \
   #    | { while read f; do b=`dirname "$$f"` \
   #      ; test -d ubuntu.$(UBUNTU)/pool/$$f || \
   #       mkdir -p ubuntu.$(UBUNTU)/pool/$$b \
   #      ; ln $$pool/$$f ubuntu.$(UBUNTU)/pool/$$b/ \
   #      ; done ; } \
   #   ; done ; } \
   # ; echo `find ubuntu.$(UBUNTU)/pool -type f | wc -l` pool files

def ubuntu_poolcount() -> None:
    ubuntu = UBUNTU
    sh___("echo `find ubuntu.{ubuntu}/pool -type f | wc -l` pool files".format(**locals()))

ubunturepo_CMD = ["python","/srv/scripts/filelist.py","--data","/srv/repo"]
ubunturepo_PORT = "80"
def ubuntu_repo() -> None:
    docker = DOCKER
    ubuntu = UBUNTU
    image = UBUNTU_OS
    imagesrepo = IMAGESREPO
    cname = "ubuntu-repo-"+ubuntu # container name
    sx___("{docker} rm --force {cname}".format(**locals()))
    sh___("{docker} run --name={cname} --detach {image}:{ubuntu} sleep 9999".format(**locals()))
    sh___("{docker} exec {cname} mkdir -p /srv/repo/ubuntu".format(**locals()))
    sh___("{docker} exec {cname} mkdir -p /srv/repo/ubuntu".format(**locals()))
    sh___("{docker} cp scripts {cname}:/srv/scripts".format(**locals()))
    sh___("{docker} cp ubuntu.{ubuntu}/dists {cname}:/srv/repo/ubuntu".format(**locals()))
    sh___("{docker} cp ubuntu.{ubuntu}/pool  {cname}:/srv/repo/ubuntu".format(**locals()))
    sh___("{docker} exec {cname} apt-get update".format(**locals()))
    sh___("{docker} exec {cname} apt-get install -y python".format(**locals()))
    CMD = ubunturepo_CMD ; PORT = ubunturepo_PORT
    sh___("{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' {cname} {imagesrepo}/ubuntu-repo:{ubuntu}".format(**locals()))
    sh___("{docker} rm --force {cname}".format(**locals()))
    if REPOS: ubuntu_tags()

def ubuntu_tags() -> None:
    docker = DOCKER
    ubuntu = UBUNTU
    imagesrepo = IMAGESREPO
    if when("updates,restricted,universe,multiverse", REPOS):
        sh___("{docker} tag {imagesrepo}/ubuntu-repo:{ubuntu} {imagesrepo}/ubuntu-repo/updates:{ubuntu}".format(**locals()))
    if when("restricted,universe,multiverse", REPOS):
        sh___("{docker} tag {imagesrepo}/ubuntu-repo:{ubuntu} {imagesrepo}/ubuntu-repo/restricted:{ubuntu}".format(**locals()))
    if when("universe,multiverse", REPOS):
        sh___("{docker} tag {imagesrepo}/ubuntu-repo:{ubuntu} {imagesrepo}/ubuntu-repo/universe:{ubuntu}".format(**locals()))
    if when("multiverse", REPOS):
        sh___("{docker} tag {imagesrepo}/ubuntu-repo:{ubuntu} {imagesrepo}/ubuntu-repo/multiverse:{ubuntu}".format(**locals()))

def ubuntu_test() -> None:
    ubuntu = UBUNTU
    # cat ubuntu-compose.yml | sed \
    #    -e 's|ubuntu-repo:.*"|ubuntu/repo:$(UBUNTU)"|' \
    #    -e 's|ubuntu:.*"|$(UBUNTU_OS):$(UBUNTU)"|' \
    #    > ubuntu-compose.yml.tmp
    # - docker-compose -p $@ -f ubuntu-compose.yml.tmp down
    # docker-compose -p $@ -f ubuntu-compose.yml.tmp up -d
    # docker exec $@_host_1 apt-get install -y firefox
    # docker-compose -p $@ -f ubuntu-compose.yml.tmp down

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

def sh___(cmd: Union[str, List[str]], shell:bool=True) -> int:
    if isinstance(cmd, basestring):
        logg.info(": %s", cmd)
    else:    
        logg.info(": %s", " ".join(["'%s'" % item for item in cmd]))
    return subprocess.check_call(cmd, shell=shell)

def sx___(cmd: Union[str, List[str]], shell:bool=True) -> int:
    if isinstance(cmd, basestring):
        logg.info(": %s", cmd)
    else:    
        logg.info(": %s", " ".join(["'%s'" % item for item in cmd]))
    return subprocess.call(cmd, shell=shell)
def output(cmd: Union[str, List[str]], shell:bool=True) -> str:
    if isinstance(cmd, basestring):
        logg.info(": %s", cmd)
    else:    
        logg.info(": %s", " ".join(["'%s'" % item for item in cmd]))
    run = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE)
    out, err = run.communicate()
    return decodes(out)
def output2(cmd: Union[str,List[str]], shell:bool=True) -> Tuple[str, int]:
    if isinstance(cmd, basestring):
        logg.info(": %s", cmd)
    else:    
        logg.info(": %s", " ".join(["'%s'" % item for item in cmd]))
    run = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE)
    out, err = run.communicate()
    return decodes(out), run.returncode
def output3(cmd: Union[str,List[str]], shell:bool=True) -> Tuple[str, str, int]:
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

def commands() -> str:
    cmds : List[str] = []
    for name in sorted(globals()):
        if name.startswith("ubuntu_"):
            if "_sync_" in name: continue
            func = globals()[name]
            if callable(func):
                cmd = name.replace("ubuntu_", "")
                cmds += [ cmd ]
    return "|".join(cmds)

def UBUNTU_set(ubuntu: str) -> str:
    global UBUNTU
    if len(ubuntu) <= 2:
        UBUNTU=max([os for os in DIST if os.startswith(ubuntu)])
        return UBUNTU
    if ubuntu in DIST.values():
       for version, dist in DIST.items():
          if dist == ubuntu:
              UBUNTU = version
              break
    elif ubuntu not in DIST:
        logg.warning("%s is not a known os version", ubuntu)
        UBUNTU = ubuntu
    return UBUNTU

if __name__ == "__main__":
    from optparse import OptionParser
    _o = OptionParser("%%prog [-options] [%s]" % commands(),
       epilog=re.sub("\\s+", " ", __doc__).strip())
    _o.add_option("-v","--verbose", action="count", default=0,
       help="increase logging level [%default]")
    _o.add_option("-D","--docker", metavar="EXE", default=DOCKER,
       help="use other docker exe or podman [%default]")
    _o.add_option("-V","--ver", metavar="NUM", default=UBUNTU,
       help="use other ubuntu version [%default]")
    _o.add_option("-u","--universe", action="store_true", default=False,
       help="include universe packages [%default]")
    _o.add_option("-m","--multiverse", action="store_true", default=False,
       help="include all packages [%default]")
    opt, args = _o.parse_args()
    logging.basicConfig(level = logging.WARNING - opt.verbose * 10)
    #
    DOCKER = opt.docker
    UBUNTU_set(opt.ver)
    if opt.universe:
        REPOS = UNI_REPOS
    if opt.multiverse:
        REPOS = ALL_REPOS
    #
    if not args: args = [ "make" ]
    for arg in args:
        if arg[0] in "123456789":
           UBUNTU_set(arg)
           continue
        funcname = "ubuntu_"+arg.replace("-", "_")
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
