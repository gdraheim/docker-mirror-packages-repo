#! /usr/bin/python3
""" sync packages repo to disk and make docker mirror images from it.
    Try to run 'sync' followed be 'repo'. If a command starts with a
    number then it changes the version to be handled. A usual command
    would be 'mirror.py 7.7 sync repo -v'. If no argument is given
    then 'make' the last version = 'sync pull repo test check tags'."""
import os
import os.path as path
import sys
import re
import subprocess
import logging
logg = logging.getLogger("MIRROR")

if sys.version[0] == '3':
    basestring = str
    xrange = range

IMAGESREPO = os.environ.get("IMAGESREPO", "localhost:5000/mirror-packages")
REPODATADIR = os.environ.get("REPODATADIR", "")

CENTOSDATADIRS= [ REPODATADIR,
    "/srv/docker-mirror-packages",
    "/data/docker-mirror-packages",
    "/data/docker-centos-repo-mirror",
    "/dock/docker-mirror-packages"]

CENTOS = "8.0.1905"
X8CENTOS = "8.3.2011"
# CENTOS = "8.3.2011"
# CENTOS = "8.2.2004"
# CENTOS = "8.1.1911"
# CENTOS = "8.0.1905"
X7CENTOS = "7.9.2009"
# CENTOS = "7.9.2009"
# CENTOS = "7.8.2003"
# CENTOS = "7.7.1908"
# CENTOS = "7.6.1810"
# CENTOS = "7.5.1804"
# CENTOS = "7.4.1708"
# CENTOS = "7.3.1611"
# CENTOS = "7.2.1511"
# CENTOS = "7.1.1503"
# CENTOS = "7.0.1406"

DOCKER = "docker"
RSYNC = "rsync"

CENTOS_MIRROR = "rsync://rsync.hrz.tu-chemnitz.de/ftp/pub/linux/centos"
# "http://ftp.tu-chemnitz.de/pub/linux/centos/"


#############################################################################

def centos_make():
    centos_sync()
    centos_pull()
    centos_repo()
    centos_test()
    centos_check()
    centos_tags()

def centos_pull():
    docker = DOCKER
    centos = CENTOS
    if centos == X7CENTOS:
        sh___("{docker} pull centos:7".format(**locals()))
        sh___("{docker} tag  centos:7 centos:{centos}".format(**locals()))
    if centos == X8CENTOS:
        sh___("{docker} pull centos:8".format(**locals()))
        sh___("{docker} tag  centos:8 centos:{centos}".format(**locals()))

def centos_sync():
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

def centos_dir():
    centos = CENTOS
    dirname = "centos.{centos}".format(**locals())
    if path.isdir(dirname):
        if path.islink(dirname):
            os.unlink(dirname)
        else:
            shutil.rmtree(dirname) # local dir
    # we want to put the mirror data on an external disk
    for data in CENTOSDATADIRS:
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

CENTOS_XXX=" ".join([
   "--exclude ppc64le",
   "--exclude aarch64",
   "--exclude EFI",
   "--exclude images",
   "--exclude isolinux",
   "--exclude '*.iso'",
   ])

def sync_subdir(subdir):
    rsync = RSYNC
    mirror = CENTOS_MIRROR 
    centos = CENTOS 
    excludes = CENTOS_XXX
    sh____("{rsync} -rv {mirror}/{centos}/{subdir}   centos.{centos}/ {excludes}".format(**locals()))

def centos_sync_AppStream():   sync_subdir("AppStream")
def centos_sync_BaseOS():      sync_subdir("BaseOS")
def centos_sync_os():          sync_subdir("os")
def centos_sync_extras():      sync_subdir("extras")
def centos_sync_PowerTools():  sync_subdir("PowerTools")
def centos_sync_centosplus():  sync_subdir("centosplus")
def centos_sync_updates():     sync_subdir("updates")
def centos_sync_sclo():        sync_subdir("sclo")

def centos_unpack():
    docker = DOCKER
    centos = CENTOS
    cname = "centos-unpack-"+centos # container name
    image = "localhost:5000/centos-repo"
    sx___("{docker} rm --force {cname}".format(**locals()))
    sh___("{docker} run --name={cname} --detach {image}:{centos} sleep 9999".format(**locals()))
    sh___("{docker} cp {cname}:/srv/repo/7/os centos.{centos}/".format(**locals()))
    sh___("{docker} cp {cname}:/srv/repo/7/extras centos.{centos}/".format(**locals()))
    sh___("{docker} cp {cname}:/srv/repo/7/updates centos.{centos}/".format(**locals()))
    sh___("{docker} cp {cname}:/srv/repo/7/sclo centos.{centos}/".format(**locals()))
    sh___("{docker} rm --force {cname}".format(**locals()))
    sh___("du -sh centos.{centos}/.".format(**locals()))

def centos_clean():
    centos = CENTOS
    for subdir in ["os", "extras", "updates", "sclo"]:
        sh___("rm -rf centos.{centos}/{subdir}".format(**locals()))

centosrepo7_CMD = ["python","/srv/scripts/mirrorlist.py","--data","/srv/repo"]
centosrepo7_PORT = 80
centosrepo8_CMD = ["python","/srv/scripts/mirrorlist.py","--data","/srv/repo"]
centosrepo8_PORT = 80

def centos_repo():
   if CENTOS.startswith("7"):
       centos_repo7()
   if CENTOS.startswith("8"):
       centos_repo8()

def centos_repo7():
    docker = DOCKER
    centos = CENTOS
    centos_restore()
    centos_cleaner()
    cname = "centos-repo-"+centos # container name
    sx___("{docker} rm --force {cname}".format(**locals()))
    sh___("{docker} run --name={cname} --detach centos:{centos} sleep 9999".format(**locals()))
    sh___("{docker} exec {cname} mkdir -p /srv/repo/7".format(**locals()))
    sh___("{docker} cp scripts {cname}:/srv/scripts".format(**locals()))
    for subdir in ["os", "extras", "updates", "sclo"]:
        sh___("{docker} cp centos.{centos}/{subdir} $@:/srv/repo/7/".format(**locals()))
    cmd = centos7_CMD
    port = centos7_PORT
    repo = IMAGESREPO
    sh___("{docker} commit -c 'CMD {cmd}' -c 'EXPOSE {port}' {cname} {repo}/centos-repo:{centos}".format(**locals()))
    sh___("{docker} rm --force {cname}".format(**locals()))
    centos_restore()

def centos_repo8():
    docker = DOCKER
    centos = CENTOS
    centos_restore()
    centos_cleaner()
    cname = "centos-repo-"+centos # container name
    sx___("{docker} rm --force {cname}".format(**locals()))
    sh___("{docker} run --name={cname} --detach centos:{centos} sleep 9999".format(**locals()))
    sh___("{docker} exec {cname} mkdir -p /srv/repo/7".format(**locals()))
    sh___("{docker} cp scripts {cname}:/srv/scripts".format(**locals()))
    for subdir in ["BaseOS", "AppStream", "extras", "PowerTools", "centosplus"]:
        sh___("{docker} cp centos.{centos}/{subdir} $@:/srv/repo/8/".format(**locals()))
    sh___("{docker} exec yum install -y python2".format(**locals()))
    sh___("{docker} exec ln -sv /usr/bin/python2 /usr/bin/python".format(**locals()))
    cmd = centos8_CMD
    port = centos8_PORT
    repo = IMAGESREPO
    sh___("{docker} commit -c 'CMD {cmd}' -c 'EXPOSE {port}' {cname} {repo}/centos-repo:{centos}".format(**locals()))
    sh___("{docker} rm --force {cname}".format(**locals()))
    centos_restore()

def centos_tags(): 
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

def centos_cleaner():
   centos = CENTOS
   arch = "x86_64"
   for subdir in ["updates", "extras"]:
       orig = "centos.{centos}/{subdir}/{arch}/drpms"
       save = "centos.{centos}/{subdir}.{arch}.drpms"
       if path.isdir(orig):
           os.move(orig, save)

def centos_restore():
   centos = CENTOS
   arch = "x86_64"
   for subdir in ["updates", "extras"]:
       orig = "centos.{centos}/{subdir}/{arch}/drpms"
       save = "centos.{centos}/{subdir}.{arch}.drpms"
       if path.isdir(save):
           os.move(save, orig)

def centos_test():
    centos = CENTOS
    logg.error("not implemented")
    # sed -e "s|centos:centos7|centos:$(CENTOS)|" -e "s|centos-repo:7|centos-repo:$(CENTOS)|" \
    #    centos-compose.yml > centos-compose.tmp
    # - docker-compose -p $@ -f centos-compose.tmp down
    # docker-compose -p $@ -f centos-compose.tmp up -d
    # docker exec centosworks_host_1 yum install -y firefox
    # docker-compose -p $@ -f centos-compose.tmp down

def centos_check():
    docker = DOCKER
    centos = CENTOS
    cname = "centos-check-"+centos # container name
    sx___("{docker} rm --force {cname}".format(**locals()))
    sh___("{docker} run --name={cname} --detach centos:{centos} sleep 9999".format(**locals()))
    centosdir = "centos.{centos}".format(**locals())
    out, end = output2("{docker} exec {cname} rpm -qa".format(**locals()))
    for f in out.split("\n"):
        found = file_find(centosdir, f+".rpm")
        if found:
            print("OK {f}.rpm        {found}".format(**locals()))
    for f in out.split("\n"):
        found = file_find(centosdir, f+".rpm")
        if not found:
            print("?? {f}.rpm".format(**locals()))
    sh___("{docker} rm --force {cname}".format(**locals()))

#############################################################################

def decodes(text):
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
def sh____(cmd, shell=True):
    if isinstance(cmd, basestring):
        logg.info(": %s", cmd)
    else:    
        logg.info(": %s", " ".join(["'%s'" % item for item in cmd]))
    return subprocess.check_call(cmd, shell=shell)
def sx____(cmd, shell=True):
    if isinstance(cmd, basestring):
        logg.info(": %s", cmd)
    else:    
        logg.info(": %s", " ".join(["'%s'" % item for item in cmd]))
    return subprocess.call(cmd, shell=shell)
def output(cmd, shell=True):
    if isinstance(cmd, basestring):
        logg.info(": %s", cmd)
    else:    
        logg.info(": %s", " ".join(["'%s'" % item for item in cmd]))
    run = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE)
    out, err = run.communicate()
    return out
def output2(cmd, shell=True):
    if isinstance(cmd, basestring):
        logg.info(": %s", cmd)
    else:    
        logg.info(": %s", " ".join(["'%s'" % item for item in cmd]))
    run = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE)
    out, err = run.communicate()
    return decodes(out), run.returncode
def output3(cmd, shell=True):
    if isinstance(cmd, basestring):
        logg.info(": %s", cmd)
    else:    
        logg.info(": %s", " ".join(["'%s'" % item for item in cmd]))
    run = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = run.communicate()
    return decodes(out), decodes(err), run.returncode

#############################################################################

def commands():
    cmds = []
    for name in sorted(globals()):
        if name.startswith("centos_"):
            func = globals()[name]
            if callable(func):
                cmd = name.replace("centos_", "")
                cmds += [ cmd ]
    return "|".join(cmds)

if __name__ == "__main__":
    from optparse import OptionParser
    _o = OptionParser("%%prog [-options] [%s]" % commands(),
       epilog=re.sub("\\s+", " ", __doc__).strip())
    _o.add_option("-v","--verbose", action="count", default=0,
       help="increase logging level [%default]")
    _o.add_option("-D","--docker", metavar="EXE", default=DOCKER,
       help="use other docker exe or podman [%default]")
    _o.add_option("-V","--version", metavar="NUM", default=CENTOS,
       help="use other centos version [%default]")
    opt, args = _o.parse_args()
    logging.basicConfig(level = logging.WARNING - opt.verbose * 10)
    #
    DOCKER = opt.docker
    CENTOS = opt.version
    #
    if not args: args = [ "make" ]
    for arg in args:
        if arg[0] in "123456789":
           CENTOS = arg
           continue
        funcname = "centos_"+arg.replace("-", "_")
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
