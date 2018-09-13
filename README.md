# docker mirror packages repo

These docker images can be started as a container
and it can serve as a replacement for the standard
packages repo of the operating system.

Tested repos are

 * localhost:5000/mirror-packages/**centos-repo:7.3.1611** _(17.3GB)_
 * localhost:5000/mirror-packages/**centos-repo:7.4.1708** _(13.2GB)_
 * localhost:5000/mirror-packages/**centos-repo:7.5.1804** _(14.7GB)_
 * localhost:5000/mirror-packages/**opensuse-repo:15.0**   _(48.9GB)_
 * localhost:5000/mirror-packages/**opensuse-repo:42.3**   _(38.6GB)_
 * localhost:5000/mirror-packages/**ubuntu-repo:16.04**    _(74.7GB)_
 * localhost:5000/mirror-packages/**ubuntu-repo:18.04**    _(19.5GB)_
 * localhost:5000/mirror-packages/**ubuntu-repo/universe:16.04** _(186GB)_
 * localhost:5000/mirror-packages/**ubuntu-repo/updates:16.04** _(74.7GB)_
 * localhost:5000/mirror-packages/**ubuntu-repo/updates:18.04** _(19.5GB)_

Remember that the internet package repos contain updates for the last
distribution release, so they do grow in size over time. As such the
image sizes (as shown above) may differ after each sync.

## CENTOS

Mimics the default http://mirrorlist.centos.org

When there is a mirror-query then it will answer
with an URL pointing back to the docker container.

    ORIG: http://mirrorlist.centos.org/?release=7&repo=os&arch=x86_64
    HERE: http://172.22.0.2/?release=7&repo=os&arch=x86_64
    Answered Mirrorlist:
       http://172.22.0.2/7/os/x86_64

In that way it can serve as an endpoint for another
container requiring yum packages from the central
operation system install repositories.

### centos-repo mirror image

To rebuild check the [centos-repo mirror info](./centos-repo-mirror.info.md)

Currently tested are

     make centos-7.5   # really centos-7.5.1804
     make centos-7.4   # really centos-7.4.1708
     make centos-7.3   # really centos-7.3.1611

## OPENSUSE

Mimics the default http://download.opensuse.org

All the default zypper targets use that URL. The
package indexes are served at the same path 
locations.

In that way it can serve as an endpoint for another
container requiring zypper packages from the central
operation system install repositories.

### opensuse-repo mirror image

To rebuild check the [opensuse-repo mirror info](./opensuse-repo-mirror.info.md)

Currently tested are

     make opensuse-15.0
     make opensuse-42.3
     make opensuse-42.2

## UBUNTU

Mimics the default http://archive.ubuntu.com

Most of the default apt-get targets use that URL. The
only exception is http://security.ubuntu.com but 
those updates are skipped here. Ubuntu stores the
package indexes by code name of the distro (so that
16.04 is in dists/xenial) while the deb packages of 
all distros are stored in /pool.

The mirror copies both the correct dists/ area and
the portions from /pool that are referenced in the
packages index. In that way it can serve as an endpoint 
for another container requiring apt-get packages from 
the central operation system install repositories.

### ubuntu-repo mirror image

To rebuild check the [ubuntu-repo mirror info](./ubuntu-repo-mirror.info.md)

Currently tested are

     make ubuntu-18.10
     make ubuntu-16.04

## Tipps and Tricks

Probably you will not be able to build the images.

That's because docker has a so called "baseimage"
that is the source of all "image" snapshots. No
image can be bigger than the baseimage. And the
baseimage has a default size of 10GB.

Edit /etc/sysconfig/docker and increase that like

    DOCKER_OPTS="--storage-opt dm.basesize=30G"

Theoretically one can just do "service docker restart"
but in reality some versions needed the old baseimage
to be removed from disk so that it is allocated again.
