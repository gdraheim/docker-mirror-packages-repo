#! /usr/bin/make -f

############## SYNC VARIANT ############
# this is faster and it is more robust #
# however it doubles the required disk #
# space to get a centos-repo:x image!! #

ALMALINUX = 9.4
CENTOS = 8.4
DISTRO = centos

centos:
	$(MAKE) centossync
	$(MAKE) centospull
	$(MAKE) centosrepo
	$(MAKE) centostest
	$(MAKE) centoscheck
	$(MAKE) centostags

centoshelp: ; ./centos-docker-mirror.py $(CENTOS) --help
centospull: ; ./centos-docker-mirror.py $(CENTOS) pull -v
centossync: ; ./centos-docker-mirror.py -V $(DISTRO):$(CENTOS) sync -v
centosrepo: ; ./centos-docker-mirror.py $(CENTOS) repo -v
centosdisk: ; ./centos-docker-mirror.py $(CENTOS) disk -v
centosbase: ; ./centos-docker-mirror.py $(CENTOS) base -v
centostest: ; ./centos-docker-mirror.py $(CENTOS) test -v
centoscheck: ; ./centos-docker-mirror.py $(CENTOS) check -v
centostags: ; ./centos-docker-mirror.py $(CENTOS) tags -v
centos-clean: ; ./centos-docker-mirror.py $(CENTOS) clean -v

centosbash:
	- docker rm -f centos-bash-$(CENTOS)
	- docker rm -f centos-repo-$(CENTOS)
	docker run -d --rm=true --name centos-repo-$(CENTOS)  $(IMAGESREPO)/centos-repo:$(CENTOS)
	IP=`docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' centos-repo-$(CENTOS)` ;\
	docker run -d --rm=true --name centos-bash-$(CENTOS)  --add-host mirrorlist.centos.org:$$IP centos:$(CENTOS) sleep 999
	docker exec -it centos-bash-$(CENTOS) bash

### centos versions
almapull.9.1: ; $(MAKE) centospull CENTOS=$(ALMALINUX) DISTRO=almalinux

almasync.9.5: ; $(MAKE) centossync CENTOS=9.5 DISTRO=almalinux
almarepo.9.5: ; $(MAKE) centosrepo CENTOS=9.5 DISTRO=almalinux
almasync.9.4: ; $(MAKE) centossync CENTOS=9.4 DISTRO=almalinux
almarepo.9.4: ; $(MAKE) centosrepo CENTOS=9.4 DISTRO=almalinux
almasync.9.3: ; $(MAKE) centossync CENTOS=9.3 DISTRO=almalinux
almarepo.9.3: ; $(MAKE) centosrepo CENTOS=9.3 DISTRO=almalinux
almasync.9.2: ; $(MAKE) centossync CENTOS=9.2 DISTRO=almalinux
almarepo.9.2: ; $(MAKE) centosrepo CENTOS=9.2 DISTRO=almalinux
almasync.9.1: ; $(MAKE) centossync CENTOS=9.1 DISTRO=almalinux
almarepo.9.1: ; $(MAKE) centosrepo CENTOS=9.1 DISTRO=almalinux
centossync.8.5 centossync.8.5.2111: ; $(MAKE) centossync CENTOS=8.5.2111
centossync.8.4 centossync.8.4.2105: ; $(MAKE) centossync CENTOS=8.4.2105
centossync.8.3 centossync.8.2.2011: ; $(MAKE) centossync CENTOS=8.3.2011
centossync.8.2 centossync.8.2.2004: ; $(MAKE) centossync CENTOS=8.2.2004
centossync.8.1 centossync.8.1.1911: ; $(MAKE) centossync CENTOS=8.1.1911
centossync.8.0 centossync.8.0.1905: ; $(MAKE) centossync CENTOS=8.0.1905
centossync.7.9 centossync.7.9.2009: ; $(MAKE) centossync CENTOS=7.9.2009
centossync.7.8 centossync.7.8.2003: ; $(MAKE) centossync CENTOS=7.8.2003
centossync.7.7 centossync.7.7.1908: ; $(MAKE) centossync CENTOS=7.7.1908
centossync.7.6 centossync.7.6.1810: ; $(MAKE) centossync CENTOS=7.6.1810
centossync.7.5 centossync.7.5.1804: ; $(MAKE) centossync CENTOS=7.5.1804
centossync.7.4 centossync.7.4.1708: ; $(MAKE) centossync CENTOS=7.4.1708
centossync.7.3 centossync.7.3.1611: ; $(MAKE) centossync CENTOS=7.3.1611
centosrepo.8.5 centosrepo.8.5.2111: ; $(MAKE) centosrepo CENTOS=8.5.2111 centostags
centosrepo.8.4 centosrepo.8.4.2105: ; $(MAKE) centosrepo CENTOS=8.4.2105 centostags
centosrepo.8.3 centosrepo.8.3.2011: ; $(MAKE) centosrepo CENTOS=8.3.2011 centostags
centosrepo.8.2 centosrepo.8.2.2004: ; $(MAKE) centosrepo CENTOS=8.2.2004 centostags
centosrepo.8.1 centosrepo.8.1.1911: ; $(MAKE) centosrepo CENTOS=8.1.1911 centostags
centosrepo.8.0 centosrepo.8.0.1905: ; $(MAKE) centosrepo CENTOS=8.0.1905 centostags
centosrepo.7.9 centosrepo.7.9.2009: ; $(MAKE) centosrepo CENTOS=7.9.2009 centostags
centosrepo.7.8 centosrepo.7.8.2003: ; $(MAKE) centosrepo CENTOS=7.8.2003 centostags
centosrepo.7.7 centosrepo.7.7.1908: ; $(MAKE) centosrepo CENTOS=7.7.1908 centostags
centosrepo.7.6 centosrepo.7.6.1810: ; $(MAKE) centosrepo CENTOS=7.6.1810 centostags
centosrepo.7.5 centosrepo.7.5.1804: ; $(MAKE) centosrepo CENTOS=7.5.1804 centostags
centosrepo.7.4 centosrepo.7.4.1708: ; $(MAKE) centosrepo CENTOS=7.4.1708 centostags
centosrepo.7.3 centosrepo.7.3.1611: ; $(MAKE) centosrepo CENTOS=7.3.1611 centostags
centos-8.5 centos-8.4.2111: ; $(MAKE) centos CENTOS=8.5.2111
centos-8.4 centos-8.4.2105: ; $(MAKE) centos CENTOS=8.4.2105
centos-8.3 centos-8.3.2011: ; $(MAKE) centos CENTOS=8.3.2011
centos-8.2 centos-8.2.2004: ; $(MAKE) centos CENTOS=8.2.2004
centos-8.1 centos-8.1.1911: ; $(MAKE) centos CENTOS=8.1.1911
centos-8.0 centos-8.0.1905: ; $(MAKE) centos CENTOS=8.0.1905
centos-7.9 centos-7.9.2009: ; $(MAKE) centos CENTOS=7.9.2009
centos-7.8 centos-7.8.2003: ; $(MAKE) centos CENTOS=7.8.2003
centos-7.7 centos-7.7.1908: ; $(MAKE) centos CENTOS=7.7.1908
centos-7.6 centos-7.6.1810: ; $(MAKE) centos CENTOS=7.6.1810
centos-7.5 centos-7.5.1804: ; $(MAKE) centos CENTOS=7.5.1804
centos-7.4 centos-7.4.1708: ; $(MAKE) centos CENTOS=7.4.1708
centos-7.3 centos-7.3.1611: ; $(MAKE) centos CENTOS=7.3.1611

centosdisk.8.5 centosdisk.8.5.2111: ; $(MAKE) centosdisk CENTOS=8.5.2111 
centosdisk.8.4 centosdisk.8.4.2105: ; $(MAKE) centosdisk CENTOS=8.4.2105 
centosdisk.8.3 centosdisk.8.3.2011: ; $(MAKE) centosdisk CENTOS=8.3.2011 
centosdisk.8.2 centosdisk.8.2.2004: ; $(MAKE) centosdisk CENTOS=8.2.2004 
centosdisk.8.1 centosdisk.8.1.1911: ; $(MAKE) centosdisk CENTOS=8.1.1911 
centosdisk.8.0 centosdisk.8.0.1905: ; $(MAKE) centosdisk CENTOS=8.0.1905 
centosdisk.7.9 centosdisk.7.9.2009: ; $(MAKE) centosdisk CENTOS=7.9.2009 
centosdisk.7.8 centosdisk.7.8.2003: ; $(MAKE) centosdisk CENTOS=7.8.2003 
centosdisk.7.7 centosdisk.7.7.1908: ; $(MAKE) centosdisk CENTOS=7.7.1908 
centosdisk.7.6 centosdisk.7.6.1810: ; $(MAKE) centosdisk CENTOS=7.6.1810 
centosdisk.7.5 centosdisk.7.5.1804: ; $(MAKE) centosdisk CENTOS=7.5.1804 
centosdisk.7.4 centosdisk.7.4.1708: ; $(MAKE) centosdisk CENTOS=7.4.1708 
centosdisk.7.3 centosdisk.7.3.1611: ; $(MAKE) centosdisk CENTOS=7.3.1611 
centosbase.8.5 centosbase.8.5.2111: ; $(MAKE) centosbase CENTOS=8.5.2111 
centosbase.8.4 centosbase.8.4.2105: ; $(MAKE) centosbase CENTOS=8.4.2105 
centosbase.8.3 centosbase.8.3.2011: ; $(MAKE) centosbase CENTOS=8.3.2011 
centosbase.8.2 centosbase.8.2.2004: ; $(MAKE) centosbase CENTOS=8.2.2004 
centosbase.8.1 centosbase.8.1.1911: ; $(MAKE) centosbase CENTOS=8.1.1911 
centosbase.8.0 centosbase.8.0.1905: ; $(MAKE) centosbase CENTOS=8.0.1905 
centosbase.7.9 centosbase.7.9.2009: ; $(MAKE) centosbase CENTOS=7.9.2009 
centosbase.7.8 centosbase.7.8.2003: ; $(MAKE) centosbase CENTOS=7.8.2003 
centosbase.7.7 centosbase.7.7.1908: ; $(MAKE) centosbase CENTOS=7.7.1908 
centosbase.7.6 centosbase.7.6.1810: ; $(MAKE) centosbase CENTOS=7.6.1810 
centosbase.7.5 centosbase.7.5.1804: ; $(MAKE) centosbase CENTOS=7.5.1804 
centosbase.7.4 centosbase.7.4.1708: ; $(MAKE) centosbase CENTOS=7.4.1708 
centosbase.7.3 centosbase.7.3.1611: ; $(MAKE) centosbase CENTOS=7.3.1611 

almadisk.9.5: ; $(MAKE) centosdisk CENTOS=9.5 DISTRO=almalinux
almabase.9.5: ; $(MAKE) centosbase CENTOS=9.5 DISTRO=almalinux
almadisk.9.4: ; $(MAKE) centosdisk CENTOS=9.4 DISTRO=almalinux
almabase.9.4: ; $(MAKE) centosbase CENTOS=9.4 DISTRO=almalinux
almadisk.9.3: ; $(MAKE) centosdisk CENTOS=9.3 DISTRO=almalinux
almabase.9.3: ; $(MAKE) centosbase CENTOS=9.3 DISTRO=almalinux
almadisk.9.2: ; $(MAKE) centosdisk CENTOS=9.2 DISTRO=almalinux
almabase.9.2: ; $(MAKE) centosbase CENTOS=9.2 DISTRO=almalinux
almadisk.9.1: ; $(MAKE) centosdisk CENTOS=9.1 DISTRO=almalinux
almabase.9.1: ; $(MAKE) centosbase CENTOS=9.1 DISTRO=almalinux
