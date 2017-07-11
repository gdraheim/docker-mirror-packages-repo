#! /usr/bin/make -f

default: 7.3 # all

7.3: 7.3.1611
7.3.1611: 
	docker build -f centos-repo.$@.dockerfile --tag "localhost:5000/centos-repo:$@" .
7.2: 7.2.1511
7.1: 7.1.1503
7.0: 7.0.1406
6.9:
6.8:
6.7:

all:
	$(MAKE) sync
	$(MAKE) build

sync:
	mkdir tmp
	rsync -r rsync://rsync.hrz.tu-chemnitz/ftp/pub/linux/centos7/os tmp/os --exclude "*.iso"
	rsync -r rsync://rsync.hrz.tu-chemnitz/ftp/pub/linux/centos7/extras tmp/extras
	rsync -r rsync://rsync.hrz.tu-chemnitz/ftp/pub/linux/centos7/updates tmp/updates

CMD = ["python","/srv/scripts/mirrorlist.py","--data","/srv/repo"]
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

check:
	- docker-compose -p testcentos down
	docker-compose -p testcentos up -d
	docker exec testcentos_target_1 yum install -y firefox
	docker-compose -p testcentos down
