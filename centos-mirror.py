#! /usr/bin/python3
""" sync packages repo to disk and make docker mirror images from it.
    Try to run 'sync' followed be 'repo'. If a command starts with a
    number then it changes the version to be handled. A usual command
    would be 'mirror.py 7.7 sync repo -v'. If no argument is given
    then 'make' the last version = 'sync pull repo test check tags'.
    ((with ''epelsync'' and ''epelrepo'' you can also take a snapshot
     from the fedora epel repos (which do not have real releases)))."""

__copyright__ = "(C) 2021 Guido Draheim"
__contact__ = "https://github.com/gdraheim/docker-mirror-packages-repo"
__license__ = "CC0 Creative Commons Zero (Public Domain)"
__version__ = "1.6.2504"

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
REPODIR = os.environ.get("REPODIR", ".")

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

X7CENTOS = max([os for os in OS if os.startswith("7.")])
X8CENTOS = max([os for os in OS if os.startswith("8.")])
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


#############################################################################

def major(version: str) -> str:
    version = version or CENTOS
    return version[0]

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
    centos = CENTOS
    if centos == X7CENTOS:
        sh___("{docker} pull centos:7".format(**locals()))
        sh___("{docker} tag  centos:7 centos:{centos}".format(**locals()))
    if centos == X8CENTOS:
        sh___("{docker} pull centos:8".format(**locals()))
        sh___("{docker} tag  centos:8 centos:{centos}".format(**locals()))

def centos_sync() -> None:
    centos = CENTOS
    centos_dir()
    if centos.startswith("7"):
        centos_sync_os()
        centos_sync_extras()
        centos_sync_updates()
        centos_sync_sclo()
    if centos.startswith("8"):
        centos_sync_BaseOS()
        centos_sync_AppStream()
        centos_sync_extras()
        centos_sync_PowerTools()
        centos_sync_centosplus()
        centos_sync_sclo()

def centos_dir() -> None:
    centos = CENTOS
    repodir = REPODIR
    dirname = "{repodir}/centos.{centos}".format(**locals())
    if path.isdir(dirname):
        if path.islink(dirname):
            os.unlink(dirname)
        else:
            shutil.rmtree(dirname)  # local dir
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
        os.mkdir(dirname)  # local dir
        logg.warning("%s/. local dir", dirname)

def centos_epeldir() -> None:
    centos = CENTOS
    epel = major(centos)
    dirname = "epel.{epel}".format(**locals())
    if path.isdir(dirname):
        if path.islink(dirname):
            os.unlink(dirname)
        else:
            shutil.rmtree(dirname)  # local dir
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
        os.mkdir(dirname)  # local dir
        logg.warning("%s/. local dir", dirname)

CENTOS_XXX = " ".join([
    "--exclude ppc64le",
    "--exclude aarch64",
    "--exclude EFI",
    "--exclude images",
    "--exclude isolinux",
    "--exclude '*.iso'",
])

def sync_subdir(subdir: str) -> None:
    rsync = RSYNC
    mirror = CENTOS_MIRROR
    centos = CENTOS
    excludes = CENTOS_XXX
    repodir = REPODIR
    sh___("{rsync} -rv {mirror}/{centos}/{subdir}   {repodir}/centos.{centos}/ {excludes}".format(**locals()))

def centos_sync_AppStream() -> None: sync_subdir("AppStream")
def centos_sync_BaseOS() -> None: sync_subdir("BaseOS")
def centos_sync_os() -> None: sync_subdir("os")
def centos_sync_extras() -> None: sync_subdir("extras")
def centos_sync_PowerTools() -> None: sync_subdir("PowerTools")
def centos_sync_centosplus() -> None: sync_subdir("centosplus")
def centos_sync_updates() -> None: sync_subdir("updates")
def centos_sync_sclo() -> None: sync_subdir("sclo")

def centos_epelsync() -> None:
    if CENTOS.startswith("7"):
        centos_epelsync7()
    if CENTOS.startswith("8"):
        centos_epelsync8()

def centos_epelsync7() -> None:
    rsync = RSYNC
    mirror = EPEL_MIRROR
    centos = CENTOS
    epel = major(centos)
    arch = ARCH
    excludes = """ --exclude "*.iso" """
    sh___("{rsync} -rv {mirror}/{epel}/{arch} epel.{epel}/{epel}/ {excludes}".format(**locals()))
def centos_epelsync8() -> None:
    rsync = RSYNC
    mirror = EPEL_MIRROR
    centos = CENTOS
    epel = major(centos)
    arch = ARCH
    excludes = """ --exclude "*.iso" """
    for subdir in ["Everything", "Modular"]:
        basedir = "epel.{epel}/{epel}/{subdir}".format(**locals())
        if not path.isdir(basedir):
            os.makedirs(basedir)
        sh___("{rsync} -rv {mirror}/{epel}/{subdir}/{arch} {basedir}/ {excludes}".format(**locals()))

def centos_unpack() -> None:
    docker = DOCKER
    centos = CENTOS
    repodir = REPODIR
    cname = "centos-unpack-" + centos  # container name
    image = "localhost:5000/centos-repo"
    sx___("{docker} rm --force {cname}".format(**locals()))
    sh___("{docker} run --name={cname} --detach {image}:{centos} sleep 9999".format(**locals()))
    sh___("{docker} cp {cname}:/srv/repo/7/os {repodir}/centos.{centos}/".format(**locals()))
    sh___("{docker} cp {cname}:/srv/repo/7/extras {repodir}/centos.{centos}/".format(**locals()))
    sh___("{docker} cp {cname}:/srv/repo/7/updates {repodir}/centos.{centos}/".format(**locals()))
    sh___("{docker} cp {cname}:/srv/repo/7/sclo {repodir}/centos.{centos}/".format(**locals()))
    sh___("{docker} rm --force {cname}".format(**locals()))
    sh___("du -sh {repodir}/centos.{centos}/.".format(**locals()))

def centos_clean() -> None:
    centos = CENTOS
    repodir = REPODIR
    for subdir in ["os", "extras", "updates", "sclo"]:
        sh___("rm -rf {repodir}/centos.{centos}/{subdir}".format(**locals()))

def centos_epelrepo() -> None:
    if CENTOS.startswith("7"):
        centos_epelrepo7()
    if CENTOS.startswith("8"):
        centos_epelrepo8()

def centos_epelrepo7() -> None:
    docker = DOCKER
    centos = CENTOS
    epel = major(centos)
    arch = ARCH
    cname = "epel-repo-" + epel  # container name
    sx___("{docker} rm --force {cname}".format(**locals()))
    sh___("{docker} run --name={cname} --detach centos:{centos} sleep 9999".format(**locals()))
    sh___("{docker} exec {cname} mkdir -p /srv/repo/epel".format(**locals()))
    sh___("{docker} exec {cname} yum install -y openssl".format(**locals()))
    sh___("{docker} cp scripts {cname}:/srv/scripts".format(**locals()))
    for script in os.listdir("scripts/."):
        sh___("{docker} exec {cname} chmod +x /srv/scripts/{script}".format(**locals()))
    #
    CMD = str(epelrepo7_CMD).replace("'", '"')
    PORT = str(epelrepo7_PORT)
    CMD2 = str(epelrepo7_http_CMD).replace("'", '"')
    PORT2 = str(epelrepo7_http_PORT)
    repo = IMAGESREPO
    yymm = datetime.date.today().strftime("%y%m")
    sh___("{docker} cp epel.{epel}/{epel} {cname}:/srv/repo/epel/".format(**locals()))
    sh___("{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' {cname} {repo}/epel-repo:{epel}.x.{yymm}".format(**locals()))
    sh___("{docker} rm --force {cname}".format(**locals()))
    sh___("{docker} run --name={cname} --detach {repo}/epel-repo:{epel}.x.{yymm} sleep 999".format(**locals()))
    sh___("{docker} commit -c 'CMD {CMD2}' -c 'EXPOSE {PORT2}' {cname} {repo}/epel-repo/http:{epel}.x.{yymm}".format(**locals()))
    sh___("{docker} rm --force {cname}".format(**locals()))

def centos_epelrepo8() -> None:
    docker = DOCKER
    centos = CENTOS
    epel = major(centos)
    arch = ARCH
    cname = "epel-repo-" + epel  # container name
    out, end = output2("./docker_mirror.py start centos:{centos} -a".format(**locals()))
    addhosts = out.strip()
    sx___("{docker} rm --force {cname}".format(**locals()))
    sh___("{docker} run --name={cname} {addhosts} --detach centos:{centos} sleep 9999".format(**locals()))
    sh___("{docker} exec {cname} mkdir -p /srv/repo/epel/{epel}".format(**locals()))
    sh___("{docker} exec {cname} yum install -y openssl".format(**locals()))
    sh___("{docker} cp scripts {cname}:/srv/scripts".format(**locals()))
    # for script in os.listdir("scripts/."):
    #    sh___("{docker} exec {cname} sed -i s:/usr/bin/python:/usr/libexec/platform-python: /srv/scripts/{script}".format(**locals()))
    #    sh___("{docker} exec {cname} chmod +x /srv/scripts/{script}".format(**locals()))
    base = "base"
    CMD = str(epelrepo8_CMD).replace("'", '"')
    PORT = str(epelrepo8_PORT)
    repo = IMAGESREPO
    yymm = datetime.date.today().strftime("%y%m")
    cmd = "{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' -m {base} {cname} {repo}/epel-repo/{base}:{epel}.x.{yymm}"
    sh___(cmd.format(**locals()))
    dists: Dict[str, List[str]] = {}
    dists["main"] = ["Everything"]
    dists["plus"] = ["Modular"]
    for dist in dists:
        sx___("{docker} rm --force {cname}".format(**locals()))
        sh___("{docker} run --name={cname} --detach {repo}/epel-repo/{base}:{epel}.x.{yymm} sleep 9999".format(**locals()))
        for subdir in dists[dist]:
            sh___("{docker} cp epel.{epel}/{epel}/{subdir} {cname}:/srv/repo/epel/{epel}/".format(**locals()))
            base = dist
        if base == dist:
            cmd = "{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' -m {base} {cname} {repo}/epel-repo/{base}:{epel}.x.{yymm}"
            sh___(cmd.format(**locals()))
    cmd = "{docker} tag {repo}/epel-repo/{base}:{epel}.x.{yymm} {repo}/epel-repo:{epel}.x.{yymm}"
    sh___(cmd.format(**locals()))
    sx___("{docker} rm --force {cname}".format(**locals()))
    sh___("{docker} rmi {repo}/epel-repo/base:{epel}.x.{yymm}".format(**locals()))
    #
    CMD = str(epelrepo8_http_CMD).replace("'", '"')
    PORT = str(epelrepo8_http_PORT)
    base = "http"
    sh___("{docker} run --name={cname} --detach {repo}/epel-repo:{epel}.x.{yymm} sleep 9999".format(**locals()))
    cmd = "{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' -m {base} {cname} {repo}/epel-repo/{base}:{epel}.x.{yymm}"
    sx___("{docker} rm --force {cname}".format(**locals()))

epelrepo7_PORT = 443
epelrepo7_CMD = ["/usr/bin/python", "/srv/scripts/mirrors.fedoraproject.org.py",
                 "--data", "/srv/repo/epel", "--ssl", "https://mirrors.fedoraproject.org"]
epelrepo7_http_PORT = 80
epelrepo7_http_CMD = ["/usr/bin/python", "/srv/scripts/mirrors.fedoraproject.org.py", "--data", "/srv/repo/epel"]

epelrepo8_PORT = 443
epelrepo8_CMD = ["/usr/libexec/platform-python", "/srv/scripts/mirrors.fedoraproject.org.py",
                 "--data", "/srv/repo/epel", "--ssl", "https://mirrors.fedoraproject.org"]
epelrepo8_http_PORT = 80
epelrepo8_http_CMD = ["/usr/libexec/platform-python", "/srv/scripts/mirrors.fedoraproject.org.py", "--data", "/srv/repo/epel"]

centosrepo7_CMD = ["/usr/bin/python", "/srv/scripts/mirrorlist.py", "--data", "/srv/repo"]
centosrepo7_PORT = 80
centosrepo8_CMD = ["/usr/libexec/platform-python", "/srv/scripts/mirrorlist.py", "--data", "/srv/repo"]
centosrepo8_PORT = 80
centosrepo8_http_CMD = ["/usr/libexec/platform-python", "/srv/scripts/mirrorlist.py", "--data", "/srv/repo"]
centosrepo8_http_PORT = 80

def centos_repo() -> None:
    if CENTOS.startswith("7"):
        centos_repo7()
    if CENTOS.startswith("8"):
        centos_repo8()

def centos_repo7() -> None:
    docker = DOCKER
    centos = CENTOS
    repodir = REPODIR
    centos_restore()
    centos_cleaner()
    cname = "centos-repo-" + centos  # container name
    sx___("{docker} rm --force {cname}".format(**locals()))
    sh___("{docker} run --name={cname} --detach centos:{centos} sleep 9999".format(**locals()))
    sh___("{docker} exec {cname} mkdir -p /srv/repo/7".format(**locals()))
    sh___("{docker} cp scripts {cname}:/srv/scripts".format(**locals()))
    base = "base"
    CMD = str(centosrepo7_CMD).replace("'", '"')
    PORT = centosrepo7_PORT
    repo = IMAGESREPO
    cmd = "{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' -m {base} {cname} {repo}/centos-repo/{base}:{centos}"
    sh___(cmd.format(**locals()))
    dists: Dict[str, List[str]] = OrderedDict()
    dists["main"] = ["os", "extras", "updates"]  # "extras" was not in 'main' for CentOS 6
    dists["sclo"] = ["sclo"]
    for dist in dists:
        sx___("{docker} rm --force {cname}".format(**locals()))
        sh___("{docker} run --name={cname} --detach {repo}/centos-repo/{base}:{centos} sleep 9999".format(**locals()))
        for subdir in dists[dist]:
            pooldir = "{repodir}/centos.{centos}/{subdir}".format(**locals())
            if path.isdir(pooldir):
                sh___("{docker} cp {pooldir} {cname}:/srv/repo/7/".format(**locals()))
                base = dist
        if base == dist:
            cmd = "{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' -m {base} {cname} {repo}/centos-repo/{base}:{centos}"
            sh___(cmd.format(**locals()))
    sh___("{docker} rm --force {cname}".format(**locals()))
    sh___("{docker} tag {repo}/centos-repo/{base}:{centos} {repo}/centos-repo:{centos}".format(**locals()))
    sh___("{docker} rmi {repo}/centos-repo/base:{centos}".format(**locals()))  # untag non-packages base
    centos_restore()

def centos_repo8() -> None:
    docker = DOCKER
    centos = CENTOS
    repodir = REPODIR
    centos_restore()
    centos_cleaner()
    cname = "centos-repo-" + centos  # container name
    sx___("{docker} rm --force {cname}".format(**locals()))
    sh___("{docker} run --name={cname} --detach centos:{centos} sleep 9999".format(**locals()))
    sh___("{docker} exec {cname} mkdir -p /srv/repo/8".format(**locals()))
    sh___("{docker} cp scripts {cname}:/srv/scripts".format(**locals()))
    base = "base"
    CMD = str(centosrepo8_CMD).replace("'", '"')
    PORT = centosrepo8_PORT
    repo = IMAGESREPO
    cmd = "{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' -m {base} {cname} {repo}/centos-repo/{base}:{centos}"
    sh___(cmd.format(**locals()))
    dists: Dict[str, List[str]] = OrderedDict()
    dists["main"] = ["BaseOS", "AppStream", "extras"]  # "extras" was not in 'main' for CentOS 6
    dists["plus"] = ["PowerTools", "centosplus"]
    dists["sclo"] = ["sclo"]
    for dist in dists:
        sx___("{docker} rm --force {cname}".format(**locals()))
        sh___("{docker} run --name={cname} --detach {repo}/centos-repo/{base}:{centos} sleep 9999".format(**locals()))
        for subdir in dists[dist]:
            pooldir = "{repodir}/centos.{centos}/{subdir}".format(**locals())
            if path.isdir(pooldir):
                sh___("{docker} cp {pooldir} {cname}:/srv/repo/8/".format(**locals()))
                base = dist
        if base == dist:
            cmd = "{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' -m {base} {cname} {repo}/centos-repo/{base}:{centos}"
            sh___(cmd.format(**locals()))
    sh___("{docker} rm --force {cname}".format(**locals()))
    sh___("{docker} tag {repo}/centos-repo/{base}:{centos} {repo}/centos-repo:{centos}".format(**locals()))
    sh___("{docker} rmi {repo}/centos-repo/base:{centos}".format(**locals()))  # untag non-packages base
    centos_restore()

def centos_tags() -> None:
    docker = DOCKER
    centos = CENTOS
    repo = IMAGESREPO
    name = "centos-repo"
    ver2 = re.sub("[.]\d+$", "", centos)
    if ver2 != centos:
        sh___("{docker} tag {repo}/{name}:{centos} {repo}/{name}:{ver2}".format(**locals()))
    ver1 = re.sub("[.]\d+$", "", ver2)
    if ver1 != ver2:
        sh___("{docker} tag {repo}/{name}:{centos} {repo}/{name}:{ver1}".format(**locals()))
        sh___("{docker} tag {repo}/{name}:{centos} {repo}/{name}{ver1}:{centos}".format(**locals()))
        sh___("{docker} tag {repo}/{name}:{centos} {repo}/{name}{ver1}:latest".format(**locals()))

def centos_cleaner() -> None:
    centos = CENTOS
    repodir = REPODIR
    arch = "x86_64"
    for subdir in ["updates", "extras"]:
        orig = "{repodir}/centos.{centos}/{subdir}/{arch}/drpms"
        save = "{repodir}/centos.{centos}/{subdir}.{arch}.drpms"
        if path.isdir(orig):
            shutil.move(orig, save)

def centos_restore() -> None:
    centos = CENTOS
    repodir = REPODIR
    arch = "x86_64"
    for subdir in ["updates", "extras"]:
        orig = "{repodir}/centos.{centos}/{subdir}/{arch}/drpms"
        save = "{repodir}/centos.{centos}/{subdir}.{arch}.drpms"
        if path.isdir(save):
            shutil.move(save, orig)

def centos_test() -> None:
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
    centos = CENTOS
    repodir = REPODIR
    cname = "centos-check-" + centos  # container name
    sx___("{docker} rm --force {cname}".format(**locals()))
    sh___("{docker} run --name={cname} --detach centos:{centos} sleep 9999".format(**locals()))
    centosdir = "{repodir}/centos.{centos}".format(**locals())
    out, end = output2("{docker} exec {cname} rpm -qa".format(**locals()))
    for f in out.split("\n"):
        found = path_find(centosdir, f + ".rpm")
        if found:
            print("OK {f}.rpm        {found}".format(**locals()))
    for f in out.split("\n"):
        found = path_find(centosdir, f + ".rpm")
        if not found:
            print("?? {f}.rpm".format(**locals()))
    sh___("{docker} rm --force {cname}".format(**locals()))

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
    global CENTOS
    if centos in OS:
        CENTOS = OS[centos]
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
