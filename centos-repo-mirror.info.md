## CENTOS REPO

Mimics the default http://mirrorlist.centos.org

When there is a mirror-query then it will answer with an URL pointing back to the docker container.

    ORIG: http://mirrorlist.centos.org/?release=7&repo=os&arch=x86_64
    HERE: http://172.22.0.2/?release=7&repo=os&arch=x86_64
    Answered Mirrorlist:
       http://172.22.0.2/7/os/x86_64

In that way it can serve as an endpoint for another container requiring yum packages from the central operation system install repositories.

### building the centos-repo image

I did have bad experiences with a direct download to package container, so now there is Makefile that does (1) do rsync to local disk and then (2) build an image as a copy of the disk data

    make centossync
    make centosrepo
    make centostest

