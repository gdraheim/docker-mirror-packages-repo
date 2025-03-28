#! /usr/bin/make -f

B= 2018
FOR=today

VERSIONFILES = *.py */*.py *.cfg
version1:
	@ grep -l __version__ $(VERSIONFILES)  | { while read f; do echo $$f; done; } 

version:
	@ grep -l __version__ $(VERSIONFILES) | { while read f; do : \
	; Y=`date +%Y -d "$(FOR)"` ; X=$$(expr $$Y - $B); D=`date +%W%u -d "$(FOR)"` ; sed -i \
	-e "/^version *=/s/[.]-*[0123456789][0123456789][0123456789]*\$$/.$$X$$D/" \
	-e "/^version *=/s/[.]\\([0123456789]\\)\$$/.\\1.$$X$$D/" \
	-e "/^ *__version__/s/[.]-*[0123456789][0123456789][0123456789]*\"/.$$X$$D\"/" \
	-e "/^ *__version__/s/[.]\\([0123456789]\\)\"/.\\1.$$X$$D\"/" \
	-e "/^ *__copyright__/s/(C) [0123456789]*-[0123456789]*/(C) $B-$$Y/" \
	-e "/^ *__copyright__/s/(C) [0123456789]* /(C) $$Y /" \
	$$f; done; }
	@ grep ^__version__ $(VERSIONFILES)
	@ $(MAKE) commit
commit:
	@ ver=`grep "version.*=" setup.cfg | sed -e "s/version *= */v/"` \
	; echo ": $(GIT) commit -m $$ver"
tag:
	@ ver=`grep "version.*=" setup.cfg | sed -e "s/version *= */v/"` \
	; rev=`${GIT} rev-parse --short HEAD` \
	; if test -r tmp.changes.txt \
	; then echo ": ${GIT} tag -F tmp.changes.txt $$ver $$rev" \
	; else echo ": ${GIT} tag $$ver $$rev" ; fi

DOCKER=docker
PYTHON2=python
PYTHON3=python3
GIT=git
TWINE=twine

include centos-main-makefile.mk
include centos-epel-makefile.mk
include ubuntu-main-makefile.mk
include opensuse-main-makefile.mk

repos:
	$(DOCKER) images --format "{{.ID}}\t{{.Repository}}:{{.Tag}}\t{{.Size}}" | grep /mirror-packages/
prune:
	: $(DOCKER) volume prune
	$(DOCKER) volume list | cut -c 8- | xargs -r docker volume rm 

removes: removes1 removes2 removes3 removes4
removes1 removes-opensuse:
	$(DOCKER) ps -q -f status=exited | xargs -r docker rm
	$(DOCKER) images --format "{{.ID}}\t{{.Repository}}:{{.Tag}}\t{{.Size}}" \
	| grep /mirror-packages/opensuse-repo | cut -f 2 | xargs -r docker rmi
removes2 removes-ubuntu:
	$(DOCKER) ps -q -f status=exited | xargs -r docker rm
	$(DOCKER) images --format "{{.ID}}\t{{.Repository}}:{{.Tag}}\t{{.Size}}" \
	| grep /mirror-packages/ubuntu-repo | cut -f 2 | xargs -r docker rmi
removes3 removes-centos:
	$(DOCKER) ps -q -f status=exited | xargs -r docker rm
	$(DOCKER) images --format "{{.ID}}\t{{.Repository}}:{{.Tag}}\t{{.Size}}" \
	| grep /mirror-packages/centos-repo | cut -f 2 | xargs -r docker rmi
	$(DOCKER) images --format "{{.ID}}\t{{.Repository}}:{{.Tag}}\t{{.Size}}" \
	| grep /mirror-packages/almalinux-repo | cut -f 2 | xargs -r docker rmi
removes4 removes-epel:
	$(DOCKER) ps -q -f status=exited | xargs -r docker rm
	$(DOCKER) images --format "{{.ID}}\t{{.Repository}}:{{.Tag}}\t{{.Size}}" \
	| grep /mirror-packages/epel-repo | cut -f 2 | xargs -r docker rmi

# new style to make /base image and .disk repo - after being tested.
base diskbase basedisk savebasedisk: obase ubase rbase
obase: ; $(PYTHON3) opensuse-docker-mirror.tests.py test_58 --savebasedisk -vv $V $K
ubase: ; $(PYTHON3) ubuntu-docker-mirror.tests.py test_68 --savebasedisk -vv $V $K
rbase: ; $(PYTHON3) centos-docker-mirror.tests.py test_78 --savebasedisk -vv $V $K


rebuild: rebuild1 rebuild2 rebuild3 rebuild4
rebuild1 opensuse-rebuild:
	$(MAKE) removes-opensuse
	$(MAKE) opensuserepo.15.2
	$(MAKE) opensuserepo.15.4
	$(MAKE) opensuserepo.15.5
	$(MAKE) opensuserepo.15.6
rebuild2 ubuntu-rebuild:
	$(MAKE) removes-ubuntu
	$(MAKE) ubunturepo.16.04
	$(MAKE) ubunturepo.18.04
	$(MAKE) universerepo.20.04
	$(MAKE) universerepo.22.04
	$(MAKE) universerepo.24.04
rebuild3 centos-rebuild:
	$(MAKE) removes-centos
	$(MAKE) centosrepo.7.9
	: $(MAKE) centosrepo.8.5
	$(MAKE) almarepo.9.1
	$(MAKE) almarepo.9.3
rebuild4 epel-rebuild:
	$(MAKE) removes-epel
	$(MAKE) epelrepo.7
	: $(MAKE) epelrepo.8
	$(MAKE) epelrepo.9

du: ;  cd repo.d/. || exit 1 ; for i in *.*; do if test -d "$$i"; then du -sh "$$i/."; fi ; done
universe: ; cd repo.d/. || exit 1 ; for i in ubuntu*; do du -sh "$$i/."; done

size:
	@ echo "| docker image                          | size"
	@ echo "| ------------------------------------- | ----"
	@ docker images --format "{{.Repository}}:{{.Tag}}\t| {{.Size}}" \
	| sed -e "/mirror-packages/!d" -e "s:.*/mirror-packages/:| mirror-packages/:" -e "/repo:/!d" -e "/:latest/d" \
	| sed -e "/centos-repo:.[.].[.]/d" -e "/centos-repo:7\\t/d"
sizes:
	@ echo "| docker image                                  | size"
	@ echo "| --------------------------------------------- | ----"
	@ docker images --format "{{.Repository}}:{{.Tag}}\t| {{.Size}}" \
	| sed -e "/mirror-packages/!d" -e "s:.*/mirror-packages/:| mirror-packages/:" -e "/repo:/d" -e "/:latest/d" \
	| sed -e "/\\/http/d" 
nonmain:
	@ docker images --format "{{.Repository}}:{{.Tag}}\t{{.Size}}" \
	| sed -e "/mirror-packages/!d" -e "s:.*/mirror-packages/::" -e /repo:/d -e "/\\/main/d" -e "/-repo\\//!d"
untag:
	$(MAKE) nonmain | cut -f 1 | xargs -r docker rmi

# ..............................................

LOCAL=--local
TESTING=-vv

K=
test_1%: ; ./docker_mirror.tests.py $@ $(TESTING) $V $K 
test_2%: ; ./docker_mirror.tests.py $@ $(TESTING) $V $K 
test_3%: ; ./docker_mirror.tests.py $@ $(TESTING) $V $K 
test_5%: ; ./opensuse-docker-mirror.tests.py $@ $(TESTING) $V $K 
test_6%: ; ./ubuntu-docker-mirror.tests.py $@ $(TESTING) $V $K 
test_7%: ; ./centos-docker-mirror.tests.py $@ $(TESTING) $V $K 
test_9%: ; ./docker_image.tests.py $@ $(TESTING) $V $K $(LOCAL)
m_%: ; ./docker_mirror.tests.py $@ $(TESTING) $V $K 
o_%: ; ./opensuse-docker-mirror.tests.py $@ $(TESTING) $V $K 
images: ; ./docker_image.tests.py $(TESTING) $V $K $(LOCAL)

RETESTING=$(TESTING) --skipfullimage --sleep=300
st_5%: ; ./opensuse-docker-mirror.tests.py te$@ $(RETESTING) $V $K
st_6%: ; ./ubuntu-docker-mirror.tests.py te$@ $(RETESTING) $V $K
st_7%: ; ./centos-docker-mirror.tests.py te$@ $(RETESTING) $V $K


dry precheck: ; ./docker_mirror.tests.py -vv $V $K --dryrun
check: mm oo cc uu
mm: ; ./docker_mirror.tests.py -vv $V $K
oo: ; ./opensuse-docker-mirror.tests.py -v $V $K
uu: ; ./ubuntu-docker-mirror.tests.py -v $V $K
rr: ; ./centos-docker-mirror.tests.py -v $V $K

ooo: ; ./opensuse-docker-mirror.tests.py -v $V $K --coverage --only 15.6
uuu: ; ./ubuntu-docker-mirror.tests.py -v $V $K --coverage --only 24.04
rrr: ; ./centos-docker-mirror.tests.py -v $V $K --coverage --only 9.4

tests: ; $(PYTHON3) dockerdir-tests.py $K

####### pip setuptools
README: README.md
	cat README.md | sed -e "/\\/badge/d" -e /^---/q > $@
setup.py: Makefile
	{ echo '#!/usr/bin/env python3' \
	; echo 'import setuptools' \
	; echo 'setuptools.setup()' ; } > setup.py
	chmod +x setup.py
setup.py.tmp: Makefile
	echo "import setuptools ; setuptools.setup()" > setup.py

.PHONY: build
build:
	rm -rf build dist *.egg-info
	$(MAKE) $(PARALLEL) setup.py README
	# pip install --root=~/local . -v
	$(PYTHON3) setup.py sdist
	- rm -v setup.py README
	$(TWINE) check dist/*
	: $(TWINE) upload dist/*

# ------------------------------------------------------------
PIP3=pip3
install:
	$(MAKE) setup.py README
	trap "rm -v setup.py README" SIGINT SIGTERM ERR EXIT ; \
	$(PIP3) install .
	$(MAKE) showfiles | grep /.local/
uninstall:
	test -d tmp || mkdir -v tmp
	cd tmp && $(PIP3) uninstall -y `sed -e '/name *=/!d' -e 's/name *= *//' ../setup.cfg`
showfiles:
	test -d tmp || mkdir -v tmp
	@ cd tmp && $(PIP3) show --files `sed -e '/name *=/!d' -e 's/name *= *//' ../setup.cfg` \
	| sed -e "s:[^ ]*/[.][.]/\\([a-z][a-z]*\\)/:~/.local/\\1/:"
re reinstall:
	- $(MAKE) uninstall
	$(MAKE) install
# ------------------------------------------------------------

####### retype + stubgen
PY_RETYPE = ../retype
py-retype:
	set -ex ; if test -d $(PY_RETYPE); then cd $(PY_RETYPE) && $(GIT) pull; else : \
	; cd $(dir $(PY_RETYPE)) && $(GIT) clone git@github.com:ambv/retype.git $(notdir $(PY_RETYPE)) \
	; cd $(PY_RETYPE) && $(GIT) checkout 17.12.0 ; fi
	python3 $(PY_RETYPE)/retype.py --version

mypy:
	zypper install -y mypy
	zypper install -y python3-click python3-pathspec
	$(MAKE) py-retype

PYLINT = pylint
PYLINT_OPTIONS =
pylint:
	zypper install -y python3-pylint

# mypy 1.0.0 has minimum --python-version 3.7
# mypy 1.9.0 has minimum --python-version 3.8
MYPY = mypy
MYPY_STRICT = --strict --show-error-codes --show-error-context --no-warn-unused-ignores --python-version 3.8

AUTOPEP8=autopep8
AUTOPEP8_INPLACE= --in-place
AUTOPEP8_ASDIFF= --diff

PY1 = docker_mirror.py
PY2 = dockerdir.py
PY3 = centos-docker-mirror.py
PY4 = opensuse-docker-mirror.py
PY5 = ubuntu-docker-mirror.py
PY6 = scripts/filelist.py
PY7 = scripts/mirrorlist.py
PY8 = scripts/mirrors.fedoraproject.org.py
PY9 = docker_image.py
P11 = docker_mirror.tests.py
P12 = dockerdir.tests.py
P19 = docker_image.tests.py

%.type:
	test -f $(@:.type=i) || mkdir tmp.scripts || true
	test -f $(@:.type=i) || cp $(@:.type=) tmp.scripts/$(subst -,_,$(notdir $(@:.type=)))
	test -f $(@:.type=i) || $(MYPY) $(MYPY_STRICT) $(MYPY_OPTIONS) tmp.scripts/$(subst -,_,$(notdir $(@:.type=)))
	test ! -f $(@:.type=i) || $(PYTHON3) $(PY_RETYPE)/retype.py $(@:.type=) -t tmp.scripts -p $(dir $@)
	test ! -f $(@:.type=i) || $(PYTHON3) $(PY_RETYPE)/retype.py $(@:.type=) -t tmp.scripts -p $(dir $@)
	test ! -f $(@:.type=i) || $(MYPY) $(MYPY_STRICT) $(MYPY_OPTIONS) tmp.scripts/$(notdir $(@:.type=))

%.pep1:
	$(AUTOPEP8) $(AUTOPEP8_OPTIONS) $(@:.pep1=) $(AUTOPEP8_ASDIFF)
%.pep8:
	$(AUTOPEP8) $(AUTOPEP8_OPTIONS) $(@:.pep8=) $(AUTOPEP8_INPLACE)
	$(GIT) --no-pager diff $(@:.pep8=)
%.lint:
	$(PYLINT) $(PYLINT_OPTIONS) $(@:.lint=)

py1: ; $(MAKE) $(PY1).pep8
py2: ; $(MAKE) $(PY2).pep8
py3: ; $(MAKE) $(PY3).pep8
py4: ; $(MAKE) $(PY4).pep8
py5: ; $(MAKE) $(PY5).pep8
py6: ; $(MAKE) $(PY6).pep8
py7: ; $(MAKE) $(PY7).pep8
py8: ; $(MAKE) $(PY8).pep8
ty1: ; $(MAKE) $(PY1).type
ty2: ; $(MAKE) $(PY2).type
ty3: ; $(MAKE) $(PY3).type
ty4: ; $(MAKE) $(PY4).type
ty5: ; $(MAKE) $(PY5).type
ty6: ; $(MAKE) $(PY6).type
ty7: ; $(MAKE) $(PY7).type
ty8: ; $(MAKE) $(PY8).type
ty9: ; $(MAKE) $(PY9).type
t11: ; $(MAKE) $(P11).type
t12: ; $(MAKE) $(P12).type
t19: ; $(MAKE) $(P19).type


type: ;	 $(MAKE) $(PY1).type $(PY2).type $(PY3).type $(PY4).type $(PY5).type $(PY6).type $(PY7).type $(PY8).type $(PY9).type \
                 $(P11).type $(P12).type $(P19).type
lint: ;	 $(MAKE) $(PY1).lint             $(PY3).lint $(PY4).lint $(PY5).lint $(PY6).lint $(PY7).lint $(PY8).lint $(PY9).lint \
                 $(P11).lint $(P12).lint $(P19).lint
style: ; $(MAKE) $(PY1).pep8 $(PY2).pep8 $(PY3).pep8 $(PY4).pep8 $(PY5).pep8 $(PY6).pep8 $(PY7).pep8 $(PY8).pep8 $(PY9).pep8 \
                 $(P11).pep8 $(P12).pep8 $(P19).pep8

# .................................
clean:
	- rm -rf dist
	- rm -rf tmp.scripts
	- rm -rf docker.tmp
	- rm -rf .mypy_cache

