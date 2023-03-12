#! /usr/bin/make -f

LEAP=15.3

opensuse:
	$(MAKE) opensusesync
	$(MAKE) opensuserepo
	$(MAKE) opensusetest

opensusesync: ; ./opensuse-docker-mirror.py $(LEAP) sync -v
opensuserepo: ; ./opensuse-docker-mirror.py $(LEAP) repo -v
opensusetest: ; ./opensuse-docker-mirror.py $(LEAP) test -v

opensusebash:
	- docker rm -f opensuse-bash-$(LEAP)
	- docker rm -f opensuse-repo-$(LEAP)
	docker run -d --rm=true --name opensuse-repo-$(LEAP)  $(IMAGESREPO)/opensuse-repo:$(LEAP)
	IP=`docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' opensuse-repo-$(LEAP)` ;\
	docker run -d --rm=true --name opensuse-bash-$(LEAP)  --add-host download.opensuse.org:$$IP opensuse/leap:$(LEAP) sleep 9999
	docker exec -it opensuse-bash-$(LEAP) bash

## opensuse versions

opensuse.15.4: ; $(MAKE) opensusedir LEAP=15.4
opensuse.15.3: ; $(MAKE) opensusedir LEAP=15.3
opensuse.15.2: ; $(MAKE) opensusedir LEAP=15.2
opensuse.15.1: ; $(MAKE) opensusedir LEAP=15.1
opensuse.15.0: ; $(MAKE) opensusedir LEAP=15.0
opensuse.42.3: ; $(MAKE) opensusedir LEAP=42.3
opensuse.42.2: ; $(MAKE) opensusedir LEAP=42.2
opensusesync.15.4: ; $(MAKE) opensusesync LEAP=15.4
opensusesync.15.3: ; $(MAKE) opensusesync LEAP=15.3
opensusesync.15.2: ; $(MAKE) opensusesync LEAP=15.2
opensusesync.15.1: ; $(MAKE) opensusesync LEAP=15.1
opensusesync.15.0: ; $(MAKE) opensusesync LEAP=15.0
opensusesync.42.3: ; $(MAKE) opensusesync LEAP=42.3
opensuserepo.15.4: ; $(MAKE) opensuserepo LEAP=15.4 OPENSUSE=opensuse/leap
opensuserepo.15.3: ; $(MAKE) opensuserepo LEAP=15.3 OPENSUSE=opensuse/leap
opensuserepo.15.2: ; $(MAKE) opensuserepo LEAP=15.2 OPENSUSE=opensuse/leap
opensuserepo.15.1: ; $(MAKE) opensuserepo LEAP=15.1 OPENSUSE=opensuse/leap
opensuserepo.15.0: ; $(MAKE) opensuserepo LEAP=15.0 OPENSUSE=opensuse/leap
opensuserepo.42.3: ; $(MAKE) opensuserepo LEAP=42.3 OPENSUSE=opensuse
opensuse-15.4: ; $(MAKE) opensuse LEAP=15.4 OPENSUSE=opensuse/leap
opensuse-15.3: ; $(MAKE) opensuse LEAP=15.3 OPENSUSE=opensuse/leap
opensuse-15.2: ; $(MAKE) opensuse LEAP=15.2 OPENSUSE=opensuse/leap
opensuse-15.1: ; $(MAKE) opensuse LEAP=15.1 OPENSUSE=opensuse/leap
opensuse-15.0: ; $(MAKE) opensuse LEAP=15.0 OPENSUSE=opensuse/leap
opensuse-42.3: ; $(MAKE) opensuse LEAP=42.3 OPENSUSE=opensuse
opensuse-42.2: ; $(MAKE) opensuse LEAP=42.2 OPENSUSE=opensuse
