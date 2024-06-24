#! /usr/bin/python3
from __future__ import print_function
from __future__ import division

""" 
   DockerDir will read a Dockerfile looking for ADD elements. It 
   creates a new subdirectory (under the --topdir) where the
   directories are copied and the dockerfile is copied as well.
   Then dockerscripts are created inside the subdir.

   This creates a self-contained docker subproject that only
   relies on the data and the dockerfile. No docker-python or
   anything else is needed. Such a docker subproject can be
   zipped up and it is still valid in a Windows boot2docker
   environment (where you don't have docker-python).

   So basically the devel environment may contain a lot of
   optional elements where dockerdir.py copies only the
   relevant elements into a docker subproject that can be
   be executed with any other docker environment. With the
   help of the dockerscripts it is easy to run even for those
   people who don't have a clue about the docker commandline.

   The additional dockerscripts include a 'build.sh' script
   and possibly a 'run.sh' script to run the resulting image.
   These scripts add some functionality that is missing from 
   the normal 'docker build' command - namely the resulting 
   image can be tagged with 

     ENV _commit localhost:5000/build:result
     ENV _tag localhost:5000/build:latest

   You can easily EXPOSE ports but these need to be bound to local
   ports upon 'docker run'. It can be preconfigured with
  
     ENV _run  -p 8080:80 -p 8000:8000
     ENV _run2 -p 8082:80 -p 8002:8000
    
   Note that the first port is the external one that you can access
   and the second port is the one inside the docker box. If you 
   provide "_run2" then a 'run2.sh' script is generated.
 """

__copyright__ = """ (c) 2015-2022 Guido Draheim """
__version__ = "1.7.6261"
import sys
import re
import os
from os import path
import subprocess
import shutil
from optparse import OptionParser
import logging
logg = logging.getLogger("dockerdir")
HINT = (logging.INFO + logging.DEBUG) // 2

_o = OptionParser("%prog [options] dockerfile [targetdir]")
_o.add_option("-t", "--topdir", metavar="DIR", default="docker.tmp",
              help="target top directory for docker subdirs (%default)")
_o.add_option("-b", "--build", action="store_true", default=False,
              help="run the build.sh after creating the subproject (%default)")
_o.add_option("-v", "--verbose", action="count", default=0,
              help="increase logging level (%default)")

docker_mirror = "docker_mirror.py"

_commit = "_commit"
_build = "_build"

_docker_mirror = "docker_mirror.py"

class DockerScripts:
    def __init__(self, dockerdir=None):
        self.dockerdir = dockerdir
    def run(self, targetfile):
        builddir = os.path.dirname(targetfile)
        logg.info("running %s: %s", builddir, "build.sh")
        done = subprocess.run(["sh", "build.sh", "--rm=true"], cwd=builddir)
        return done.returncode
    def create(self, dockerfile=None):
        # configure .......................................................
        dockerdir = self.dockerdir or ""
        if not dockerfile:
            dockerfile = path.join(dockerdir, "Dockerfile")
        else:
            dockerdir = path.dirname(dockerfile)
        ENV = {}
        with open(dockerfile) as f:
            for line in f:
                m = re.match(r"(?:ENV|env)\s+([_\w]+)\s+(.*)", line)
                if m:
                    ENV[m.group(1)] = m.group(2).strip()
        # docker-mirror-package-repo .....................................
        mirror_start = ""
        mirror_stop = ""
        docker_mirror = _docker_mirror
        if path.exists(path.join(dockerdir, docker_mirror)):
            dockerfilename = path.basename(dockerfile)
            mirror_start = "./{docker_mirror} -f {dockerfilename} -a start".format(**locals())
            mirror_stop = "./{docker_mirror} -f {dockerfilename} -a stop".format(**locals())
        # generate ........................................................
        _taglist = [tag for tag in ENV if tag.startswith("_tag")]
        if _commit in ENV:
            commit = ENV[_commit]
            optbuild = ""
            if _build in ENV:
                optbuild = ENV[_build]
            script = ["#! /bin/sh", "set -ex"]
            if mirror_start:
                script.append('addhosts=`{mirror_start}`'.format(**locals()))
            script.append('docker build $addhosts {optbuild} -t {commit} "$@" `dirname $0`'.format(**locals()))
            if mirror_stop:
                script.append('{mirror_stop}'.format(**locals()))
            newtags = ""
            for _tag in _taglist:
                tag = ENV[_tag]
                if "{}" not in tag:
                    tag = "{}" + tag
                opttag, newtag = tag.split("{}", 1)
                # script.append("docker tag -f {opttag} {commit} {newtag}".format(**locals()))
                script.append("docker tag {opttag} {commit} {newtag}".format(**locals()))
                newtags += " " + newtag
            if newtags:
                script.append("echo 'done {commit} => {newtags}'".format(**locals()))
            else:
                script.append("echo 'done {commit}'".format(**locals()))
        else:
            optbuild = ""
            if _build in ENV:
                optbuild = ENV[_build]
            tagbuild = ""
            if "_tag" in ENV:
                tagbuild = "-t " + ENV["_tag"]
            script = ["#! /bin/sh", "set -ex"]
            if mirror_start:
                script.append('addhosts=`{mirror_start}`'.format(**locals()))
            script.append('docker build $addhosts {optbuild} {tagbuild} "$@" `dirname $0`'.format(**locals()))
            if mirror_stop:
                script.append('{mirror_stop}'.format(**locals()))
            script.append("echo 'done {tagbuild}'".format(**locals()))
        runscripts = {}
        _runlist = [tag for tag in ENV if tag.startswith("_run")]
        for _run in _runlist:
            runopt = ENV[_run]
            target = ""
            if "_tag" in ENV: target = ENV["_tag"]
            if _commit in ENV: target = ENV[_commit]
            _tag = _run.replace("_run", "_tag")
            if _tag in ENV: target = ENV[_tag]
            if not target:
                logg.warning("found _run but no target image name")
                continue
            runscript = ["#! /bin/sh", "set -ex"]
            runscript.append('docker run {runopt} "$@" {target}'.format(**locals()))
            scriptname = _run[1:] + ".sh"
            runscripts[scriptname] = runscript
        if runscripts and script:
            scriptname = sorted(runscripts.keys())[0]  # first script
            script.append('echo "ready to `dirname $0`/{scriptname}"'.format(**locals()))
        # output ...................................................
        if script:
            scriptpath = path.join(dockerdir, "build.sh")
            scripttext = "\n".join(script) + "\n"
            with open(scriptpath, "w") as f:
                f.write(scripttext)
            logg.info("=== written %s", scriptpath)
            logg.log(HINT, "\n%s", scripttext)
        os.chmod(scriptpath, 0o775)
        for scriptname, runscript in runscripts.items():
            scriptpath = path.join(dockerdir, scriptname)
            scripttext = "\n".join(runscript) + "\n"
            with open(scriptpath, "w") as f:
                f.write(scripttext)
            logg.info("=== written %s", scriptpath)
            logg.log(HINT, "\n%s", scripttext)
            os.chmod(scriptpath, 0o775)

class DockerDir:
    def __init__(self, topdir=None):
        self.topdir = topdir or "."
    def run(self, dockerfile=None, targetdir=None):
        targetfile = self.create(dockerfile)
        return DockerScripts().run(targetfile)
    def create(self, dockerfile=None, targetdir=None):
        targetdir = targetdir or self.topdir
        dockerfile = dockerfile or "Dockerfile"
        errors = 0
        dockerfile_dir = path.dirname(dockerfile)
        dockerfile_name = path.basename(dockerfile)
        if dockerfile_name == "Dockerfile":
            dockername = path.dirname(dockerfile_dir)
        else:
            dockername = path.splitext(dockerfile_name)[0]
        dockerdir = path.join(targetdir, dockername)
        if path.isdir(dockerdir):
            shutil.rmtree(dockerdir)
        if not path.isdir(dockerdir):
            os.makedirs(dockerdir)
        targetfile = path.join(dockerdir, "Dockerfile")
        logg.info("cp %s %s", dockerfile, targetfile)
        shutil.copyfile(dockerfile, targetfile)
        #
        optional = [docker_mirror]
        sources = []
        for line in open(dockerfile):
            add = re.match(r"(?:ADD|add)\s+(\w\S+)\s+(.*)", line)
            if add:
                mount = add.group(1)
                sources.append(mount)
        for mount in optional + sources:
            # check in the usual places for the source data
            found = None
            for srcdir in [dockerfile_dir, "files", "Software", "../../Software"]:
                srctree = path.join(srcdir, mount)
                if path.isfile(srctree):
                    newtree = path.join(dockerdir, mount)
                    logg.info("cp -r %s %s", srctree, newtree)
                    shutil.copy(srctree, newtree)
                    found = srctree
                elif path.exists(srctree):
                    newtree = path.join(dockerdir, mount)
                    logg.info("cp -r %s %s", srctree, newtree)
                    shutil.copytree(srctree, newtree)
                    found = srctree
                if found:
                    break
            if found:
                logg.debug("did find %s", found)
            elif mount in optional:
                logg.info(" did not find src %s", mount)
            else:
                logg.error("did not find ADD %s", mount)
                errors += 1
        assert not errors
        return targetfile

def run(dockerfile, targetdir, build=False):
    dockerdir = DockerDir(targetdir)
    try:
        targetfile = dockerdir.create(dockerfile, targetdir)
    except Exception as e:
        logg.error("dockerdir create failed: %s", e)
        return 1
    dockerscripts = DockerScripts()
    dockerscripts.create(targetfile)
    if build:
        builddir = os.path.dirname(targetfile)
        logg.info("running %s: %s", builddir, "build.sh")
        done = subprocess.run(["sh", "build.sh", "--rm=true"], cwd=builddir)
        return done.returncode
    return 0

if __name__ == "__main__":
    opt, args = _o.parse_args()
    logging.basicConfig(level=max(0, logging.WARNING - 5 * opt.verbose))
    logg.setLevel(level=max(0, logging.WARNING - 5 - 5 * opt.verbose))
    logging.addLevelName(HINT, "HINT")
    dockerfile = None
    targetdir = None
    if len(args) > 0: dockerfile = args[0]
    if len(args) > 1: targetdir = args[1]
    sys.exit(run(dockerfile, targetdir or opt.topdir, opt.build))
