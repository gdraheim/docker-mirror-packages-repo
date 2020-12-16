#! /usr/bin/make -f

LEAP=15.2

opensuse:
	$(MAKE) opensusesync
	$(MAKE) opensuserepo
	$(MAKE) opensusetest

opensusesync: ; ./opensuse-mirror.py $(LEAP) sync -v
opensuserepo: ; ./opensuse-mirror.py $(LEAP) repo -v
opensusetest: ; ./opensuse-mirror.py $(LEAP) test -v

opensusebash:
	- docker rm -f opensuse-bash-$(LEAP)
	- docker rm -f opensuse-repo-$(LEAP)
	docker run -d --rm=true --name opensuse-repo-$(LEAP)  $(IMAGESREPO)/opensuse-repo:$(LEAP)
	IP=`docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' opensuse-repo-$(LEAP)` ;\
	docker run -d --rm=true --name opensuse-bash-$(LEAP)  --add-host download.opensuse.org:$$IP opensuse/leap:$(LEAP) sleep 9999
	docker exec -it opensuse-bash-$(LEAP) bash
