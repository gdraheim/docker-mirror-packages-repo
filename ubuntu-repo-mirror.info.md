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

The makefiles were later replaced by a python script which does run the "rsync" and "docker" commands as 
subshell processes. It does make it easier to cover the quirks that are needed the different versions of
the opensuse-repo need. Simply provide the intended version as the first argument and you are good to go.

    ./ubuntu-mirror.py 15.2 sync
    ./ubuntu-mirror.py 15.2 repo
    ./ubuntu-mirror.py 15.2 test

The original makefiles targets have been switched to do that with a default version. The old makefiles
implementation may be checked on the github 'makefiles' branch.

