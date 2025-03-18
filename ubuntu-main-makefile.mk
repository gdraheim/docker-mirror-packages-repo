#! /usr/bin/make -f

UBUNTU = 22.04
UBUNTU_REPOS ?= --updates
# UNTU_REPOS ?= --universe
# UNTU_REPOS ?= --multiverse

ubuntu:
	$(MAKE) ubuntusync
	$(MAKE) ubunturepo
	$(MAKE) ubuntutest
	$(MAKE) ubuntutags

ubuntusync: ; ./ubuntu-docker-mirror.py $(UBUNTU) sync -v $(UBUNTU_REPOS)
ubuntubase: ; ./ubuntu-docker-mirror.py $(UBUNTU) base -v $(UBUNTU_REPOS)
ubunturepo: ; ./ubuntu-docker-mirror.py $(UBUNTU) repo -v $(UBUNTU_REPOS)
ubuntutest: ; ./ubuntu-docker-mirror.py $(UBUNTU) test -v $(UBUNTU_REPOS)
ubuntutags: ; ./ubuntu-docker-mirror.py $(UBUNTU) tags -v $(UBUNTU_REPOS)

ubuntubash:
	- docker rm -f ubuntu-bash-$(UBUNTU)
	- docker rm -f ubuntu-repo-$(UBUNTU)
	docker run -d --rm=true --name ubuntu-repo-$(UBUNTU)  $(IMAGESREPO)/ubuntu-repo:$(UBUNTU)
	IP=`docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ubuntu-repo-$(UBUNTU)` ;\
	docker run -d --rm=true --name ubuntu-bash-$(UBUNTU)  --add-host archive.ubuntu.com:$$IP \
                                                             --add-host security.ubuntu.com:$$IP ubuntu:$(UBUNTU) sleep 9999
	docker exec -it ubuntu-bash-$(UBUNTU) bash

debiansync.10: ; ./ubuntu-docker-mirror.py debian:10 sync -v 

### ubuntu versions

ubuntusync.24.04: ; $(MAKE) ubuntusync UBUNTU=24.04
ubuntusync.23.10: ; $(MAKE) ubuntusync UBUNTU=23.10
ubuntusync.23.04: ; $(MAKE) ubuntusync UBUNTU=23.04
ubuntusync.22.10: ; $(MAKE) ubuntusync UBUNTU=22.10
ubuntusync.22.04: ; $(MAKE) ubuntusync UBUNTU=22.04
ubuntusync.21.10: ; $(MAKE) ubuntusync UBUNTU=21.10
ubuntusync.21.04: ; $(MAKE) ubuntusync UBUNTU=21.04
ubuntusync.20.10: ; $(MAKE) ubuntusync UBUNTU=20.10
ubuntusync.20.04: ; $(MAKE) ubuntusync UBUNTU=20.04
ubuntusync.19.10: ; $(MAKE) ubuntusync UBUNTU=19.10
ubuntusync.18.04: ; $(MAKE) ubuntusync UBUNTU=18.04
ubuntusync.16.04: ; $(MAKE) ubuntusync UBUNTU=16.04
# -
ubunturepo.24.04: ; $(MAKE) ubunturepo UBUNTU=24.04
ubunturepo.23.10: ; $(MAKE) ubunturepo UBUNTU=23.10
ubunturepo.23.04: ; $(MAKE) ubunturepo UBUNTU=23.04
ubunturepo.22.10: ; $(MAKE) ubunturepo UBUNTU=22.10
ubunturepo.22.04: ; $(MAKE) ubunturepo UBUNTU=22.04
ubunturepo.21.10: ; $(MAKE) ubunturepo UBUNTU=21.10
ubunturepo.21.04: ; $(MAKE) ubunturepo UBUNTU=21.04
ubunturepo.20.10: ; $(MAKE) ubunturepo UBUNTU=20.10
ubunturepo.20.04: ; $(MAKE) ubunturepo UBUNTU=20.04
ubunturepo.19.10: ; $(MAKE) ubunturepo UBUNTU=19.10
ubunturepo.18.04: ; $(MAKE) ubunturepo UBUNTU=18.04
ubunturepo.16.04: ; $(MAKE) ubunturepo UBUNTU=16.04

ubuntu-24.04: ; $(MAKE) ubuntu UBUNTU=24.04
ubuntu-23.10: ; $(MAKE) ubuntu UBUNTU=23.10
ubuntu-23.04: ; $(MAKE) ubuntu UBUNTU=23.04
ubuntu-22.10: ; $(MAKE) ubuntu UBUNTU=22.10
ubuntu-22.04: ; $(MAKE) ubuntu UBUNTU=22.04
ubuntu-21.10: ; $(MAKE) ubuntu UBUNTU=21.10
ubuntu-21.04: ; $(MAKE) ubuntu UBUNTU=21.04
ubuntu-20.10: ; $(MAKE) ubuntu UBUNTU=20.10
ubuntu-20.04: ; $(MAKE) ubuntu UBUNTU=20.04
ubuntu-19.10: ; $(MAKE) ubuntu UBUNTU=19.10
ubuntu-18.04: ; $(MAKE) ubuntu UBUNTU=18.04
ubuntu-16.04: ; $(MAKE) ubuntu UBUNTU=16.04

universesync: ; $(MAKE) REPOS=universe
universesync.24.04: ; $(MAKE) ubuntusync UBUNTU=24.04 UBUNTU_REPOS=--universe
universesync.23.10: ; $(MAKE) ubuntusync UBUNTU=23.10 UBUNTU_REPOS=--universe
universesync.23.04: ; $(MAKE) ubuntusync UBUNTU=23.04 UBUNTU_REPOS=--universe
universesync.22.10: ; $(MAKE) ubuntusync UBUNTU=22.10 UBUNTU_REPOS=--universe
universesync.22.04: ; $(MAKE) ubuntusync UBUNTU=22.04 UBUNTU_REPOS=--universe
universesync.21.10: ; $(MAKE) ubuntusync UBUNTU=21.10 UBUNTU_REPOS=--universe
universesync.21.04: ; $(MAKE) ubuntusync UBUNTU=21.04 UBUNTU_REPOS=--universe
universesync.20.10: ; $(MAKE) ubuntusync UBUNTU=20.10 UBUNTU_REPOS=--universe
universesync.20.04: ; $(MAKE) ubuntusync UBUNTU=20.04 UBUNTU_REPOS=--universe
universesync.19.10: ; $(MAKE) ubuntusync UBUNTU=19.10 UBUNTU_REPOS=--universe
universesync.18.04: ; $(MAKE) ubuntusync UBUNTU=18.04 UBUNTU_REPOS=--universe
universesync.16.04: ; $(MAKE) ubuntusync UBUNTU=16.04 UBUNTU_REPOS=--universe
# -
universerepo.24.04: ; $(MAKE) ubunturepo UBUNTU=24.04 UBUNTU_REPOS=--universe
universerepo.23.10: ; $(MAKE) ubunturepo UBUNTU=23.10 UBUNTU_REPOS=--universe
universerepo.23.04: ; $(MAKE) ubunturepo UBUNTU=23.04 UBUNTU_REPOS=--universe
universerepo.22.10: ; $(MAKE) ubunturepo UBUNTU=22.10 UBUNTU_REPOS=--universe
universerepo.22.04: ; $(MAKE) ubunturepo UBUNTU=22.04 UBUNTU_REPOS=--universe
universerepo.21.10: ; $(MAKE) ubunturepo UBUNTU=21.10 UBUNTU_REPOS=--universe
universerepo.21.04: ; $(MAKE) ubunturepo UBUNTU=21.04 UBUNTU_REPOS=--universe
universerepo.20.10: ; $(MAKE) ubunturepo UBUNTU=20.10 UBUNTU_REPOS=--universe
universerepo.20.04: ; $(MAKE) ubunturepo UBUNTU=20.04 UBUNTU_REPOS=--universe
universerepo.19.10: ; $(MAKE) ubunturepo UBUNTU=19.10 UBUNTU_REPOS=--universe
universerepo.18.04: ; $(MAKE) ubunturepo UBUNTU=18.04 UBUNTU_REPOS=--universe
universerepo.16.04: ; $(MAKE) ubunturepo UBUNTU=16.04 UBUNTU_REPOS=--universe

# docker_mirror.ini shallow starts
ubuntubase.24.04: ; $(MAKE) ubuntubase UBUNTU=24.04
ubuntubase.23.10: ; $(MAKE) ubuntubase UBUNTU=23.10
ubuntubase.23.04: ; $(MAKE) ubuntubase UBUNTU=23.04
ubuntubase.22.10: ; $(MAKE) ubuntubase UBUNTU=22.10
ubuntubase.22.04: ; $(MAKE) ubuntubase UBUNTU=22.04
ubuntubase.21.10: ; $(MAKE) ubuntubase UBUNTU=21.10
ubuntubase.21.04: ; $(MAKE) ubuntubase UBUNTU=21.04
ubuntubase.20.10: ; $(MAKE) ubuntubase UBUNTU=20.10
ubuntubase.20.04: ; $(MAKE) ubuntubase UBUNTU=20.04
ubuntubase.19.10: ; $(MAKE) ubuntubase UBUNTU=19.10
ubuntubase.18.04: ; $(MAKE) ubuntubase UBUNTU=18.04
ubuntubase.16.04: ; $(MAKE) ubuntubase UBUNTU=16.04

ubuntudisk.24.04: ; ./ubuntu-docker-mirror.py 24.04 disk -v --universe
ubuntudisk.22.04: ; ./ubuntu-docker-mirror.py 22.04 disk -v --universe
ubuntudisk.20.04: ; ./ubuntu-docker-mirror.py 20.04 disk -v --universe
ubuntudisk.18.04: ; ./ubuntu-docker-mirror.py 18.04 disk -v --universe
ubuntudisk.16.04: ; ./ubuntu-docker-mirror.py 16.04 disk -v --universe

ubuntudu.24.04: ; ./ubuntu-docker-mirror.py 24.04 du -v
ubuntudu.22.04: ; ./ubuntu-docker-mirror.py 22.04 du -v
ubuntudu.20.04: ; ./ubuntu-docker-mirror.py 20.04 du -v
ubuntudu.18.04: ; ./ubuntu-docker-mirror.py 18.04 du -v
ubuntudu.16.04: ; ./ubuntu-docker-mirror.py 16.04 du -v
