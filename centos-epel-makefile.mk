#! /usr/bin/make -f

EPEL = 9

epel:
	$(MAKE) epeldir
	$(MAKE) epelsync
	$(MAKE) epelrepo

epeldir:  ; ./centos-docker-mirror.py $(EPEL) epeldir
epelsync: ; ./centos-docker-mirror.py $(EPEL) epelsync
epelrepo: ; ./centos-docker-mirror.py $(EPEL) epelrepo

# centos:8.0.1905 does refer to epel-repo:7, so until the end of 2019 we tag it also as epel-repo:8

### epel versions

epel.7: ; $(MAKE) epeldir EPEL=7
epel.8: ; $(MAKE) epeldir EPEL=8
epel.9: ; $(MAKE) epeldir EPEL=9
epelsync.7: ; $(MAKE) epelsync EPEL=7
epelsync.8: ; $(MAKE) epelsync EPEL=8
epelsync.9: ; $(MAKE) epelsync EPEL=9
epelrepo.7: ; $(MAKE) epelrepo EPEL=7
epelrepo.8: ; $(MAKE) epelrepo EPEL=8
epelrepo.9: ; $(MAKE) epelrepo EPEL=9
epel-7: ; $(MAKE) epel EPEL=7
epel-8: ; $(MAKE) epel EPEL=8
epel-9: ; $(MAKE) epel EPEL=9
