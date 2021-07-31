#! /usr/bin/make -f

UBUNTU = 20.04

ubuntu:
	$(MAKE) ubuntusync
	$(MAKE) ubunturepo
	$(MAKE) ubuntutest
	$(MAKE) ubuntutags

ubuntusync: ; ./ubuntu-mirror.py $(UBUNTU) sync -v
ubunturepo: ; ./ubuntu-mirror.py $(UBUNTU) repo -v
ubuntutest: ; ./ubuntu-mirror.py $(UBUNTU) test -v
ubuntutags: ; ./ubuntu-mirror.py $(UBUNTU) tags -v

ubuntubash:
	- docker rm -f ubuntu-bash-$(UBUNTU)
	- docker rm -f ubuntu-repo-$(UBUNTU)
	docker run -d --rm=true --name ubuntu-repo-$(UBUNTU)  $(IMAGESREPO)/ubuntu-repo:$(UBUNTU)
	IP=`docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ubuntu-repo-$(UBUNTU)` ;\
	docker run -d --rm=true --name ubuntu-bash-$(UBUNTU)  --add-host archive.ubuntu.com:$$IP \
                                                             --add-host security.ubuntu.com:$$IP ubuntu:$(UBUNTU) sleep 9999
	docker exec -it ubuntu-bash-$(UBUNTU) bash
