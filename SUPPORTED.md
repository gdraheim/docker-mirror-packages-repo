## CENTOS

The CentOS support time span follows the time span of RHEL Redhat Enterprise Linux, 
and that's very long.

As the project began it was centos:7.3 to be around, so this is the first version you 
can find in the sources of the mirror project. In general the IT service of a company
will update to the next minor version within a few years as the basis is very stable.

In this world, a major version is supported atleast 5 years after the last minor
version. Similarly we can scrap every minor version about 5 years after its inception
although the CentOs guidelines say that they support every minor version as long as
the major version is supported.

The biggest problem with CentOs is not so much the base distribution but that most
software setup scenarios can only succeed with extra packages from the SCL and EPEL
projects. And those might bring in a dependency that does not allow to update soon.

### CentOs Releases

    7.3.1611 # 2016-12 # 2021 (2024-08)
    7.4.1708 # 2017-09 # 2022 (2024-08)
    7.5.1804 # 2018-05 # 2023 (2024-08)
    7.6.1810 # 2018-12 # 2023 (2024-08)
    7.7.1908 # 2019-09 # 2024 (2024-08)
    7.8.2003 # 2020-04 # 2024 (2024-08)
    7.9.2009 #
    8.0.1905 # 2019-09 # 2029 (2029-05)
    8.1.1911 # 2020-01 # 2029 (2029-05)
    8.2.2004 # 2020-06 # 2029 (2029-05)
    8.3.2011 # 2020-12 # 2029 (2029-05)
    Stream-8 # (start) # 2021 (2021-12)

### CentOs Stream

Note that the CentOs team has announced an end-of-life of CentOS 8 at the end of 2021.
This follows the idea to switch from CentOS being behind the schedule of Redhat release
to be ahead of the current RHEL release. >> CentOS Stream continues after that date, 
serving as the upstream (development) branch of Red Hat Enterprise Linux. <<

 * https://blog.centos.org/2020/12/future-is-centos-stream/

### Redhat Releases

    7.3 # 2016-11 
    7.4 # 2017-07 
    7.5 # 2018-04 
    7.6 # 2018-10 
    7.7 # 2019-08 
    7.8 # 2020-03 
    8.0 # 2019-05 
    8.1 # 2019-11 
    8.2 # 2020-04

## UBUNTU

The Ubuntu support has a differentiation of LTS Long Term Support versions or not.
In the real world companies will only ever use LTS version to distribute their
software and other versions are only used for testing with the actual release
being delayed to the next LTS version which will be around every 2 years.

Similarly to RHEL the LTS version have a support of 5 years after its release.
In reality there is also an option for ESM Extended Security Maintenance that
companies can pay for, and that brings another 5 years of support. This makes
it not easy to decide for the mirror project when to drop that old version.

As this project began it was ubuntu:14.04 to be around, so this is the first
version you can find in the sources of the mirror project. As this version has
some serious bugs that were never fixed, we may assume that it will be dropped
soon by IT support. As a consequence the next version ubuntu:16.04 may be so
popular that ESM will be used even longer.

### Ubuntu Releases

     14.04    # 2014-04 # 2019 (LTS 2019-04)
     16.04    # 2016-04 # 2019 (LTS 2021-04)
     16.04.1  # 2016-07 # 2019 (LTS 2021-04)
     16.04.2  # 2017-02 # 2020 (LTS 2021-04)
     16.04.3  # 2017-08 # 2020 (LTS 2021-04)
     16.04.4  # 2018-03 # 2021 (LTS 2021-04)
     16.04.5  # 2018-08 # 2021 (LTS 2021-04)
     16.04.6  # 2019-02 # 2022 (LTS 2021-04)
     18.04    # 2018-04 # 2021 (LTS 2023-04)
     18.04.1  # 2018-07 # 2021 (LTS 2023-04)
     18.04.2  # 2019-02 # 2022 (LTS 2023-04)
     18.04.3  # 2019-08 # 2022 (LTS 2023-04)
     18.04.4  # 2020-02 # 2023 (LTS 2023-04)
     18.04.5  # 2020-08 # 2023 (LTS 2023-04)
     19.04    # 2019-04 #
     19.10    # 2019-10 #
     20.04    # 2020-04 # 2023 (LTS 2025-04)
     20.04.1  # 2020-07 # 2023 (LTS 2025-04)
     20.10    # 2020-10 #

###

## OPENSUSE

The Opensuse project did have a time when it tried to be independen of the
associated SLES Suse Enterpirse Linux. That made for a break in the version
scheme when 42.x was put in as a kind of "wait loop" for the versions of the
enterprise linux to catch up. Additionally, there is defined scheme when a
version will be handled as long term support. As a rule of thumb, the last
minor version of a major version cycle is supported longer.

As this project began it was opensuse 42.2 to be around. so this is the first
version you can find in the sources of the mirror project. As this version has
some peculiar annoyances, we may assume that it will be dropped soon - plus that
IT support has generally used SLES at the time. With Opensuse 15.x we may find
longer usage in the departments as it has more similarities with SLES.

In the following tables, the official support for Opensuse is quite short and
the mirror project may support them longer. The SLES versions have official
support being much longer but we put a limit of 3 years after publication here
as the enterprise IT departments are usually quieker than that.

### Opensuses Releases

     42.2 # 2016-11 # 2018-01
     42.3 # 2017-07 # 2019-06
     15.0 # 2018-05 # 2019-12
     15.1 # 2019-05 # 2020-11
     15.2 # 2020-07 # 2021-11
     15.3 # 2021-07 ?

### SLES Releases

     15 .00 # 2018-06 # 2021 (2028-07 / 2031-07)
     15 SP1 # 2019-06 # 2022 (2028-07 / 2031-07)
     15 SP2 # 2020-06 # 2023 (2028-07 / 2031-07)







