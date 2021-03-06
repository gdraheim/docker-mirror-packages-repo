#! /usr/bin/make -f

EPEL = 8

epel:
	$(MAKE) epeldir
	$(MAKE) epelsync
	$(MAKE) epelrepo

epeldir:  ; ./centos-mirror.py $(EPEL) epeldir
epelsync: ; ./centos-mirror.py $(EPEL) epelsync
epelrepo: ; ./centos-mirror.py $(EPEL) epelrepo

# centos:8.0.1905 does refer to epel-repo:7, so until the end of 2019 we tag it also as epel-repo:8
