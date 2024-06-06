FROM centos
RUN cd /etc/yum.repos.d/
RUN sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*
RUN sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*
RUN dnf -y install epel-release
RUN dnf -y install jsoncpp
RUN yum install -y passwd expect libevent libicu logrotate openssl perl-DBD-Pg perl-Time-HiRes python3 uuid glibc-common
ENV POSTGRES_PASSWD=kirill
WORKDIR /pangolin
COPY ./files /pangolin
RUN bash pangolin_install.sh

# VOLUME ["/pgdata/06/data"]

#FROM alpine
#RUN apk add --no-cache bash jsoncpp shadow expect libevent icu-dev logrotate openssl perl-dbd-pg perl-time-hires python3 uuidgen coreutils tar sudo sed rpm postgresql
#ENTRYPOINT ["tail", "-f", "/dev/null"]
#CMD /bin/bash
