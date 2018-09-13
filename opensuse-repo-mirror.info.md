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

The toplevel Makfile contains some targets to download older (or more recent) versions. That would combine the steps above.

    make opensuse-15.0
    make opensuse-42.3
    make opensuse-42.2
