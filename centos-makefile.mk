#! /usr/bin/make -f

############## SYNC VARIANT ############
# this is faster and it is more robust #
# however it doubles the required disk #
# space to get a centos-repo:x image!! #

CENTOS = 8.3

centos:
	$(MAKE) centossync
	$(MAKE) centospull
	$(MAKE) centosrepo
	$(MAKE) centostest
	$(MAKE) centoscheck
	$(MAKE) centostags

centoshelp: ; ./centos-mirror.py $(CENTOS) --help
centospull: ; ./centos-mirror.py $(CENTOS) pull -v
centossync: ; ./centos-mirror.py $(CENTOS) sync -v
centosrepo: ; ./centos-mirror.py $(CENTOS) repo -v
centostest: ; ./centos-mirror.py $(CENTOS) test -v
centoscheck: ; ./centos-mirror.py $(CENTOS) check -v
centostags: ; ./centos-mirror.py $(CENTOS) tags -v
centos-clean: ; ./centos-mirror.py $(CENTOS) clean -v

centosbash:
	- docker rm -f centos-bash-$(CENTOS)
	- docker rm -f centos-repo-$(CENTOS)
	docker run -d --rm=true --name centos-repo-$(CENTOS)  $(IMAGESREPO)/centos-repo:$(CENTOS)
	IP=`docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' centos-repo-$(CENTOS)` ;\
	docker run -d --rm=true --name centos-bash-$(CENTOS)  --add-host mirrorlist.centos.org:$$IP centos:$(CENTOS) sleep 999
	docker exec -it centos-bash-$(CENTOS) bash
