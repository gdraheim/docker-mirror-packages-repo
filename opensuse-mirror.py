#! /usr/bin/python3
""" sync packages repo to disk and make docker mirror images from it.
    Try to run 'sync' followed be 'repo'. If a command starts with a
    number then it changes the version to be handled. A usual command
    would be 'mirror.py 7.7 sync repo -v'. If no argument is given
    then 'make' the last version = 'sync pull repo test check tags'."""

__copyright__ = "(C) 2020 Guido Draheim"
__contact__ = "https://github.com/gdraheim/docker-mirror-packages-repo"
__license__ = "CC0 Creative Commons Zero (Public Domain)"
__version__ = "1.6.2495"

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
XXLEAP = ["15.2"]
LEAP: str ="15.2"

RSYNC_SUSE1="rsync://suse.uni-leipzig.de/opensuse-full/opensuse"
RSYNC_SUSE2="rsync://ftp.tu-chemnitz.de/pub/linux/opensuse"
RSYNC_SUSE="rsync://mirror.cs.upb.de/opensuse"

DOCKER = "docker"

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

def opensuse_dir() -> None:
    leap = LEAP
    dirname = "opensuse.{leap}".format(**locals())
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

def opensuse_sync_1() -> None:
    leap = LEAP
    mirror = RSYNC_SUSE
    excludes = """  --filter="exclude boot" --filter="exclude EFI"  """
    excludes += """ --size-only --filter="exclude *.src.rpm" """
    leaprepo = "opensuse.{leap}/distribution/leap/{leap}/repo".format(**locals())
    if not path.isdir(leaprepo): os.makedirs(leaprepo)
    sh___("{rsync} -rv {mirror}/distribution/leap/{leap}/repo/oss {leaprepo}/ {excludes}".format(**locals()))
	   
def opensuse_sync_2() -> None:
    leap = LEAP
    mirror = RSYNC_SUSE
    excludes = """  --filter="exclude boot" --filter="exclude EFI"  """
    excludes += """  --filter="exclude x86_64" --filter="exclude noarch"  """
    excludes += """ --size-only --filter="exclude *.src.rpm" """
    leaprepo = "opensuse.{leap}/distribution/leap/{leap}/repo".format(**locals())
    if not path.isdir(leaprepo): os.makedirs(leaprepo)
    sh___("{rsync} -rv {mirror}/distribution/leap/{leap}/repo/non-oss {leaprepo}/ {excludes}".format(**locals()))

def opensuse_sync_3() -> None:
    leap = LEAP
    mirror = RSYNC_SUSE
    excludes = """  --filter="exclude boot" --filter="exclude *.drpm"  """
    excludes += """ --size-only --filter="exclude *.src.rpm" """
    leaprepo = "opensuse.{leap}/update/leap/{leap}/repo".format(**locals())
    if not path.isdir(leaprepo): os.makedirs(leaprepo)
    sh___("{rsync} -rv {mirror}/update/leap/{leap}/repo/oss {leaprepo}/ {excludes}".format(**locals()))

def opensuse_sync_4() -> None:
    leap = LEAP
    mirror = RSYNC_SUSE
    excludes = """  --filter="exclude boot" --filter="exclude EFI"  """
    excludes += """  --filter="exclude x86_64" --filter="exclude noarch"  """
    excludes += """  --filter="exclude strc" --filter="exclude nosrc"  """
    excludes += """ --size-only --filter="exclude *.src.rpm" """
    leaprepo = "opensuse.{leap}/update/leap/{leap}/repo".format(**locals())
    if not path.isdir(leaprepo): os.makedirs(leaprepo)
    sh___("{rsync} -rv {mirror}/update/leap/{leap}/repo/non-oss {leaprepo}/ {excludes}".format(**locals()))

# /etc/zypp/repos.d/oss-update.repo:baseurl=http://download.opensuse.org/update/42.2/
# /etc/zypp/repos.d/update-non-oss.repo:baseurl=http://download.opensuse.org/update/leap/42.2/non-oss/
# /etc/zypp/repos.d/oss.repo:baseurl=http://download.opensuse.org/distribution/leap/42.2/repo/oss/
# /etc/zypp/repos.d/non-oss.repo:baseurl=http://download.opensuse.org/distribution/leap/42.2/repo/non-oss/

opensuserepo_CMD = ["python","/srv/scripts/filelist.py","--data","/srv/repo"]
opensuserepo_PORT = "80"
def opensuse_repo() -> None:
     docker = DOCKER
     leap = LEAP
     cname = "opensuse-repo-" + leap
     image = BASE[LEAP]
     imagesrepo = IMAGESREPO
     sx___("{docker} rm --force {cname}".format(**locals()))
     sh___("{docker} run --name={cname} --detach {image}:{leap} sleep 9999".format(**locals()))
     sh___("{docker} exec {cname} mkdir -p /srv/repo/".format(**locals()))
     sh___("{docker} cp scripts {cname}:/srv/scripts".format(**locals()))
     sh___("{docker} cp opensuse.{leap}/distribution {cname}:/srv/repo/".format(**locals()))
     sh___("{docker} cp opensuse.{leap}/update       {cname}:/srv/repo/".format(**locals()))
     # sh___("{docker} exec {cname} rm -r /srv/repo/update/{leap}".format(**locals()))
     sh___("{docker} exec {cname} ln -s /srv/repo/update/leap/{leap}/oss /srv/repo/update/{leap}".format(**locals()))
     sh___("{docker} exec {cname} zypper ar file:///srv/repo/distribution/leap/{leap}/repo/oss oss-repo".format(**locals()))
     sh___("{docker} exec {cname} zypper --no-remote install -y python createrepo".format(**locals()))
     if leap in XXLEAP:   
        sh___(""" {docker} exec {cname} bash -c "cd /srv/repo/update/leap/$(LEAP)/oss && createrepo ." """.format(**locals()))
     CMD = opensuserepo_CMD ; PORT = opensuserepo_PORT
     sh___("{docker} commit -c 'CMD {CMD}' -c 'EXPOSE {PORT}' {cname} {imagesrepo}/opensuse-repo:{leap}".format(**locals()))
     sh___("{docker} rm --force {cname}".format(**locals()))

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

def commands() -> str:
    cmds: List[str] = []
    for name in sorted(globals()):
        if name.startswith("opensuse_"):
            if "_sync_" in name: continue
            func = globals()[name]
            if callable(func):
                cmd = name.replace("opensuse_", "")
                cmds += [cmd]
    return "|".join(cmds)

def LEAP_set(leap: str) -> str:
    global LEAP
    if len(leap) <= 2:
        LEAP = max([os for os in BASE if os.startswith(leap) and not os.startswith("42") ])
        return LEAP
    if leap not in BASE.values():
        logg.warning("%s is not a known os version", leap)
    LEAP = leap
    return LEAP

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
    opt, args = _o.parse_args()
    logging.basicConfig(level=logging.WARNING - opt.verbose * 10)
    #
    DOCKER = opt.docker
    LEAP_set(opt.ver)
    #
    if not args: args = ["make"]
    for arg in args:
        if arg[0] in "123456789":
            LEAP_set(arg)
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
