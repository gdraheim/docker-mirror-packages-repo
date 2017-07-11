FROM centos:centos7
COPY scripts /srv/scripts
RUN yum install -y wget
#
ENV REL 7
ENV VER 7.3.1611
ENV XXX --exclude-directories=LiveOS,isolinux,images,EFI
ENV FTP2 ftp://mirror.de.leaseweb.net/centos/7.3.1611
ENV CUT2 --cut-dirs=3
ENV FTP1 ftp://mirror.eu.oneandone.net/linux/distributions/centos/7.3.1611
ENV CUT1 --cut-dirs=5

# wget -O mirrorlist.os.txt "http://mirrorlist.centos.org/?release=7&repo=os&arch=x86_64"
# wget -O mirrorlist.extras.txt "http://mirrorlist.centos.org/?release=7&repo=extras&arch=x86_64"
# wget -O mirrorlist.updates.txt "http://mirrorlist.centos.org/?release=7&repo=updates&arch=x86_64"

RUN mkdir -p "/srv/repo/$VER/os"
RUN wget -4 -P /srv/repo/$VER/os -nv -nH $XXX --mirror $CUT2 $FTP2/os/x86_64
RUN ls -ld /srv/repo/$VER/os/x86_64/*
#
RUN mkdir -p "/srv/repo/$VER/extras"
RUN wget -4 -P /srv/repo/$VER/extras -nv -nH $XXX --mirror $CUT2 $FTP2/extras/x86_64
RUN ls -ld /srv/repo/$VER/extras/x86_64/*
#
RUN mkdir -p "/srv/repo/$VER/updates"
RUN wget -4 -P /srv/repo/$VER/updates -nv -nH $XXX --mirror $CUT2 $FTP2/updates/x86_64
RUN ls -ld /srv/repo/$VER/extras/x86_64/*
+
RUN cd /srv/repo && ln -s "$VER" "$REL"
#
VOLUME /srv/repo/data
EXPOSE 80
CMD "cd /srv/repo && python /srv/scripts/mirrorlist.py"
