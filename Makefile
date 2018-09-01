#! /usr/bin/make -f

CENTOS_VER = 7.5
CENTOS = 7.5.1804
# CENTOS = 7.4.1708
# CENTOS_VER = 7.3
# CENTOS = 7.3.1611

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
	$(MAKE) centosrepo
	$(MAKE) centostest
	$(MAKE) centoscheck
	$(MAKE) centosversion

CENTOS_MIRROR=rsync://rsync.hrz.tu-chemnitz.de/ftp/pub/linux/centos

sync:
	$(MAKE) sync-dir
	$(MAKE) sync-all
sync-dir:
	if test -d $(DATA); then mkdir $(DATA)/centos-$(CENTOS); ln -s $(DATA)/centos-$(CENTOS) centos-$(CENTOS) \
	; else mkdir centos-$(CENTOS); fi; test -d centos-$(CENTOS)/.
sync-all: sync-os sync-extras sync-updates
sync-os: ;      rsync -rv $(CENTOS_MIRROR)/$(CENTOS)/os      centos-$(CENTOS)/ --exclude "*.iso"
sync-extras: ;  rsync -rv $(CENTOS_MIRROR)/$(CENTOS)/extras  centos-$(CENTOS)/
sync-updates: ; rsync -rv $(CENTOS_MIRROR)/$(CENTOS)/updates centos-$(CENTOS)/
centos-unpack:
	- docker rm --force $@
	docker run --name=$@ --detach localhost:5000/centos-repo:$(CENTOS) sleep 9999
	docker cp $@:/srv/repo/7/os centos-$(CENTOS)/
	docker cp $@:/srv/repo/7/extras centos-$(CENTOS)/
	docker cp $@:/srv/repo/7/updates centos-$(CENTOS)/
	docker rm --force $@
	du -sh centos-$(CENTOS)/.
centos-clean:
	rm -rf centos-$(CENTOS)/os
	rm -rf centos-$(CENTOS)/extras
	rm -rf centos-$(CENTOS)/updates

centosrepo_CMD = ["python","/srv/scripts/mirrorlist.py","--data","/srv/repo"]
centosrepo_PORT = 80
centosrepo:
	$(MAKE) centos-restore centos-cleaner
	- docker rm --force $@
	docker run --name=$@ --detach centos:$(CENTOS) sleep 9999
	docker exec $@ mkdir -p /srv/repo/7
	docker cp scripts $@:/srv/scripts
	docker cp centos-$(CENTOS)/os $@:/srv/repo/7/
	docker cp centos-$(CENTOS)/extras $@:/srv/repo/7/
	docker cp centos-$(CENTOS)/updates $@:/srv/repo/7/
	docker commit -c 'CMD $($@_CMD)' -c 'EXPOSE $($@_PORT)' $@ localhost:5000/centos-repo:$(CENTOS)
	docker rm --force $@
	$(MAKE) centos-restore
centosversion: centos-repo
centos-repo:
	docker tag localhost:5000/$@:$(CENTOS) localhost:5000/$@:$(CENTOS_VER)
centos-cleaner:
	test ! -d centos-$(CENTOS)/updates/x86_64/drpms \
	 || mv -v centos-$(CENTOS)/updates/x86_64/drpms \
	          centos-$(CENTOS)/updates.x86_64.drpms 
	test ! -d centos-$(CENTOS)/extras/x86_64/drpms \
	 || mv -v centos-$(CENTOS)/extras/x86_64/drpms \
	          centos-$(CENTOS)/extras.x86_64.drpms 
centos-restore:
	test ! -d centos-$(CENTOS)/updates.x86_64.drpms \
	 || mv -v centos-$(CENTOS)/updates.x86_64.drpms \
	          centos-$(CENTOS)/updates/x86_64/drpms 
	test ! -d centos-$(CENTOS)/extras.x86_64.drpms \
	 || mv -v centos-$(CENTOS)/extras.x86_64.drpms \
	          centos-$(CENTOS)/extras/x86_64/drpms 

centostest:
	sed -e "s|centos:centos7|centos:$(CENTOS)|" -e "s|centos-repo:7|centos-repo:$(CENTOS)|" \
	  centos-compose.yml > centos-compose.tmp
	- docker-compose -p $@ -f centos-compose.tmp down
	docker-compose -p $@ -f centos-compose.tmp up -d
	docker exec centosworks_host_1 yum install -y firefox
	docker-compose -p $@ -f centos-compose.tmp down

centoscheck:
	- docker rm --force $@
	docker run --name=$@ --detach centos:$(CENTOS) sleep 9999
	docker exec $@ rpm -qa | { while read f; do : \
	; found=`find centos-$(CENTOS)/. -name $$f.rpm` \
	; if [ -z "$$found" ]; then echo : ; else echo "OK $$f         $$found"; fi \
	; done ; }
	docker exec $@ rpm -qa | { while read f; do : \
	; found=`find centos-$(CENTOS)/. -name $$f.rpm` \
	; if [ -z "$$found" ]; then echo "?? $$f $$found"; else : ; fi \
	; done ; }
	docker rm --force $@

############## OPENSUSE VARIANT ############
# this is faster and it is more robust #
# however it doubles the required disk #

DATA=/data/docker-centos-repo-mirror
OPENSUSE=opensuse/leap
LEAP=15.0
SUSE=rsync://suse.uni-leipzig.de/opensuse-full/opensuse

rsync:
	$(MAKE) rsync-
	$(MAKE) rsync1 rsync2 rsync3 rsync4
rsync-:
	if test -d $(DATA); then mkdir $(DATA)/leap-$(LEAP); ln -s $(DATA)/leap-$(LEAP) leap-$(LEAP) \
	; else mkdir leap-$(LEAP); fi; test -d leap-$(LEAP)/.
rsync1:
	mkdir -p leap-$(LEAP)/distribution/leap/$(LEAP)/repo 
	rsync -rv     $(SUSE)/distribution/leap/$(LEAP)/repo/oss \
	         leap-$(LEAP)/distribution/leap/$(LEAP)/repo/ \
	   --filter="exclude boot" --filter="exclude EFI" \
	   --size-only --filter="exclude *.src.rpm"
rsync2:
	mkdir -p leap-$(LEAP)/distribution/leap/$(LEAP)/repo 
	rsync -rv     $(SUSE)/distribution/leap/$(LEAP)/repo/non-oss \
	         leap-$(LEAP)/distribution/leap/$(LEAP)/repo/ \
	   --filter="exclude boot" --filter="exclude noarch" \
	   --filter="exclude x86_64" --filter="exclude EFI" \
	   --size-only --filter="exclude *.src.rpm"
rsync3:
	mkdir -p leap-$(LEAP)/update/leap/$(LEAP)/ 
	rsync -rv     $(SUSE)/update/leap/$(LEAP)/oss \
	         leap-$(LEAP)/update/leap/$(LEAP) \
	   --filter="exclude boot" --filter="exclude *.drpm" \
	   --size-only --filter="exclude *.src.rpm"
rsync4:
	mkdir -p leap-$(LEAP)/update/leap/$(LEAP) 
	rsync -rv     $(SUSE)/update/leap/$(LEAP)/non-oss \
	         leap-$(LEAP)/update/leap/$(LEAP)/ \
	   --filter="exclude boot" --filter="exclude noarch" --filter="exclude x86_64" \
	   --filter="exclude EFI" --filter="exclude src" --filter="exclude nosrc" \
	   --size-only --filter="exclude *.src.rpm"

# /etc/zypp/repos.d/oss-update.repo:baseurl=http://download.opensuse.org/update/42.2/
# /etc/zypp/repos.d/update-non-oss.repo:baseurl=http://download.opensuse.org/update/leap/42.2/non-oss/
# /etc/zypp/repos.d/oss.repo:baseurl=http://download.opensuse.org/distribution/leap/42.2/repo/oss/
# /etc/zypp/repos.d/non-oss.repo:baseurl=http://download.opensuse.org/distribution/leap/42.2/repo/non-oss/

opensuserepo_CMD = ["python","/srv/scripts/filelist.py","--data","/srv/repo"]
opensuserepo_PORT = 80
opensuserepo:
	- docker rm --force $@
	docker run --name=$@ --detach $(OPENSUSE):$(LEAP) sleep 9999
	docker exec $@ mkdir -p /srv/repo/
	docker cp scripts $@:/srv/scripts
	docker cp leap-$(LEAP)/distribution $@:/srv/repo/
	docker cp leap-$(LEAP)/update       $@:/srv/repo/
	: docker exec $@ rm -r /srv/repo/update/$(LEAP)
	docker exec $@ ln -s /srv/repo/update/leap/$(LEAP)/oss /srv/repo/update/$(LEAP)
	docker exec $@ zypper ar file:///srv/repo/distribution/leap/$(LEAP)/repo/oss oss-repo
	docker exec $@ zypper --no-remote install -y python
	docker commit -c 'CMD $($@_CMD)' -c 'EXPOSE $($@_PORT)' $@ localhost:5000/opensuse-repo:$(LEAP)
	docker rm --force $@

opensusetest:
	cat opensuse-compose.yml | sed \
	   -e 's|opensuse-repo:.*"|opensuse/repo:$(LEAP)"|' \
	   -e 's|opensuse:.*"|$(OPENSUSE):$(LEAP)"|' \
	   > opensuse-compose.yml.tmp
	- docker-compose -p $@ -f opensuse-compose.yml.tmp down
	docker-compose -p $@ -f opensuse-compose.yml.tmp up -d
	docker exec $@_host_1 zypper install -y firefox
	docker-compose -p $@ -f opensuse-compose.yml.tmp down

