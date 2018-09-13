## UBUNTU REPO

Mimics the default http://archive.ubuntu.com

Most of the default apt-get targets use that URL. The only exception is http://security.ubuntu.com but those updates are skipped here. Ubuntu stores the package indexes by code name of the distro (so that 16.04 is in dists/xenial) while the deb packages of all distros are stored in /pool.

The mirror copies both the correct dists/ area and the portions from /pool that are referenced in the packages index. In that way it can serve as an endpoint for another container requiring apt-get packages from the central operation system install repositories.

### building the ubuntu-repo image

I did have bad experiences with a direct download to package container, so now there is Makefile that does (1) do rsync to local disk and then (2) build an image as a copy of the disk data

    make ubuntusync
    make ubunturepo
    make ubuntutest

### different versions for the ubuntu-repo

The toplevel Makfile contains some targets to download older (or more recent) versions. That would combine the steps above.

    make ubuntu-18.10
    make ubuntu-16.04
