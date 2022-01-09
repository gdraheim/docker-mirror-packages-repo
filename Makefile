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

PYTHON2=python
PYTHON3=python3

include centos-makefile.mk
include opensuse-makefile.mk
include ubuntu-makefile.mk
include epel-makefile.mk

K=
test_%: ; ./testsuite.py $@ -v $K
check: ; ./testsuite.py -vv $K

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

MYPY = mypy
MYPY_STRICT = --strict --show-error-codes --show-error-context --no-warn-unused-ignores

type: 
	$(MAKE) type.r type.d type.f type.m type.e
type.r:
	$(MYPY) $(MYPY_STRICT) centos-mirror.py opensuse-mirror.py ubuntu-mirror.py
	- rm -rf .mypy_cache
type.d:
	$(PYTHON3) $(PY_RETYPE)/retype.py docker_mirror.py -t docker_mirror.tmp -p .
	$(MYPY) $(MYPY_STRICT) docker_mirror.tmp/docker_mirror.py
	- rm -rf .mypy_cache
type.f:
	$(PYTHON3) $(PY_RETYPE)/retype.py scripts/filelist.py -t scripts.tmp -p scripts
	$(MYPY) $(MYPY_STRICT) scripts.tmp/filelist.py
	- rm -rf .mypy_cache
type.m:
	$(PYTHON3) $(PY_RETYPE)/retype.py scripts/mirrorlist.py -t scripts.tmp -p scripts
	$(MYPY) $(MYPY_STRICT) scripts.tmp/mirrorlist.py
	- rm -rf .mypy_cache
type.e:
	$(PYTHON3) $(PY_RETYPE)/retype.py scripts/mirrors.fedoraproject.org.py -t scripts.tmp -p scripts
	$(MYPY) $(MYPY_STRICT) scripts.tmp/mirrors.fedoraproject.org.py
	- rm -rf .mypy_cache

AUTOPEP8=autopep8
pep style: 
	$(MAKE) pep.di pep.si pep.d pep.r pep.s 
pep.d style.d pep.d.apply style.d.apply:
	$(AUTOPEP8) docker_mirror.py --in-place
	git --no-pager diff docker_mirror.py
pep.di style.di pep.di.apply style.di.apply:
	$(AUTOPEP8) docker_mirror.pyi --in-place
	git --no-pager diff docker_mirror.pyi
pep.r style.r pep.r.apply style.r.apply:
	$(AUTOPEP8) centos-mirror.py opensuse-mirror.py ubuntu-mirror.py --in-place
	git --no-pager diff centos-mirror.py opensuse-mirror.py ubuntu-mirror.py
pep.s style.s pep.s.apply style.s.apply:
	$(AUTOPEP8) scripts/*.py --in-place
	git --no-pager diff scripts/*.py
pep.si style.si pep.si.apply style.si.apply:
	$(AUTOPEP8) scripts/*.pyi --in-place
	git --no-pager diff scripts/*.pyi
