# hardlinked repositories

The number of distros on my disk and in the `docker images` list has grown over time.
That leads to a situation that even some terrabyte of disk space may face some pressure.

Instead of copying the data from the sync-dir into the container, it is also possible
to mount the repo data. This is generally handled by specs in `~/.config/docker_mirror.ini`.

## disk and base

Instead of `ubunturepo` or `opensuserepo` or `centosrepo` you 
need to run two targets for each repo version.

* `make ubuntubase.24.04`
* `make ubuntudisk.24.04`

As a result it will print out the values needed for `docker_mirror.ini`.

Note that you can not directly mount the sync-dirs. They are broken into multiple
pieces ('base' and 'update' repos) and their metadata index is often broken. This
is fixed when copying the data into the repo-image container -or- when the '.disk' 
directory  is created. The rpm/deb files themselves are hardlinked into the '.disk' 
directory, so they do not consume extra space.

(Technical detail: to hardlink a file in Unix means that the same inode has 
multiple file names. Writing to such a file may update the data in two locations. 
The repodata-fix.py script will therefore backup the old package.xml and create a 
new file in the '.disk' area. So that file is not hardlinked with the sync-dir).

## docker_mirror.ini

The `docker_mirror.ini` can hold overrides that are used to start a repo-container
via `docker_mirror.py`. Here's what I have as of 2024. This allows me to

* `./docker_mirror.py --local start almalinux:9.4 --add-hosts -vvv`

docker_mirror.ini:

    [almalinux:9.4-20240530]
    image = localhost:5000/mirror-packages/almalinux-repo/base:9.4
    mount = /dock/docker-mirror-packages/almalinux.9.4-20240530.disk/srv/repo
    
    [opensuse/leap:15.4]
    image = localhost:5000/mirror-packages/opensuse-repo/base:15.4
    mount = /dock/docker-mirror-packages/opensuse.15.4.disk/srv/repo
    
    [opensuse/leap:15.5]
    image = localhost:5000/mirror-packages/opensuse-repo/base:15.5
    mount = /dock/docker-mirror-packages/opensuse.15.5.disk/srv/repo
    
    [opensuse/leap:15.6]
    image = localhost:5000/mirror-packages/opensuse-repo/base:15.6
    mount = /dock/docker-mirror-packages/opensuse.15.6.disk/srv/repo
    
    [ubuntu:20.04]
    image = localhost:5000/mirror-packages/ubuntu-repo/base:20.04
    mount = /dock/docker-mirror-packages/ubuntu.20.04.disk/srv/repo
    
    [ubuntu:22.04]
    image = localhost:5000/mirror-packages/ubuntu-repo/base:22.04
    mount = /dock/docker-mirror-packages/ubuntu.22.04.disk/srv/repo
    
    [ubuntu:24.04]
    image = localhost:5000/mirror-packages/ubuntu-repo/base:24.04
    mount = /dock/docker-mirror-packages/ubuntu.24.04.disk/srv/repo






