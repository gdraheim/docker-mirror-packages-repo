#! /usr/bin/make -f

CENTOS_VER = 7.3
CENTOS = 7.3.1611

default: all

############# WGET VARIANT ##########
# it simply downloads the rpms, but #
# it turned out to fail to create   #
# some docker layers in docker 1.12 #

7.3: 7.3.1611
	docker tag "localhost:5000/centos-repo:$@" "localhost:5000/centos-repo:7"
7.3.1611: 
	docker build -f centos-repo.$@.dockerfile --tag "localhost:5000/centos-repo:$@" .
	docker tag "localhost:5000/centos-repo:$@" "localhost:5000/centos-repo:7.3"
7.2: 7.2.1511
7.1: 7.1.1503
7.0: 7.0.1406
6.9:
6.8:
6.7:

############## SYNC VARIANT ############
# this is faster and it is more robust #
# however it doubles the required disk #
# space to get a centos-os:7.3 image!! #

all:
	$(MAKE) sync
	$(MAKE) centos
	$(MAKE) testcentos
	$(MAKE) centos-repo

CENTOS_MIRROR=rsync://rsync.hrz.tu-chemnitz.de/ftp/pub/linux/centos

sync:
	if test -d $(DATA); then mkdir $(DATA)/centos-$(CENTOS); ln -s $(DATA)/centos-$(CENTOS) centos-$(CENTOS) \
	; else mkdir centos-$(CENTOS); fi; test -d centos-$(CENTOS)/.
	$(MAKE) sync-os sync-extras sync-updates
sync-os: ;      rsync -rv $(CENTOS_MIRROR)/$(CENTOS)/os      centos-$(CENTOS)/ --exclude "*.iso"
sync-extras: ;  rsync -rv $(CENTOS_MIRROR)/$(CENTOS)/extras  centos-$(CENTOS)/
sync-updates: ; rsync -rv $(CENTOS_MIRROR)/$(CENTOS)/updates centos-$(CENTOS)/

centos_CMD = ["python","/srv/scripts/mirrorlist.py","--data","/srv/repo"]
centos:
	- docker rm --force $@
	docker run --name=$@ --detach $@:$(CENTOS) sleep 9999
	docker exec $@ mkdir -p /srv/repo/7
	docker cp scripts $@:/srv/scripts
	docker cp centos-$(CENTOS)/os $@:/srv/repo/7/
	docker cp centos-$(CENTOS)/extras $@:/srv/repo/7/
	docker cp centos-$(CENTOS)/updates $@:/srv/repo/7/
	docker commit -c 'CMD $($@_CMD)' $@ localhost:5000/$@-repo:$(CENTOS)
	docker rm --force $@
centos-repo:
	docker tag localhost:5000/$@:$(CENTOS) localhost:5000/$@:$(CENTOS_VER)

testcentos:
	- docker-compose -p $@ -f centos-compose.yml down
	docker-compose -p $@ -f centos-compose.yml up -d
	docker exec testcentos_host_1 yum install -y firefox
	docker-compose -p $@ -f centos-compose.yml $@ down

############## OPENSUSE VARIANT ############
# this is faster and it is more robust #
# however it doubles the required disk #

DATA=/data/docker-centos-repo-mirror
LEAP=42.2
SUSE=rsync://suse.uni-leipzig.de/opensuse-full/opensuse
rsync:
	if test -d $(DATA); then mkdir $(DATA)/leap-$(LEAP); ln -s $(DATA)/leap-$(LEAP) leap-$(LEAP) \
	; else mkdir leap-$(LEAP); fi; test -d leap-$(LEAP)/.
	$(MAKE) rsync1 rsync2 rsync3 rsync4
rsync1:
	mkdir -p leap-$(LEAP)/distribution/leap/$(LEAP)/repo 
	rsync -rv     $(SUSE)/distribution/leap/$(LEAP)/repo/oss \
	         leap-$(LEAP)/distribution/leap/$(LEAP)/repo/ \
	   --filter="exclude boot" --filter="exclude EFI"
rsync2:
	mkdir -p leap-$(LEAP)/distribution/leap/$(LEAP)/repo 
	rsync -rv     $(SUSE)/distribution/leap/$(LEAP)/repo/non-oss \
	         leap-$(LEAP)/distribution/leap/$(LEAP)/repo/ \
	   --filter="exclude boot" --filter="exclude noarch" --filter="exclude x86_64" --filter="exclude EFI"
rsync3:
	mkdir -p leap-$(LEAP)/update/leap/$(LEAP)/ 
	rsync -rv     $(SUSE)/update/leap/$(LEAP)/oss \
	         leap-$(LEAP)/update/leap/$(LEAP) \
	   --filter="exclude boot"
rsync4:
	mkdir -p leap-$(LEAP)/update/leap/$(LEAP) 
	rsync -rv     $(SUSE)/update/leap/$(LEAP)/non-oss \
	         leap-$(LEAP)/update/leap/$(LEAP)/ \
	   --filter="exclude boot" --filter="exclude noarch" --filter="exclude x86_64" \
	   --filter="exclude EFI" --filter="exclude src" --filter="exclude nosrc"

# /etc/zypp/repos.d/oss-update.repo:baseurl=http://download.opensuse.org/update/42.2/
# /etc/zypp/repos.d/update-non-oss.repo:baseurl=http://download.opensuse.org/update/leap/42.2/non-oss/
# /etc/zypp/repos.d/oss.repo:baseurl=http://download.opensuse.org/distribution/leap/42.2/repo/oss/
# /etc/zypp/repos.d/non-oss.repo:baseurl=http://download.opensuse.org/distribution/leap/42.2/repo/non-oss/

opensuse_CMD = ["python","/srv/scripts/filelist.py","--data","/srv/repo"]
opensuse:
	- docker rm --force $@
	docker run --name=$@ --detach $@:$(LEAP) sleep 9999
	docker exec $@ mkdir -p /srv/repo/
	docker cp scripts $@:/srv/scripts
	docker cp leap-$(LEAP)/distribution $@:/srv/repo/
	docker cp leap-$(LEAP)/update       $@:/srv/repo/
	docker exec $@ rm -r /srv/repo/update/$(LEAP)
	docker exec $@ ln -s /srv/repo/update/leap/$(LEAP)/oss /srv/repo/update/$(LEAP)
	docker exec $@ zypper ar file:///srv/repo/distribution/leap/42.2/repo/oss oss-repo
	docker exec $@ zypper --no-remote install -y python
	docker commit -c 'CMD $($@_CMD)' $@ localhost:5000/$@-repo:$(LEAP)
	docker rm --force $@

testsuse:
	- docker-compose -p $@ down
	docker-compose -p $@ -f opensuse-compose.yml up -d
	docker exec $@_host_1 zypper install -r oss -y firefox
	docker-compose -p $@ -f opensuse-compose.yml down

testsus:
	- docker-compose -p $@e down
	docker-compose -p $@e -f opensuse-compose.yml up -d
