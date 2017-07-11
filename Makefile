#! /usr/bin/make -f

all:
	$(MAKE) sync
	$(MAKE) build

sync:
	mkdir tmp
	rsync -r rsync://rsync.hrz.tu-chemnitz/ftp/pub/linux/centos7/os tmp/os --exclude "*.iso"
	rsync -r rsync://rsync.hrz.tu-chemnitz/ftp/pub/linux/centos7/extras tmp/extras
	rsync -r rsync://rsync.hrz.tu-chemnitz/ftp/pub/linux/centos7/updates tmp/updates

CMD = "cd /srv/repo && /srv/scripts/mirrorlist.py"
build:
	- docker rm --force centos
	docker run --name=centos --detach centos:centos7 sleep 9999
	docker exec centos mkdir -p /srv/repo/7
	docker cp scripts centos:/srv/scripts
	docker cp tmp/os centos:/srv/repo/7/os
	docker cp tmp/extras centos:/srv/repo/7/extras
	docker cp tmp/updates centos:/srv/repo/7/updates
	docker commit -c 'CMD $(CMD)' centos localhost:5000/centos-repo:7
	docker rm --force centos
