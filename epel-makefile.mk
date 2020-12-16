#! /usr/bin/make -f

epel:
	$(MAKE) epeldir
	$(MAKE) epelsync
	$(MAKE) epelrepo

epeldir:  ; ./centos-mirror.py 7 epeldir
epelsync: ; ./centos-mirror.py 7 epelsync
epelrepo: ; ./centos-mirror.py 7 epelrepo

# centos:8.0.1905 does refer to epel-repo:7, so until the end of 2019 we tag it also as epel-repo:8
