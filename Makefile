#! /usr/bin/make -f

B= 2018
FOR=today

VERSIONFILES = *.py */*.py *.cfg
version1:
	@ grep -l __version__ $(VERSIONFILES)  | { while read f; do echo $$f; done; } 

version:
	@ grep -l __version__ $(VERSIONFILES) | { while read f; do : \
	; Y=`date +%Y -d "$(FOR)"` ; X=$$(expr $$Y - $B); D=`date +%W%u -d "$(FOR)"` ; sed -i \
	-e "/^version *=/s/[.]-*[0123456789][0123456789][0123456789]*\$$/.$$X$$D\"/" \
	-e "/^version *=/s/[.]\\([0123456789]\\)\$$/.\\1.$$X$$D/" \
	-e "/^ *__version__/s/[.]-*[0123456789][0123456789][0123456789]*\"/.$$X$$D\"/" \
	-e "/^ *__version__/s/[.]\\([0123456789]\\)\"/.\\1.$$X$$D\"/" \
	-e "/^ *__copyright__/s/(C) [0123456789]*-[0123456789]*/(C) $B-$$Y/" \
	-e "/^ *__copyright__/s/(C) [0123456789]* /(C) $$Y /" \
	$$f; done; }
	@ grep ^__version__ $(VERSIONFILES)


include centos-makefile.mk
include opensuse-makefile.mk
include ubuntu-makefile.mk
include epel-makefile.mk

epel.7: ; $(MAKE) epeldir EPEL=7
epel.8: ; $(MAKE) epeldir EPEL=8
epelsync.7: ; $(MAKE) epelsync EPEL=7
epelsync.8: ; $(MAKE) epelsync EPEL=8
epelrepo.7: ; $(MAKE) epelrepo EPEL=7
epelrepo.8: ; $(MAKE) epelrepo EPEL=8
epel-7: ; $(MAKE) epel EPEL=7
epel-8: ; $(MAKE) epel EPEL=8

centos.8.3 centos.8.3.2011: ; $(MAKE) centosdir CENTOS=8.3.2011
centos.8.2 centos.8.2.2004: ; $(MAKE) centosdir CENTOS=8.2.2004
centos.8.1 centos.8.1.1911: ; $(MAKE) centosdir CENTOS=8.1.1911
centos.8.0 centos.8.0.1905: ; $(MAKE) centosdir CENTOS=8.0.1905
centos.7.9 centos.7.9.2009: ; $(MAKE) centosdir CENTOS=7.9.2009
centos.7.8 centos.7.8.2003: ; $(MAKE) centosdir CENTOS=7.8.2003
centos.7.7 centos.7.7.1908: ; $(MAKE) centosdir CENTOS=7.7.1908
centos.7.6 centos.7.6.1810: ; $(MAKE) centosdir CENTOS=7.6.1810
centos.7.5 centos.7.5.1804: ; $(MAKE) centosdir CENTOS=7.5.1804
centos.7.4 centos.7.4.1708: ; $(MAKE) centosdir CENTOS=7.4.1708
centos.7.3 centos.7.3.1611: ; $(MAKE) centosdir CENTOS=7.3.1611
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
centosrepo.8.3 centosrepo.8.3.2011: ; $(MAKE) centosrepo CENTOS=8.3.2011 centostags
centosrepo.8.2 centosrepo.8.2.2004: ; $(MAKE) centosrepo CENTOS=8.2.2004 centostags
centosrepo.8.1 centosrepo.8.1.1911: ; $(MAKE) centosrepo CENTOS=8.1.1911 centostags
centosrepo.8.0 centosrepo.8.0.1905: ; $(MAKE) centosrepo CENTOS=8.0.1905 centostags
centosrepo.7.7 centosrepo.7.7.1908: ; $(MAKE) centosrepo CENTOS=7.7.1908 centostags
centosrepo.7.6 centosrepo.7.6.1810: ; $(MAKE) centosrepo CENTOS=7.6.1810 centostags
centosrepo.7.5 centosrepo.7.5.1804: ; $(MAKE) centosrepo CENTOS=7.5.1804 centostags
centosrepo.7.4 centosrepo.7.4.1708: ; $(MAKE) centosrepo CENTOS=7.4.1708 centostags
centosrepo.7.3 centosrepo.7.3.1611: ; $(MAKE) centosrepo CENTOS=7.3.1611 centostags
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

opensuse.15.2: ; $(MAKE) opensusedir LEAP=15.2
opensuse.15.1: ; $(MAKE) opensusedir LEAP=15.1
opensuse.15.0: ; $(MAKE) opensusedir LEAP=15.0
opensuse.42.3: ; $(MAKE) opensusedir LEAP=42.3
opensuse.42.2: ; $(MAKE) opensusedir LEAP=42.2
opensusesync.15.2: ; $(MAKE) opensusesync LEAP=15.2
opensusesync.15.1: ; $(MAKE) opensusesync LEAP=15.1
opensusesync.15.0: ; $(MAKE) opensusesync LEAP=15.0
opensusesync.42.3: ; $(MAKE) opensusesync LEAP=42.3
opensuserepo.15.2: ; $(MAKE) opensuserepo LEAP=15.2 OPENSUSE=opensuse/leap
opensuserepo.15.1: ; $(MAKE) opensuserepo LEAP=15.1 OPENSUSE=opensuse/leap
opensuserepo.15.0: ; $(MAKE) opensuserepo LEAP=15.0 OPENSUSE=opensuse/leap
opensuserepo.42.3: ; $(MAKE) opensuserepo LEAP=42.3 OPENSUSE=opensuse
opensuse-15.2: ; $(MAKE) opensuse LEAP=15.2 OPENSUSE=opensuse/leap
opensuse-15.1: ; $(MAKE) opensuse LEAP=15.1 OPENSUSE=opensuse/leap
opensuse-15.0: ; $(MAKE) opensuse LEAP=15.0 OPENSUSE=opensuse/leap
opensuse-42.3: ; $(MAKE) opensuse LEAP=42.3 OPENSUSE=opensuse
opensuse-42.2: ; $(MAKE) opensuse LEAP=42.2 OPENSUSE=opensuse

ubuntu.19.10: ;	$(MAKE) ubuntudir UBUNTU=19.10
ubuntu.18.04: ;	$(MAKE) ubuntudir UBUNTU=18.04
ubuntu.16.04: ; $(MAKE) ubuntudir UBUNTU=16.04
ubuntusync.19.10: ; $(MAKE) ubuntusync UBUNTU=19.10 REPOS=updates
ubuntusync.18.04: ; $(MAKE) ubuntusync UBUNTU=18.04 REPOS=updates
ubuntusync.16.04: ; $(MAKE) ubuntusync UBUNTU=16.04 REPOS=updates
ubunturepo.19.10: ; $(MAKE) ubunturepo UBUNTU=19.10 REPOS=updates
ubunturepo.18.04: ; $(MAKE) ubunturepo UBUNTU=18.04 REPOS=updates
ubunturepo.16.04: ; $(MAKE) ubunturepo UBUNTU=16.04 REPOS=updates
ubuntu-19.10: ; $(MAKE) ubuntu UBUNTU=19.10
ubuntu-18.04: ; $(MAKE) ubuntu UBUNTU=18.04
ubuntu-16.04: ; $(MAKE) ubuntu UBUNTU=16.04

universesync: ; $(MAKE) REPOS=universe
universesync.19.10: ; $(MAKE) ubuntusync UBUNTU=19.10 REPOS=universe
universesync.18.04: ; $(MAKE) ubuntusync UBUNTU=18.04 REPOS=universe
universesync.16.04: ; $(MAKE) ubuntusync UBUNTU=16.04 REPOS=universe
universerepo.19.10: ; $(MAKE) ubunturepo UBUNTU=19.10 REPOS=universe
universerepo.18.04: ; $(MAKE) ubunturepo UBUNTU=18.04 REPOS=universe
universerepo.16.04: ; $(MAKE) ubunturepo UBUNTU=16.04 REPOS=universe

K=
test_%: ; ./testsuite.py $@ -v $K
check: ; ./testsuite.py -vv $K

mypy:
	zypper install -y mypy
	zypper install -y python3-click python3-pathspec
	cd .. && git clone git@github.com:ambv/retype.git
	cd ../retype && git checkout 17.12.0

type: 
	$(MAKE) type.r type.d type.f type.m type.e
type.r:
	mypy --strict centos-mirror.py opensuse-mirror.py ubuntu-mirror.py
	- rm -rf .mypy_cache
type.d:
	python3 ../retype/retype.py docker_mirror.py -t docker_mirror.tmp -p .
	mypy --strict docker_mirror.tmp/docker_mirror.py
	- rm -rf .mypy_cache
type.f:
	python3 ../retype/retype.py scripts/filelist.py -t scripts.tmp -p scripts
	mypy --strict scripts.tmp/filelist.py
	- rm -rf .mypy_cache
type.m:
	python3 ../retype/retype.py scripts/mirrorlist.py -t scripts.tmp -p scripts
	mypy --strict scripts.tmp/mirrorlist.py
	- rm -rf .mypy_cache
type.e:
	python3 ../retype/retype.py scripts/mirrors.fedoraproject.org.py -t scripts.tmp -p scripts
	mypy --strict scripts.tmp/mirrors.fedoraproject.org.py
	- rm -rf .mypy_cache
pep style: 
	$(MAKE) pep.d pep.r pep.s
pep.i style.i: 
	$(MAKE) pep.d.i pep.r.i pep.s.i
pep.d style.d     pep.d.diff style.d.diff:
	autopep8 docker_mirror.py --diff
pep.d.i style.d.i pep.d.apply style.d.apply:
	autopep8 docker_mirror.py --in-place
	git diff docker_mirror.py
pep.r style.r     pep.r.diff style.r.diff:
	autopep8 centos-mirror.py opensuse-mirror.py ubuntu-mirror.py --diff
pep.r.i style.r.i pep.r.apply style.r.apply:
	autopep8 centos-mirror.py opensuse-mirror.py ubuntu-mirror.py --in-place
	git diff centos-mirror.py opensuse-mirror.py ubuntu-mirror.py
pep.s style.s     pep.s.diff style.s.diff:
	autopep8 scripts/*.py --diff
pep.s.i style.s.i pep.s.apply style.s.apply:
	autopep8 scripts/*.py --in-place
	git diff scripts/*.py
