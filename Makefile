#! /usr/bin/make -f

include centos-makefile.mk
include opensuse-makefile.mk
include ubuntu-makefile.mk

centos.7.6 centos.7.6.1810: ; $(MAKE) centosdir CENTOS=7.6.1810
centos.7.5 centos.7.5.1804: ; $(MAKE) centosdir CENTOS=7.5.1804
centos.7.4 centos.7.4.1708: ; $(MAKE) centosdir CENTOS=7.4.1708
centos.7.3 centos.7.3.1611: ; $(MAKE) centosdir CENTOS=7.3.1611
centos-7.6 centos-7.6.1810: ; $(MAKE) centos CENTOS=7.6.1810
centos-7.5 centos-7.5.1804: ; $(MAKE) centos CENTOS=7.5.1804
centos-7.4 centos-7.4.1708: ; $(MAKE) centos CENTOS=7.4.1708
centos-7.3 centos-7.3.1611: ; $(MAKE) centos CENTOS=7.3.1611

opensuse.15.0: ; $(MAKE) opensusedir LEAP=15.0
opensuse.42.3: ; $(MAKE) opensusedir LEAP=42.3
opensuse.42.2: ; $(MAKE) opensusedir LEAP=42.2
opensusesync.15.0: ; $(MAKE) opensuserepo LEAP=15.0
opensusesync.42.3: ; $(MAKE) opensuserepo LEAP=42.3
opensuserepo.15.0: ; $(MAKE) opensuserepo LEAP=15.0 OPENSUSE=opensuse/leap
opensuserepo.42.3: ; $(MAKE) opensuserepo LEAP=42.3 OPENSUSE=opensuse
opensuse-15.0: ; $(MAKE) opensuse LEAP=15.0 OPENSUSE=opensuse/leap
opensuse-42.3: ; $(MAKE) opensuse LEAP=42.3 OPENSUSE=opensuse
opensuse-42.2: ; $(MAKE) opensuse LEAP=42.2 OPENSUSE=opensuse

ubuntu.16.04: ; $(MAKE) ubuntudir UBUNTU=16.04
ubuntu.18.04: ;	$(MAKE) ubuntudir UBUNTU=18.04
ubuntusync.16.04: ; $(MAKE) ubuntusync UBUNTU=16.04 REPOS=updates
ubuntusync.18.04: ; $(MAKE) ubuntusync UBUNTU=18.04 REPOS=updates
ubunturepo.16.04: ; $(MAKE) ubunturepo UBUNTU=16.04 REPOS=updates
ubunturepo.18.04: ; $(MAKE) ubunturepo UBUNTU=18.04 REPOS=updates
ubuntu-16.04: ; $(MAKE) ubuntu UBUNTU=16.04
ubuntu-18.04: ;	$(MAKE) ubuntu UBUNTU=18.04

