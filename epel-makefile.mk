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
	$(MAKE) epelrepo
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

## [[centos:8]]
## [/etc/yum.repos.d/CentOS-Base.repo]
## mirrorlist=http://mirrorlist.centos.org/?release=$releasever&arch=$basearch&repo=BaseOS&infra=$infra
## #baseurl=http://mirror.centos.org/$contentdir/$releasever/BaseOS/$basearch/os/
## [/etc/yum.repos.d/epel.repo]
## #baseurl=https://download.fedoraproject.org/pub/epel/$releasever/Everything/$basearch
## metalink=https://mirrors.fedoraproject.org/metalink?repo=epel-$releasever&arch=$basearch&infra=$infra&content=$contentdir

## [[centos:7]]
## [/etc/yum.repos.d/CentOS-Base.repo]
## mirrorlist=http://mirrorlist.centos.org/?release=$releasever&arch=$basearch&repo=os&infra=$infra
## #baseurl=http://mirror.centos.org/centos/$releasever/os/$basearch/
## [/etc/yum.repos.d/epel.repo]
## #baseurl=https://download.fedoraproject.org/pub/epel/7/$basearch
## metalink=https://mirrors.fedoraproject.org/metalink?repo=epel-7&arch=$basearch

# both of /usr/lib/python2.7/site-packages/yum/yumRepo.py and libdnf/repo/Repo.cpp rely
# on curl/libcurl to download metalink data - which rejects a self-signed certificate.
# Therefore you need to run "sed -i -e s/https:/http:/ /etc/yum.repos.d/epel.repo" 
# after any "yum install epel-release". The original mirrors.fedora is fine with that.

epelrepo_port = 443
epelrepo_cmd = ["python","/srv/scripts/mirrors.fedoraproject.org.py","--data","/srv/repo/epel", "--ssl", "https://mirrors.fedoraproject.org"]
epelrepo_PORT = 80
epelrepo_CMD = ["python","/srv/scripts/mirrors.fedoraproject.org.py","--data","/srv/repo/epel"]
epelrepo:
	- docker rm --force $@
	docker run --name=$@ --detach centos:$(EPEL) sleep 9999
	docker exec $@ mkdir -p /srv/repo/epel
	docker exec $@ yum install -y openssl
	case $(EPEL) in 8*) : ;; *) exit 0 ;; esac ;\
	docker exec $@ yum install -y python2 &&\
	docker exec $@ ln -sv /usr/bin/python2 /usr/bin/python
	docker cp scripts $@:/srv/scripts
	docker cp epel.$(EPEL)/$(EPEL) $@:/srv/repo/epel/
	docker commit -c 'CMD $($@_CMD)' -c 'EXPOSE $($@_PORT)' $@ $(IMAGESREPO)/epel-repo:$(EPEL)
	docker tag $(IMAGESREPO)/epel-repo:$(EPEL) $(IMAGESREPO)/epel-repo:$(EPEL).x.`date '+%y%m'`
	- [ "7" != "$(EPEL)" ] || [ "19" != `date +%y` ] ||\
	docker tag $(IMAGESREPO)/epel-repo:$(EPEL) $(IMAGESREPO)/epel-repo:8.x.`date '+%y%m'`
	docker rm --force $@

# centos:8.0.1905 does refer to epel-repo:7, so until the end of 2019 we tag it also as epel-repo:8

