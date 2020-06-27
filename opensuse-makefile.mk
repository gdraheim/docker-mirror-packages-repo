#! /usr/bin/make -f

IMAGESREPO ?= localhost:5000/mirror-packages

OPENSUSEDATADIRS= $(REPODATADIR) /srv/docker-mirror-packages /data/docker-mirror-packages /data/docker-centos-repo-mirror /dock/docker-mirror-packages
OPENSUSE=opensuse/leap
# LEAP=42.2
# LEAP=42.3
# LEAP=15.0
# LEAP=15.1
# LEAP=15.2
XXLEAP=15.2
LEAP=15.2

RSYNC_SUSE1=rsync://suse.uni-leipzig.de/opensuse-full/opensuse
RSYNC_SUSE2=rsync://ftp.tu-chemnitz.de/pub/linux/opensuse
RSYNC_SUSE=rsync://mirror.cs.upb.de/opensuse

opensuse:
	$(MAKE) opensusesync
	$(MAKE) opensuserepo
	$(MAKE) opensusetest

opensusesync:
	$(MAKE) opensusedir
	$(MAKE) opensusesync1 opensusesync2 opensusesync3 opensusesync4
opensusedir:
	@ test ! -d opensuse.$(LEAP) || rmdir -v opensuse.$(LEAP) || rm -v opensuse.$(LEAP)
	@ for data in $(OPENSUSEDATADIRS); do : \
	; echo .. check $$data \
	; if test -d $$data; then : \
	; test -d  $$data/opensuse.$(LEAP) \
	|| mkdir -v $$data/opensuse.$(LEAP) \
	; ln -svf   $$data/opensuse.$(LEAP) . \
	; fi; done ; true
	@ if test -d opensuse.$(LEAP)/. ; then : \
	; else mkdir -v opensuse.$(LEAP) ; fi
	ls -ld opensuse.$(LEAP)
opensusesync1:
	mkdir -p opensuse.$(LEAP)/distribution/leap/$(LEAP)/repo 
	rsync -rv   $(RSYNC_SUSE)/distribution/leap/$(LEAP)/repo/oss \
	         opensuse.$(LEAP)/distribution/leap/$(LEAP)/repo/ \
	   --filter="exclude boot" --filter="exclude EFI" \
	   --size-only --filter="exclude *.src.rpm"
opensusesync2:
	mkdir -p opensuse.$(LEAP)/distribution/leap/$(LEAP)/repo 
	rsync -rv   $(RSYNC_SUSE)/distribution/leap/$(LEAP)/repo/non-oss \
	         opensuse.$(LEAP)/distribution/leap/$(LEAP)/repo/ \
	   --filter="exclude boot" --filter="exclude noarch" \
	   --filter="exclude x86_64" --filter="exclude EFI" \
	   --size-only --filter="exclude *.src.rpm"
opensusesync3:
	mkdir -p opensuse.$(LEAP)/update/leap/$(LEAP)/ 
	rsync -rv   $(RSYNC_SUSE)/update/leap/$(LEAP)/oss \
	         opensuse.$(LEAP)/update/leap/$(LEAP) \
	   --filter="exclude boot" --filter="exclude *.drpm" \
	   --size-only --filter="exclude *.src.rpm"
opensusesync4:
	mkdir -p opensuse.$(LEAP)/update/leap/$(LEAP) 
	rsync -rv   $(RSYNC_SUSE)/update/leap/$(LEAP)/non-oss \
	         opensuse.$(LEAP)/update/leap/$(LEAP)/ \
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
	docker cp opensuse.$(LEAP)/distribution $@:/srv/repo/
	docker cp opensuse.$(LEAP)/update       $@:/srv/repo/
	: docker exec $@ rm -r /srv/repo/update/$(LEAP)
	docker exec $@ ln -s /srv/repo/update/leap/$(LEAP)/oss /srv/repo/update/$(LEAP)
	docker exec $@ zypper ar file:///srv/repo/distribution/leap/$(LEAP)/repo/oss oss-repo
	docker exec $@ zypper --no-remote install -y python createrepo
	case $(LEAP) in $(XXLEAP)*) : ;; *) exit 0;; esac ;\
	docker exec $@ bash -c "cd /srv/repo/update/leap/$(LEAP)/oss && createrepo ."
	docker commit -c 'CMD $($@_CMD)' -c 'EXPOSE $($@_PORT)' $@ $(IMAGESREPO)/opensuse-repo:$(LEAP)
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

opensusebash:
	- docker rm -f opensuse-bash-$(LEAP)
	- docker rm -f opensuse-repo-$(LEAP)
	docker run -d --rm=true --name opensuse-repo-$(LEAP)  $(IMAGESREPO)/opensuse-repo:$(LEAP)
	IP=`docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' opensuse-repo-$(LEAP)` ;\
	docker run -d --rm=true --name opensuse-bash-$(LEAP)  --add-host download.opensuse.org:$$IP opensuse/leap:$(LEAP) sleep 9999
	docker exec -it opensuse-bash-$(LEAP) bash
