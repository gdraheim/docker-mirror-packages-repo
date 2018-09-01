#! /usr/bin/make -f

IMAGESREPO ?= localhost:5000/mirror-packages

UBUNTUDATADIRS= $(REPODATADIR) /srv/docker-mirror-packages /data/docker-mirror-packages /data/docker-centos-repo-mirror
UBUNTU_OS=ubuntu
UBUNTU=16.04
RSYNC_UBUNTU=rsync://ftp5.gwdg.de/pub/linux/debian/ubuntu
# RSYNC_UBUNTU=rsync://ftp5.gwdg.de/ubuntu

UBUNTU18.10 = cosmic
UBUNTU18.04 = bionic
UBUNTU17.10 = artful
UBUNTU16.04 = xenial
UBUNTU14.04 = trusty
UBUNTU12.04 = precise

ubuntu:
	$(MAKE) ubuntusync
	$(MAKE) ubunturepo
	$(MAKE) ubuntutest

ubuntusync:
	$(MAKE) ubuntudir
	$(MAKE) ubuntu-sync-main # ubuntu-sync-restricted ubuntu-sync-universe ubuntu-sync-multiverse
ubuntudir:
	@ test ! -d ubuntu.$(UBUNTU) || rmdir -v ubuntu.$(UBUNTU) || rm -v ubuntu.$(UBUNTU)
	@ for data in $(UBUNTUDATADIRS); do : \
	; echo .. check $$data \
	; if test -d $$data; then : \
	; test -d  $$data/ubuntu.$(UBUNTU) \
	|| mkdir -v $$data/ubuntu.$(UBUNTU) \
	; ln -sv    $$data/ubuntu.$(UBUNTU) ubuntu.$(UBUNTU) \
	; fi; done ; true
	@ if test -d ubuntu.$(UBUNTU)/. ; then : \
	; else mkdir -v ubuntu.$(UBUNTU) ; fi
	ls -ld ubuntu.$(UBUNTU)
ubuntu-sync-main:
	echo "UBUNTU$(UBUNTU) = $(UBUNTU$(UBUNTU))"
	test  -d ubuntu.$(UBUNTU)/dists/$(UBUNTU$(UBUNTU))/main || \
	mkdir -p ubuntu.$(UBUNTU)/dists/$(UBUNTU$(UBUNTU))/main 
	rsync -rv $(RSYNC_UBUNTU)/dists/$(UBUNTU$(UBUNTU))/main/binary-amd64 \
	         ubuntu.$(UBUNTU)/dists/$(UBUNTU$(UBUNTU))/main \
	   --size-only --filter="exclude *.src.rpm"
	rsync -rv $(RSYNC_UBUNTU)/dists/$(UBUNTU$(UBUNTU))/main/binary-i386 \
	         ubuntu.$(UBUNTU)/dists/$(UBUNTU$(UBUNTU))/main \
	   --size-only --filter="exclude *.src.rpm"
	zcat ubuntu.$(UBUNTU)/dists/$(UBUNTU$(UBUNTU))/main/binary-amd64/Packages.gz \
	     ubuntu.$(UBUNTU)/dists/$(UBUNTU$(UBUNTU))/main/binary-i386/Packages.gz \
	| sed -e '/^Filename:/!d' -e 's|Filename: *pool/||' > Packages.$@.tmp
	rsync -rv $(RSYNC_UBUNTU)/pool \
	         ubuntu.$(UBUNTU)/pool \
	   --size-only --files-from=Packages.$@.tmp

ubunturepo_CMD = ["python","/srv/scripts/filelist.py","--data","/srv/repo"]
ubunturepo_PORT = 80
ubunturepo:
	- docker rm --force $@
	docker run --name=$@ --detach $(UBUNTU_OS):$(UBUNTU) sleep 9999
	docker exec $@ mkdir -p /srv/repo/
	docker cp scripts $@:/srv/scripts
	docker cp ubuntu.$(UBUNTU)/dists $@:/srv/repo/
	docker cp ubuntu.$(UBUNTU)/pool  $@:/srv/repo/
	docker exec $@ apt-get install -y python
	docker commit -c 'CMD $($@_CMD)' -c 'EXPOSE $($@_PORT)' $@ $(IMAGESREPO)/ubuntu-repo:$(UBUNTU)
	docker rm --force $@

ubuntutest:
	cat ubuntu-compose.yml | sed \
	   -e 's|ubuntu-repo:.*"|ubuntu/repo:$(UBUNTU)"|' \
	   -e 's|ubuntu:.*"|$(UBUNTU_OS):$(UBUNTU)"|' \
	   > ubuntu-compose.yml.tmp
	- docker-compose -p $@ -f ubuntu-compose.yml.tmp down
	docker-compose -p $@ -f ubuntu-compose.yml.tmp up -d
	docker exec $@_host_1 apt-get install -y firefox
	docker-compose -p $@ -f ubuntu-compose.yml.tmp down

ubu:
	- docker rm --force $@
	docker run --name=$@ --detach $(UBUNTU_OS):$(UBUNTU) sleep 9999
	@ echo " " docker exec -it $@ bash
