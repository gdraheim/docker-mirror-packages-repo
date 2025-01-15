## OPENSUSE REPO

Mimics the default http://download.opensuse.org

All the default zypper targets use that URL. The package indexes are served at the same path locations.

In that way it can serve as an endpoint for another container requiring zypper packages from the central operation system install repositories.

### building the opensuse-repo image

I did have bad experiences with a direct download to package container, so now there is Makefile that does (1) do rsync to local disk and then (2) build an image as a copy of the disk data

    make opensusesync
    make opensuserepo
    make opensusetest

### different versions for the opensuse-repo

The makefiles were later replaced by a python script which does run the "rsync" and "docker" commands as 
subshell processes. It does make it easier to cover the quirks that are needed the different versions of
the opensuse-repo need. Simply provide the intended version as the first argument and you are good to go.

    ./opensuse-docker-mirror.py 15.2 sync
    ./opensuse-docker-mirror.py 15.2 repo
    ./opensuse-docker-mirror.py 15.2 test

The original makefiles targets have been switched to do that with a default version. The old makefiles
implementation may be checked on the github 'makefiles' branch.

### testsuite and results

opensuse-docker-mirror.py     450     42    91%

| mirror-packages image | size
| --------------------- | -----------------------------------------
| localhost:5000/mirror-packages/opensuse-repo/update:15.2 | 118GB
| localhost:5000/mirror-packages/opensuse-repo:15.2 | 118GB
| localhost:5000/mirror-packages/opensuse-repo/main:15.2 | 93.2GB
| localhost:5000/mirror-packages/opensuse-repo/base:15.2 | 153MB
| localhost:5000/mirror-packages/opensuse-repo/update:15.4 | 143GB
| localhost:5000/mirror-packages/opensuse-repo:15.4 | 143GB
| localhost:5000/mirror-packages/opensuse-repo/main:15.4 | 59.8GB
| localhost:5000/mirror-packages/opensuse-repo/base:15.4 | 160MB
| localhost:5000/mirror-packages/opensuse-repo/update:15.5 | 112GB
| localhost:5000/mirror-packages/opensuse-repo:15.5 | 112GB
| localhost:5000/mirror-packages/opensuse-repo/main:15.5 | 70.7GB
| localhost:5000/mirror-packages/opensuse-repo/base:15.5 | 158MB
| localhost:5000/mirror-packages/opensuse-repo/update:15.6 | 211GB
| localhost:5000/mirror-packages/opensuse-repo:15.6 | 211GB
| localhost:5000/mirror-packages/opensuse-repo/main:15.6 | 205GB
| localhost:5000/mirror-packages/opensuse-repo/base:15.6 | 162MB


