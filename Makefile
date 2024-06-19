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

PYTHON2=python
PYTHON3=python3
TWINE=twine

include centos-main-makefile.mk
include centos-epel-makefile.mk
include ubuntu-main-makefile.mk
include opensuse-main-makefile.mk

repos:
	docker images --format "{{.ID}}\t{{.Repository}}:{{.Tag}}\t{{.Size}}" | grep /mirror-packages/
removes:
	docker images --format "{{.ID}}\t{{.Repository}}:{{.Tag}}\t{{.Size}}" | cut -f 2 | xargs -r docker rmi
prune:
	: docker volume prune
	docker volume list | cut -c 8- | xargs -r docker volume rm 

rebuild: rebuild1 rebuild2 rebuild3
rebuild1:
	make opensuserepo.15.2
	make opensuserepo.15.4
	make opensuserepo.15.5
	make opensuserepo.15.6
rebuild2:
	make centosrepo.7.7
	make centosrepo.7.9
	make almarepo.9.1
	make almarepo.9.3
rebuild3:
	make ubunturepo.16.04
	make ubunturepo.18.04
	make universerepo.20.04
	make universerepo.22.04
	make universerepo.24.04

universe:
	cd repo.d/. || exit 1 ; for i in ubuntu*; do du -sh "$$i/."; done

sizes:
	@ docker images --format "{{.Repository}}:{{.Tag}}\t{{.Size}}" \
	| sed -e "/mirror-packages/!d" -e "s:.*/mirror-packages/::" -e /repo:/d -e /:latest/d
nonmain:
	@ docker images --format "{{.Repository}}:{{.Tag}}\t{{.Size}}" \
	| sed -e "/mirror-packages/!d" -e "s:.*/mirror-packages/::" -e /repo:/d -e "/\\/main/d" -e "/-repo\\//!d"
untag:
	$(MAKE) nonmain | cut -f 1 | xargs -r docker rmi

# ..............................................

K=
test_%: ; ./docker_mirror.tests.py $@ -vv $K
check: ; ./docker_mirror.tests.py -vv $K
dry precheck: ; ./docker_mirror.tests.py -vv $K --dryrun

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
	$(PIP3) uninstall -y `sed -e '/name *=/!d' -e 's/name *= *//' setup.cfg`
showfiles:
	@ $(PIP3) show --files `sed -e '/name *=/!d' -e 's/name *= *//' setup.cfg` \
	| sed -e "s:[^ ]*/[.][.]/\\([a-z][a-z]*\\)/:~/.local/\\1/:"
re reinstall:
	- $(MAKE) uninstall
	$(MAKE) install
# ------------------------------------------------------------

####### retype + stubgen
PY_RETYPE = ../retype
py-retype:
	set -ex ; if test -d $(PY_RETYPE); then cd $(PY_RETYPE) && git pull; else : \
	; cd $(dir $(PY_RETYPE)) && git clone git@github.com:ambv/retype.git $(notdir $(PY_RETYPE)) \
	; cd $(PY_RETYPE) && git checkout 17.12.0 ; fi
	python3 $(PY_RETYPE)/retype.py --version

mypy:
	zypper install -y mypy
	zypper install -y python3-click python3-pathspec
	$(MAKE) py-retype

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
P11 = docker_mirror.tests.py
P12 = dockerdir.tests.py

%.type:
	test -f $(@:.type=i) || $(MYPY) $(MYPY_STRICT) $(MYPY_OPTIONS) $(@:.type=)
	test ! -f $(@:.type=i) || $(PYTHON3) $(PY_RETYPE)/retype.py $(@:.type=) -t tmp.scripts -p $(dir $@)
	test ! -f $(@:.type=i) || $(PYTHON3) $(PY_RETYPE)/retype.py $(@:.type=) -t tmp.scripts -p $(dir $@)
	test ! -f $(@:.type=i) || $(MYPY) $(MYPY_STRICT) $(MYPY_OPTIONS) tmp.scripts/$(notdir $(@:.type=))
%.pep1:
	$(AUTOPEP8) $(AUTOPEP8_OPTIONS) $(@:.pep1=) $(AUTOPEP8_ASDIFF)
%.pep8:
	$(AUTOPEP8) $(AUTOPEP8_OPTIONS) $(@:.pep8=) $(AUTOPEP8_INPLACE)
	git --no-pager diff $(@:.pep8=)

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
t11: ; $(MAKE) $(P11).type
t12: ; $(MAKE) $(P12).type

type: ;	 $(MAKE) $(PY1).type $(PY2).type $(PY3).type $(PY4).type $(PY5).type $(PY6).type $(PY7).type $(PY8).type \
                 $(P11).type $(P12).type
style: ; $(MAKE) $(PY1).pep8 $(PY2).pep8 $(PY3).pep8 $(PY4).pep8 $(PY5).pep8 $(PY6).pep8 $(PY7).pep8 $(PY8).pep8 \
                 $(P11).pep8 $(P12).pep8

# .................................
clean:
	- rm -rf dist
	- rm -rf tmp.scripts
	- rm -rf docker.tmp
	- rm -rf .mypy_cache

