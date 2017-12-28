FROM ubuntu:16.04
MAINTAINER  Subrata Sarker  <subrata_sarker@yahoo.com>

RUN apt-get update && \
    apt-get -y install sudo \
                build-essential \
                vim apache2 \
                apache2-dev \
                curl \
                python2.7 \
                python-dev \
                python-pip \
                libsqlite3-dev \
                sqlite3 \
                libsqlite3-dev \
                cron
RUN useradd -m ubuntu && echo "ubuntu:ubuntu" | chpasswd && adduser ubuntu sudo
EXPOSE 80
ENV USER ubuntu
USER ubuntu
WORKDIR /home/ubuntu
CMD /bin/bash