#! /usr/bin/make -f

include centos-makefile.mk
include opensuse-makefile.mk
include ubuntu-makefile.mk
include epel-makefile.mk

epel.7: ; $(MAKE) epeldir EPEL=7
epel.8: ; $(MAKE) epeldir EPEL=8
epelsync.7: ; $(MAKE) epelsync EPEL=7
epelsync.8: ; $(MAKE) epelsync EPEL=8

centos.8.0 centos.8.0.1905: ; $(MAKE) centosdir CENTOS=8.0.1905
centos.7.7 centos.7.7.1908: ; $(MAKE) centosdir CENTOS=7.7.1908
centos.7.6 centos.7.6.1810: ; $(MAKE) centosdir CENTOS=7.6.1810
centos.7.5 centos.7.5.1804: ; $(MAKE) centosdir CENTOS=7.5.1804
centos.7.4 centos.7.4.1708: ; $(MAKE) centosdir CENTOS=7.4.1708
centos.7.3 centos.7.3.1611: ; $(MAKE) centosdir CENTOS=7.3.1611
centossync.8.0 centossync.8.0.1905: ; $(MAKE) centossync CENTOS=8.0.1905
centossync.7.7 centossync.7.7.1908: ; $(MAKE) centossync CENTOS=7.7.1908
centossync.7.6 centossync.7.6.1810: ; $(MAKE) centossync CENTOS=7.6.1810
centossync.7.5 centossync.7.5.1804: ; $(MAKE) centossync CENTOS=7.5.1804
centossync.7.4 centossync.7.4.1708: ; $(MAKE) centossync CENTOS=7.4.1708
centossync.7.3 centossync.7.3.1611: ; $(MAKE) centossync CENTOS=7.3.1611
centosrepo.8.0 centosrepo.8.0.1905: ; $(MAKE) centosrepo CENTOS=8.0.1905 centostags
centosrepo.7.7 centosrepo.7.7.1908: ; $(MAKE) centosrepo CENTOS=7.7.1908 centostags
centosrepo.7.6 centosrepo.7.6.1810: ; $(MAKE) centosrepo CENTOS=7.6.1810 centostags
centosrepo.7.5 centosrepo.7.5.1804: ; $(MAKE) centosrepo CENTOS=7.5.1804 centostags
centosrepo.7.4 centosrepo.7.4.1708: ; $(MAKE) centosrepo CENTOS=7.4.1708 centostags
centosrepo.7.3 centosrepo.7.3.1611: ; $(MAKE) centosrepo CENTOS=7.3.1611 centostags
centos-8.0 centos-8.0.1905: ; $(MAKE) centos CENTOS=8.0.1905
centos-7.7 centos-7.7.1908: ; $(MAKE) centos CENTOS=7.7.1908
centos-7.6 centos-7.6.1810: ; $(MAKE) centos CENTOS=7.6.1810
centos-7.5 centos-7.5.1804: ; $(MAKE) centos CENTOS=7.5.1804
centos-7.4 centos-7.4.1708: ; $(MAKE) centos CENTOS=7.4.1708
centos-7.3 centos-7.3.1611: ; $(MAKE) centos CENTOS=7.3.1611

opensuse.15.1: ; $(MAKE) opensusedir LEAP=15.1
opensuse.15.0: ; $(MAKE) opensusedir LEAP=15.0
opensuse.42.3: ; $(MAKE) opensusedir LEAP=42.3
opensuse.42.2: ; $(MAKE) opensusedir LEAP=42.2
opensusesync.15.1: ; $(MAKE) opensusesync LEAP=15.1
opensusesync.15.0: ; $(MAKE) opensusesync LEAP=15.0
opensusesync.42.3: ; $(MAKE) opensusesync LEAP=42.3
opensuserepo.15.1: ; $(MAKE) opensuserepo LEAP=15.1 OPENSUSE=opensuse/leap
opensuserepo.15.0: ; $(MAKE) opensuserepo LEAP=15.0 OPENSUSE=opensuse/leap
opensuserepo.42.3: ; $(MAKE) opensuserepo LEAP=42.3 OPENSUSE=opensuse
opensuse-15.1: ; $(MAKE) opensuse LEAP=15.1 OPENSUSE=opensuse/leap
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
ubuntu-18.04: ; $(MAKE) ubuntu UBUNTU=18.04

universesync.16.04: ; $(MAKE) ubuntusync UBUNTU=16.04 REPOS=universe
universesync.18.04: ; $(MAKE) ubuntusync UBUNTU=18.04 REPOS=universe
universerepo.16.04: ; $(MAKE) ubunturepo UBUNTU=16.04 REPOS=universe
universerepo.18.04: ; $(MAKE) ubunturepo UBUNTU=18.04 REPOS=universe
