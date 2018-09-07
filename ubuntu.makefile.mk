#! /usr/bin/make -f

IMAGESREPO ?= localhost:5000/mirror-packages

UBUNTUDATADIRS= $(REPODATADIR) /srv/docker-mirror-packages /data/docker-mirror-packages /data/docker-centos-repo-mirror
UBUNTU_OS=ubuntu
UBUNTU=16.04
RSYNC_UBUNTU=rsync://ftp5.gwdg.de/pub/linux/debian/ubuntu

UBUNTU_TMP = ubuntu.tmp

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
	$(MAKE) ubuntutags

ubuntusync:
	$(MAKE) ubuntudir
	$(MAKE) ubuntu-sync-base.1
	$(MAKE) ubuntu-sync-base.2
	$(MAKE) ubuntu-sync-base.3
	$(MAKE) ubuntu-sync-base.4
	$(MAKE) ubuntu-sync-main.1
	$(MAKE) ubuntu-sync-restricted.1
	$(MAKE) ubuntu-sync-universe.1
	$(MAKE) ubuntu-sync-multiverse.1
	$(MAKE) ubuntu-sync-main.2
	$(MAKE) ubuntu-sync-restricted.2
	$(MAKE) ubuntu-sync-universe.2
	$(MAKE) ubuntu-sync-multiverse.2
	$(MAKE) ubuntu-sync-main.3
	$(MAKE) ubuntu-sync-restricted.3
	$(MAKE) ubuntu-sync-universe.3
	$(MAKE) ubuntu-sync-multiverse.3
	$(MAKE) ubuntu-sync-main.4
	$(MAKE) ubuntu-sync-restricted.4
	$(MAKE) ubuntu-sync-universe.4
	$(MAKE) ubuntu-sync-multiverse.4
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
ubuntu-sync-base.1: ; $(MAKE) ubuntu-sync.base dist=$(UBUNTU$(UBUNTU))
ubuntu-sync-base.2: ; $(MAKE) ubuntu-sync.base dist=$(UBUNTU$(UBUNTU))-updates
ubuntu-sync-base.3: ; $(MAKE) ubuntu-sync.base dist=$(UBUNTU$(UBUNTU))-backports
ubuntu-sync-base.4: ; $(MAKE) ubuntu-sync.base dist=$(UBUNTU$(UBUNTU))-security
ubuntu-sync.base:
	echo "dist = $(dist)"
	test  -d ubuntu.$(UBUNTU)/dists/$(dist) || \
	mkdir -p ubuntu.$(UBUNTU)/dists/$(dist)
	@ test -d $(UBUNTU_TMP) || mkdir $(UBUNTU_TMP)
	{ echo "Release" ; echo "InRelease"; } > $(UBUNTU_TMP)/Release.$(dist).base.tmp
	rsync -v $(RSYNC_UBUNTU)/dists/$(dist) \
	        ubuntu.$(UBUNTU)/dists/$(dist) \
	             --ignore-times --files-from=$(UBUNTU_TMP)/Release.$(dist).base.tmp
ubuntu-sync-main.1:       ; $(MAKE) ubuntu-sync.main dist=$(UBUNTU$(UBUNTU)) main=main when=$(filter updates restricted universe multiverse,$(REPOS))
ubuntu-sync-restricted.1: ; $(MAKE) ubuntu-sync.main dist=$(UBUNTU$(UBUNTU)) main=restricted when=$(filter restricted universe multiverse,$(REPOS))
ubuntu-sync-universe.1:   ; $(MAKE) ubuntu-sync.main dist=$(UBUNTU$(UBUNTU)) main=universe when=$(filter universe multiverse,$(REPOS))
ubuntu-sync-multiverse.1: ; $(MAKE) ubuntu-sync.main dist=$(UBUNTU$(UBUNTU)) main=multiverse when=$(filter multiverse,$(REPOS))
ubuntu-sync-main.2:       ; $(MAKE) ubuntu-sync.main dist=$(UBUNTU$(UBUNTU))-updates main=main when=$(filter updates restricted universe multiverse,$(REPOS))
ubuntu-sync-restricted.2: ; $(MAKE) ubuntu-sync.main dist=$(UBUNTU$(UBUNTU))-updates main=restricted when=$(filter restricted universe multiverse,$(REPOS))
ubuntu-sync-universe.2:   ; $(MAKE) ubuntu-sync.main dist=$(UBUNTU$(UBUNTU))-updates main=universe when=$(filter universe multiverse,$(REPOS))
ubuntu-sync-multiverse.2: ; $(MAKE) ubuntu-sync.main dist=$(UBUNTU$(UBUNTU))-updates main=multiverse when=$(filter multiverse,$(REPOS))
ubuntu-sync-main.3:       ; $(MAKE) ubuntu-sync.main dist=$(UBUNTU$(UBUNTU))-backports main=main when=$(filter updates restricted universe multiverse,$(REPOS))
ubuntu-sync-restricted.3: ; $(MAKE) ubuntu-sync.main dist=$(UBUNTU$(UBUNTU))-backports main=restricted when=$(filter restricted universe multiverse,$(REPOS))
ubuntu-sync-universe.3:   ; $(MAKE) ubuntu-sync.main dist=$(UBUNTU$(UBUNTU))-backports main=universe when=$(filter universe multiverse,$(REPOS))
ubuntu-sync-multiverse.3: ; $(MAKE) ubuntu-sync.main dist=$(UBUNTU$(UBUNTU))-backports main=multiverse when=$(filter multiverse,$(REPOS))
ubuntu-sync-main.4:       ; $(MAKE) ubuntu-sync.main dist=$(UBUNTU$(UBUNTU))-security main=main  when=$(filter updates restricted universe multiverse,$(REPOS))
ubuntu-sync-restricted.4: ; $(MAKE) ubuntu-sync.main dist=$(UBUNTU$(UBUNTU))-security main=restricted when=$(filter restricted universe multiverse,$(REPOS))
ubuntu-sync-universe.4:   ; $(MAKE) ubuntu-sync.main dist=$(UBUNTU$(UBUNTU))-security main=universe when=$(filter universe multiverse,$(REPOS))
ubuntu-sync-multiverse.4: ; $(MAKE) ubuntu-sync.main dist=$(UBUNTU$(UBUNTU))-security main=multiverse when=$(filter multiverse,$(REPOS))

downloads=universe
check:
	echo : $(filter update universe, $(downloads))

ubuntu-sync.main:
	test  -d ubuntu.$(UBUNTU)/dists/$(dist)/$(main) || \
	mkdir -p ubuntu.$(UBUNTU)/dists/$(dist)/$(main)
	rsync -rv $(RSYNC_UBUNTU)/dists/$(dist)/$(main)/binary-amd64 \
	         ubuntu.$(UBUNTU)/dists/$(dist)/$(main) --ignore-times
	rsync -rv $(RSYNC_UBUNTU)/dists/$(dist)/$(main)/binary-i386 \
	         ubuntu.$(UBUNTU)/dists/$(dist)/$(main) --ignore-times
	rsync -rv $(RSYNC_UBUNTU)/dists/$(dist)/$(main)/source \
	         ubuntu.$(UBUNTU)/dists/$(dist)/$(main) --ignore-times
	@ test -d $(UBUNTU_TMP) || mkdir $(UBUNTU_TMP)
	zcat ubuntu.$(UBUNTU)/dists/$(dist)/$(main)/binary-amd64/Packages.gz \
	     ubuntu.$(UBUNTU)/dists/$(dist)/$(main)/binary-i386/Packages.gz \
	| sed -e '/^Filename:/!d' -e 's|Filename: *pool/||' \
	                          > $(UBUNTU_TMP)/Packages.$(dist).$(main).tmp
	test -z "$(when)" || \
	rsync -rv $(RSYNC_UBUNTU)/pool \
	         ubuntu.$(UBUNTU)/pool \
	   --size-only --files-from=$(UBUNTU_TMP)/Packages.$(dist).$(main).tmp

ubunturepo_CMD = ["python","/srv/scripts/filelist.py","--data","/srv/repo"]
ubunturepo_PORT = 80
ubunturepo:
	- docker rm --force $@
	docker run --name=$@ --detach $(UBUNTU_OS):$(UBUNTU) sleep 9999
	docker exec $@ mkdir -p /srv/repo/ubuntu
	docker exec $@ mkdir -p /srv/repo/ubuntu
	docker cp scripts $@:/srv/scripts
	docker cp ubuntu.$(UBUNTU)/dists $@:/srv/repo/ubuntu
	docker cp ubuntu.$(UBUNTU)/pool  $@:/srv/repo/ubuntu
	docker exec $@ apt-get update
	docker exec $@ apt-get install -y python
	docker commit -c 'CMD $($@_CMD)' -c 'EXPOSE $($@_PORT)' $@ $(IMAGESREPO)/ubuntu-repo:$(UBUNTU)
	docker rm --force $@
	test -z "$(REPOS)" || $(MAKE) ubuntutags UBUNTU=$(UBUNTU) REPOS=$(REPOS)
ubuntutags:
	test -z "$(filter updates restricted universe multiverse,$(REPOS))" || \
	docker tag $(IMAGESREPO)/ubuntu-repo:$(UBUNTU) $(IMAGESREPO)/ubuntu-repo/updates:$(UBUNTU)
	: test -z "$(filter restricted universe restricted,$(REPOS))" || \
	: docker tag $(IMAGESREPO)/ubuntu-repo:$(UBUNTU) $(IMAGESREPO)/ubuntu-repo/restricted:$(UBUNTU)
	test -z "$(filter universe universe,$(REPOS))" || \
	docker tag $(IMAGESREPO)/ubuntu-repo:$(UBUNTU) $(IMAGESREPO)/ubuntu-repo/universe:$(UBUNTU)
	test -z "$(filter multiverse,$(REPOS))" || \
	docker tag $(IMAGESREPO)/ubuntu-repo:$(UBUNTU) $(IMAGESREPO)/ubuntu-repo/multiverse:$(UBUNTU)

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
