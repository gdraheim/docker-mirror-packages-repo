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

### different versions for the centos-repo

The toplevel Makfile contains some targets to download older (or more recent) versions. That would combine the steps above.

    make centos-7.6   # really centos.7.6.1810
    make centos-7.5   # really centos-7.5.1804
    make centos-7.4   # really centos-7.4.1708
    make centos-7.3   # really centos-7.3.1611
