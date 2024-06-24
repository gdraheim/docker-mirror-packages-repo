[![Style Check](https://github.com/gdraheim/docker-mirror-packages-repo/actions/workflows/stylecheck.yml/badge.svg?event=push)](https://github.com/gdraheim/docker-mirror-packages-repo/actions/workflows/stylecheck.yml)
[![Type Check](https://github.com/gdraheim/docker-mirror-packages-repo/actions/workflows/typecheck.yml/badge.svg?event=push)](https://github.com/gdraheim/docker-mirror-packages-repo/actions/workflows/typecheck.yml)
[![PyPI version](https://badge.fury.io/py/docker-mirror-packages-repo.svg)](https://pypi.org/project/docker-mirror-packages-repo/)

# docker mirror packages repo

Allows to simulate upstream centos / ubuntu / opensuse
package repository servers by using a docker container
which contains a local package mirror.

The scripts in this project allow to build a local package
mirror using rsync. When ready the rpm/deb packages get
copied into a docker image which has a small web script
that mimics the mirrorlist function of the original
upstream package repository servers.

There is a helper script docker_mirror which can start
a mirror docker image as container. The --add-hosts
option prints the line for "docker run" so that calls
to the original upstream package server get diverted
to the ip address of the locally running docker container.

Effectively all `"yum install"` or `"zypper install"` or
`"apt-get install"` commands run locally in the docker 
network. No internet access required. Without changing 
repo files. Without special proxy host setups. This is
faster, allows for reproducible install tests, and it
can be used in a disconnected environment.

The scripting has also been used with docker-compose
and ansible deployment setups. Over the years a number
of package repos have been tested - starting with
distros from 2016 until today. Even when the upstream
package repositories get disabled, for being out of
support, the local docker mirrors continue to work.

----

Tested repos are

| docker image                                  | size
| --------------------------------------------- | ----
| mirror-packages/epel-repo:9.x.2406	| 44.9GB
| mirror-packages/epel-repo:7.x.2012	| 49GB
| mirror-packages/ubuntu-repo/universe:24.04	| 134GB
| mirror-packages/ubuntu-repo/restricted:24.04	| 30.6GB
| mirror-packages/ubuntu-repo/main:24.04	| 27GB
| mirror-packages/ubuntu-repo/universe:22.04	| 178GB
| mirror-packages/ubuntu-repo/restricted:22.04	| 35GB
| mirror-packages/ubuntu-repo/main:22.04	| 29.2GB
| mirror-packages/ubuntu-repo/universe:20.04	| 198GB
| mirror-packages/ubuntu-repo/restricted:20.04	| 111GB
| mirror-packages/ubuntu-repo/main:20.04	| 107GB
| mirror-packages/ubuntu-repo/restricted:18.04	| 26GB
| mirror-packages/ubuntu-repo/main:18.04	| 25.8GB
| mirror-packages/ubuntu-repo/universe:16.04	| 186GB
| mirror-packages/ubuntu-repo/restricted:16.04	| 45.4GB
| mirror-packages/ubuntu-repo/main:16.04	| 44.4GB
| mirror-packages/almalinux-repo/plus:9.4	| 46.4GB
| mirror-packages/almalinux-repo/main:9.4	| 23.4GB
| mirror-packages/almalinux-repo/plus:9.3	| 59.6GB
| mirror-packages/almalinux-repo/main:9.3	| 26.1GB
| mirror-packages/almalinux-repo/plus:9.1	| 23.1GB
| mirror-packages/almalinux-repo/main:9.1	| 22.4GB
| mirror-packages/centos-repo/sclo:7.9.2009	| 22.4GB
| mirror-packages/centos-repo7:7.9.2009	| 22.4GB
| mirror-packages/centos-repo/main:7.9.2009	| 15.1GB
| mirror-packages/opensuse-repo/update:15.6	| 210GB
| mirror-packages/opensuse-repo/main:15.6	| 205GB
| mirror-packages/opensuse-repo/update:15.5	| 112GB
| mirror-packages/opensuse-repo/main:15.5	| 70.8GB
| mirror-packages/opensuse-repo/update:15.4	| 143GB
| mirror-packages/opensuse-repo/main:15.4	| 59.8GB
| mirror-packages/opensuse-repo/update:15.2	| 118GB

Remember that the internet package repos contain updates for the last
distribution release, so they do grow in size over time. As such the
image sizes (as shown above) may differ after each sync.

## BACKGROUND

Consider that you have a Dockerfile with

    FROM centos:7.5.1804
    RUN yum install -y httpd httpd-tools

This will reach out to the internet downloading 20+ rpm packages.

It would be better to have a local mirror of the default yum 
repositories for centos. When using a docker environment you 
can reassign the systems' package repo URL to a local container 
that can answer the yum download requests.

That mode is not only faster but you can also commit the yum repo
mirror in your binary repository. New updates on the external 
internet yum repository will not suddenly change rebuild results. 
This has been extensively used in testing docker-related tools 
where the result image was dropped right away after testing it.

## CENTOS

Mimics the default URL of http://mirrorlist.centos.org

The default package repositories in CentOS look like this:

    # /etc/yum.repos.d/CentOS-Base.repo
    [base]
    name=CentOS-$releasever - Base
    mirrorlist=http://mirrorlist.centos.org/?release=$releasever&arch=$basearch&repo=os
    #baseurl=http://mirror.centos.org/centos/$releasever/os/$basearch/

So instead of pointing directly to the storage host "mirror.centos.org" 
there is a reference to a web service on "mirrorlist.centos.org" that 
will return a list of very different storage host options.

The provided "centos-repo" image is able to answer mirrorlist requests
on its port 80/http. It will simply return a single URL pointing back
to itself. A storage path is attached to serve as the download baseurl.

Example: with --add-host "mirrorlist.centos.org:172.22.0.2"

    REQUEST: http://mirrorlist.centos.org/?release=7&repo=os&arch=x86_64
    REALLLY: http://172.22.0.2/?release=7&repo=os&arch=x86_64
    Answered Mirrorlist:
       http://172.22.0.2/7/os/x86_64

The provided "centos-repo" image will furthermore answer download requests
for yum packages on 80/http - simply the url path is mapped to a local path
in the container and a sendfile will return the content. These are mostly 
`*.rpm` packages as well as some package index files.

For more information check the [centos-repo mirror info](./centos-repo-mirror.info.md)

## ALMALINUX

Mimics the default URL of http://mirrors.almalinux.org

The default package repositories in AlmaLinux look like this:

    # /etc/yum.repos.d/almalinux-baseos.repo
    [baseos]
    name=AlmaLinux $releasever - BaseOS
    mirrorlist=https://mirrors.almalinux.org/mirrorlist/$releasever/baseos
    # baseurl=https://repo.almalinux.org/almalinux/$releasever/BaseOS/$basearch/os/

This looks similar to centos but actually it runs on https and the release and
repo queries are not added as `?parameters` but as path parts. The new style has 
been merged into the centos mirrorlist script.

The same image does also server package requests on https. Be sure that your
dockerfiles have a line `echo sslverify=false >> /etc/yum.conf`.

Other than that, the AlmaLinux images are considered the default continuation
of the CentOS image series. So `centos-docker-mirror.py 8.4` assumes centos
while `centos-docker-mirror.py 8.9` assumes almalinux as the base image.

## EPEL

Mimics the default URL of http://mirrors.fedoraproject.org

This is an extra yum repository that works on top of CentOS or AlmaLinux.

Be sure to add "--epel" to the docker_mirror.py call to get it started as
a second container, which will get included into the `--add-hosts` value
result.

Note that EPEL does not have a release series. You will always get some
latest package from it. Instead the mirror images get an extension number
which reflects the date when docker-mirror-packages-repo was created. The
docker_mirror.py script knows the release dates of the CentOS or AlmaLinux
release, so that it can find an epel-repo which is recent enough.

## OPENSUSE

Mimics the default URL of http://download.opensuse.org

Unlike for centos there is no mirrorlist involved here. All the default 
zypper targets use that single URL. The package indexes are served at 
the same path locations.

The provided "opensuse-repo" image will answer download requests 
for zypper packages on on 80/http - simply the url path is 
mapped to a local path in the container and a sendfile will 
return the content. These are mostly `*.rpm` packages as well
as some package index files.

For mor information check the [opensuse-repo mirror info](./opensuse-repo-mirror.info.md)

## UBUNTU

Mimics the default URL of http://archive.ubuntu.com

Most of the default apt-get targets use that URL. The
only exception is http://security.ubuntu.com for getting
update packages.

The provided "ubuntu-repo" image will answer download requests 
for ubuntu packages on on 80/http - simply the url path 
is mapped to a local path in the container and a sendfile 
will return the content. These are mostly `*.deb` packages 
as well as some package index files.

For more information check the [ubuntu-repo mirror info](./ubuntu-repo-mirror.info.md)

# UBUNTU UNIVERSE

Unlike with Redhat- and Suse-style extra repositories, the
Ubuntu "universe" packages are hosted on the same server. That
requires the "docker_mirror.py" script to start just one container
when it sees the "--universe" option on the command line. It does
try to find a "/universe" docker-mirror-packages-repo variant then.

Since the universe mirror is bigger by a good factor, the default
for docker_mirror.py is to not try to get a universe repo. Likewise
the ubuntu-docker-mirror.py script will not try to sync and include
the universe packages unless it sees the "--universe" option.

There was not attempt made to include multiverse package.

## IMPLEMENTATION

Every package repo has a different way to store data in its
file tree. In general it is not a good idea to just rsync
all of it. Sure you can but...

...for example Ubuntu uses one host for all distro versions.
All `*.deb` packages for all versions are stored in a single
`$host:/pool/` subdirectory. The deb packages for a single
version are listed in a `$host:/dists/$version/Packages.gz` 
file. The distro version is not given by number (16.04) but 
by code name (xenial).

The mirror scripts in this project know about that - so the 
rsync will first download the `Packages.gz` files, in order 
to unpack/filter them into a list of `/pool/x/y/*.deb` paths
in a temporary file. Then `rsync --files-from=pool-files.tmp` 
will do the rest.

When the rsync is complete, only a little web service script
is added on top of building the image. So when the image is
started as a container, it does accept requests on 80/http
serving the rsync'ed files back (except epel-repo since the
usual Fedora URL is shown running on 443/https).

For tips and tricks please see [PROBLEMS FAQ](./PROBLEMS.md).

