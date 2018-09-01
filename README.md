# docker pkg repo mirror

These docker image scan be started as a container
and it can serve as a replacment for the standard
package repo of the operationg system.

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

### building the centos-repo image

I did have bad experiences with a direct download to
package container, so now there is Makefile that does
(1) do rsync to local disk and then (2) build an image 
as a copy of the disk data

     make sync
     make centosrepo
     make centostest

## OPENSUSE

Mimics the default http://download.opensuse.org

All the default zypper targets use that URL. The
package indexes are served at the same path 
locations.

In that way it can serve as an endpoint for another
container requiring zypper packages from the central
operation system install repositories.

### building the opensuse-repo image

I did have bad experiences with a direct download to
package container, so now there is Makefile that does
(1) do rsync to local disk and then (2) build an image 
as a copy of the disk data

     make rsync
     make opensuserepo
     make opensusetest

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
