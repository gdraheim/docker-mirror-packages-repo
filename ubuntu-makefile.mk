#! /usr/bin/make -f

UBUNTU = 20.04
UBUNTU_REPOS ?= --updates
# UNTU_REPOS ?= --universe
# UNTU_REPOS ?= --multiverse

ubuntu:
	$(MAKE) ubuntusync
	$(MAKE) ubunturepo
	$(MAKE) ubuntutest
	$(MAKE) ubuntutags

ubuntusync: ; ./ubuntu-mirror.py $(UBUNTU) sync -v $(UBUNTU_REPOS)
ubunturepo: ; ./ubuntu-mirror.py $(UBUNTU) repo -v $(UBUNTU_REPOS)
ubuntutest: ; ./ubuntu-mirror.py $(UBUNTU) test -v $(UBUNTU_REPOS)
ubuntutags: ; ./ubuntu-mirror.py $(UBUNTU) tags -v $(UBUNTU_REPOS)

ubuntubash:
	- docker rm -f ubuntu-bash-$(UBUNTU)
	- docker rm -f ubuntu-repo-$(UBUNTU)
	docker run -d --rm=true --name ubuntu-repo-$(UBUNTU)  $(IMAGESREPO)/ubuntu-repo:$(UBUNTU)
	IP=`docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ubuntu-repo-$(UBUNTU)` ;\
	docker run -d --rm=true --name ubuntu-bash-$(UBUNTU)  --add-host archive.ubuntu.com:$$IP \
                                                             --add-host security.ubuntu.com:$$IP ubuntu:$(UBUNTU) sleep 9999
	docker exec -it ubuntu-bash-$(UBUNTU) bash

### ubuntu versions

ubuntu.21.10: ;	$(MAKE) ubuntudir UBUNTU=21.10
ubuntu.21.04: ;	$(MAKE) ubuntudir UBUNTU=21.04
ubuntu.20.10: ;	$(MAKE) ubuntudir UBUNTU=20.10
ubuntu.20.04: ;	$(MAKE) ubuntudir UBUNTU=20.04
ubuntu.19.10: ;	$(MAKE) ubuntudir UBUNTU=19.10
ubuntu.18.04: ;	$(MAKE) ubuntudir UBUNTU=18.04
ubuntu.16.04: ; $(MAKE) ubuntudir UBUNTU=16.04
ubuntusync.21.10: ; $(MAKE) ubuntusync UBUNTU=21.10
ubuntusync.21.04: ; $(MAKE) ubuntusync UBUNTU=21.04
ubuntusync.20.10: ; $(MAKE) ubuntusync UBUNTU=20.10
ubuntusync.20.04: ; $(MAKE) ubuntusync UBUNTU=20.04
ubuntusync.19.10: ; $(MAKE) ubuntusync UBUNTU=19.10
ubuntusync.18.04: ; $(MAKE) ubuntusync UBUNTU=18.04
ubuntusync.16.04: ; $(MAKE) ubuntusync UBUNTU=16.04
ubunturepo.19.10: ; $(MAKE) ubunturepo UBUNTU=19.10
ubunturepo.18.04: ; $(MAKE) ubunturepo UBUNTU=18.04
ubunturepo.16.04: ; $(MAKE) ubunturepo UBUNTU=16.04
ubuntu-21.10: ; $(MAKE) ubuntu UBUNTU=21.10
ubuntu-21.04: ; $(MAKE) ubuntu UBUNTU=21.04
ubuntu-20.10: ; $(MAKE) ubuntu UBUNTU=20.10
ubuntu-20.04: ; $(MAKE) ubuntu UBUNTU=20.04
ubuntu-19.10: ; $(MAKE) ubuntu UBUNTU=19.10
ubuntu-18.04: ; $(MAKE) ubuntu UBUNTU=18.04
ubuntu-16.04: ; $(MAKE) ubuntu UBUNTU=16.04

universesync: ; $(MAKE) REPOS=universe
universesync.21.10: ; $(MAKE) ubuntusync UBUNTU=21.10 UBUNTU_REPOS=--universe
universesync.21.04: ; $(MAKE) ubuntusync UBUNTU=21.04 UBUNTU_REPOS=--universe
universesync.20.10: ; $(MAKE) ubuntusync UBUNTU=20.10 UBUNTU_REPOS=--universe
universesync.20.04: ; $(MAKE) ubuntusync UBUNTU=20.04 UBUNTU_REPOS=--universe
universesync.19.10: ; $(MAKE) ubuntusync UBUNTU=19.10 UBUNTU_REPOS=--universe
universesync.18.04: ; $(MAKE) ubuntusync UBUNTU=18.04 UBUNTU_REPOS=--universe
universesync.16.04: ; $(MAKE) ubuntusync UBUNTU=16.04 UBUNTU_REPOS=--universe
universerepo.19.10: ; $(MAKE) ubunturepo UBUNTU=19.10 UBUNTU_REPOS=--universe
universerepo.18.04: ; $(MAKE) ubunturepo UBUNTU=18.04 UBUNTU_REPOS=--universe
universerepo.16.04: ; $(MAKE) ubunturepo UBUNTU=16.04 UBUNTU_REPOS=--universe
