#! /usr/bin/make -f

IMAGESREPO ?= localhost:5000/mirror-packages

EPELDATADIRS= $(REPODATADIR) /srv/docker-mirror-packages /data/docker-mirror-packages /data/docker-centos-repo-mirror /dock/docker-mirror-packages
EPEL = 7
BASEARCH = x86_64

##### basearch=x86_64
###baseurl=http://download.fedoraproject.org/pub/epel/7/$basearch
##metalink=https://mirrors.fedoraproject.org/metalink?repo=epel-7&arch=$basearch
#  http://fedora.tu-chemnitz.de/pub/linux/fedora-epel/7/x86_64/debug/repodata/repomd.xml
# rsync://fedora.tu-chemnitz.de/ftp/pub/linux/fedora-epel/7/x86_64/debug/repodata/repomd.xml
EPEL_MIRROR = rsync://fedora.tu-chemnitz.de/ftp/pub/linux/fedora-epel

epel:
	$(MAKE) epeldir
	$(MAKE) epelsync
epeldir:
	@ test ! -d epel.$(EPEL) || rmdir -v epel.$(EPEL) || rm -v epel.$(EPEL)
	@ for data in $(EPELDATADIRS); do : \
	; echo .. check $$data \
	; if test -d $$data; then : \
	; test -d  $$data/epel.$(EPEL) \
	|| mkdir -v $$data/epel.$(EPEL) \
	; ln -svf   $$data/epel.$(EPEL) . \
	; fi; done ; true
	@ if test -d epel.$(EPEL)/. ; then : \
	; else mkdir -v epel.$(EPEL) ; fi
	ls -ld epel.$(EPEL)

XXX_EPEL = --exclude "*.iso"
epelsync: 
	$(MAKE) epeldir
	test -d epel.$(EPEL)/$(EPEL) || mkdir epel.$(EPEL)/$(EPEL)
	rsync -rv $(EPEL_MIRROR)/$(EPEL)/$(BASEARCH)  epel.$(EPEL)/$(EPEL)/ $(XXX_EPEL)
