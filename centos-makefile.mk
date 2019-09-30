#! /usr/bin/make -f

IMAGESREPO ?= localhost:5000/mirror-packages

CENTOSDATADIRS= $(REPODATADIR) /srv/docker-mirror-packages /data/docker-mirror-packages /data/docker-centos-repo-mirror

CENTOS = 7.5.1804
# CENTOS = 7.4.1708
# CENTOS = 7.3.1611
# CENTOS = 7.2.1511
# CENTOS = 7.1.1503
# CENTOS = 7.0.1406

############# WGET VARIANT ##########
# it simply downloads the rpms, but #
# it turned out to fail to create   #
# some docker layers in docker 1.12 #

7.3: 7.3.1611
	docker tag "localhost:5000/centos-repo:$@" "localhost:5000/centos-repo:7"
7.3.1611: 
	docker build -f centos-repo.$@.dockerfile --tag "localhost:5000/centos-repo:$@" .
	docker tag "localhost:5000/centos-repo:$@" "localhost:5000/centos-repo:7.3"

############## SYNC VARIANT ############
# this is faster and it is more robust #
# however it doubles the required disk #
# space to get a centos-repo:x image!! #

centos:
	$(MAKE) centossync
	$(MAKE) centosrepo
	$(MAKE) centostest
	$(MAKE) centoscheck
	$(MAKE) centostags

CENTOS_MIRROR=rsync://rsync.hrz.tu-chemnitz.de/ftp/pub/linux/centos


centossync:
	$(MAKE) centosdir
	$(MAKE) sync-os sync-extras sync-updates
centosdir:
	@ test ! -d centos.$(CENTOS) || rmdir -v centos.$(CENTOS) || rm -v centos.$(CENTOS)
	@ for data in $(CENTOSDATADIRS); do : \
	; echo .. check $$data \
	; if test -d $$data; then : \
	; test -d  $$data/centos.$(CENTOS) \
	|| mkdir -v $$data/centos.$(CENTOS) \
	; ln -sv    $$data/centos.$(CENTOS) centos.$(CENTOS) \
	; fi; done ; true
	@ if test -d centos.$(CENTOS)/. ; then : \
	; else mkdir -v centos.$(CENTOS) ; fi
	ls -ld centos.$(CENTOS)

sync-os: ;      rsync -rv $(CENTOS_MIRROR)/$(CENTOS)/os      centos.$(CENTOS)/ --exclude "*.iso"
sync-extras: ;  rsync -rv $(CENTOS_MIRROR)/$(CENTOS)/extras  centos.$(CENTOS)/
sync-updates: ; rsync -rv $(CENTOS_MIRROR)/$(CENTOS)/updates centos.$(CENTOS)/
centos-unpack:
	- docker rm --force $@
	docker run --name=$@ --detach localhost:5000/centos-repo:$(CENTOS) sleep 9999
	docker cp $@:/srv/repo/7/os centos.$(CENTOS)/
	docker cp $@:/srv/repo/7/extras centos.$(CENTOS)/
	docker cp $@:/srv/repo/7/updates centos.$(CENTOS)/
	docker rm --force $@
	du -sh centos-$(CENTOS)/.
centos-clean:
	rm -rf centos.$(CENTOS)/os
	rm -rf centos.$(CENTOS)/extras
	rm -rf centos.$(CENTOS)/updates

centosrepo_CMD = ["python","/srv/scripts/mirrorlist.py","--data","/srv/repo"]
centosrepo_PORT = 80
centosrepo:
	$(MAKE) centos-restore centos-cleaner
	- docker rm --force $@
	docker run --name=$@ --detach centos:$(CENTOS) sleep 9999
	docker exec $@ mkdir -p /srv/repo/7
	docker cp scripts $@:/srv/scripts
	docker cp centos.$(CENTOS)/os $@:/srv/repo/7/
	docker cp centos.$(CENTOS)/extras $@:/srv/repo/7/
	docker cp centos.$(CENTOS)/updates $@:/srv/repo/7/
	docker commit -c 'CMD $($@_CMD)' -c 'EXPOSE $($@_PORT)' $@ $(IMAGESREPO)/centos-repo:$(CENTOS)
	docker rm --force $@
	$(MAKE) centos-restore

centostags: centos-repo
centos-repo:
	ver2=`echo $(CENTOS) | sed -e "s|^\\([01234567890][01234567890]*[.][01234567890]*\\).*|\\1|"` \
	; docker tag $(IMAGESREPO)/$@:$(CENTOS) $(IMAGESREPO)/$@:$$ver2
	ver1=`echo $(CENTOS) | sed -e "s|^\\([01234567890][01234567890]*\\).*|\\1|"` \
	;  docker tag $(IMAGESREPO)/$@:$(CENTOS) $(IMAGESREPO)/$@$$ver1:$(CENTOS) \
	&& docker tag $(IMAGESREPO)/$@:$(CENTOS) $(IMAGESREPO)/$@$$ver1:latest

centos-cleaner:
	test ! -d centos.$(CENTOS)/updates/x86_64/drpms \
	 || mv -v centos.$(CENTOS)/updates/x86_64/drpms \
	          centos.$(CENTOS)/updates.x86_64.drpms 
	test ! -d centos.$(CENTOS)/extras/x86_64/drpms \
	 || mv -v centos.$(CENTOS)/extras/x86_64/drpms \
	          centos.$(CENTOS)/extras.x86_64.drpms 
centos-restore:
	test ! -d centos.$(CENTOS)/updates.x86_64.drpms \
	 || mv -v centos.$(CENTOS)/updates.x86_64.drpms \
	          centos.$(CENTOS)/updates/x86_64/drpms 
	test ! -d centos.$(CENTOS)/extras.x86_64.drpms \
	 || mv -v centos.$(CENTOS)/extras.x86_64.drpms \
	          centos.$(CENTOS)/extras/x86_64/drpms 

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
	; found=`find centos.$(CENTOS)/. -name $$f.rpm` \
	; if [ -z "$$found" ]; then echo : ; else echo "OK $$f         $$found"; fi \
	; done ; }
	docker exec $@ rpm -qa | { while read f; do : \
	; found=`find centos.$(CENTOS)/. -name $$f.rpm` \
	; if [ -z "$$found" ]; then echo "?? $$f $$found"; else : ; fi \
	; done ; }
	docker rm --force $@
