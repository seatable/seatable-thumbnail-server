FROM ubuntu:24.04
# docker.seafile.top/seafile-dev/seatable-thumbnail-server:1.x.x

# https://github.com/phusion/baseimage-docker
COPY base_scripts /bd_build
RUN /bd_build/prepare.sh && \
    /bd_build/system_services.sh && \
    /bd_build/utilities.sh && \
    /bd_build/cleanup.sh
ENV DEBIAN_FRONTEND="teletype" \
    LANG="en_US.UTF-8" \
    LANGUAGE="en_US:en" \
    LC_ALL="en_US.UTF-8"

## Dev related libs
RUN apt-get update --fix-missing

# Time zone
RUN export DEBIAN_FRONTEND=noninteractive && apt-get install -y tzdata

# Nginx
RUN apt-get install -y nginx

# Mysql
RUN apt-get install -y mysql-client

# set python3 global
RUN apt-get install -y python3 python3-pip python3-setuptools && \
    rm /usr/lib/python3.12/EXTERNALLY-MANAGED && \
    rm -f /usr/bin/python && ln -s /usr/bin/python3 /usr/bin/python

RUN pip3 install --no-cache-dir uvicorn==0.16.0 pillow==10.2.* sqlalchemy==2.0.18 pymysql==1.0.* future==0.18.* requests==2.31.* redis==4.4.* django==4.2.*


# seatable-thumbnail
RUN mkdir -p /opt/seatable-thumbnail 
WORKDIR /opt/seatable-thumbnail
COPY seafile /opt/seatable-thumbnail/seafile
COPY seatable-thumbnail-server /opt/seatable-thumbnail/seatable-thumbnail-server

RUN ln -sf /opt/seatable-thumbnail/seafile/lib/libsearpc.so.1.0.2 /opt/seatable-thumbnail/seafile/lib/libsearpc.so.1
RUN ln -sf /opt/seatable-thumbnail/seafile/lib/libsearpc.so.1.0.2 /opt/seatable-thumbnail/seafile/lib/libsearpc.so


# scripts
COPY scripts /scripts

RUN mkdir -p /etc/service/nginx && \
	rm -f /etc/nginx/sites-enabled/* /etc/nginx/conf.d/* && \
	mv /scripts/nginx.conf /etc/nginx/nginx.conf && \
	mv /scripts/nginx.sh /etc/service/nginx/run

# my_init
RUN rm -rf /etc/my_init.d/*
COPY scripts/01_init.sh /etc/my_init.d/01_init.sh
RUN chmod +x /etc/my_init.d/01_init.sh \
	/scripts/*.sh \
	/scripts/*.py

CMD ["/sbin/my_init", "--", "/scripts/enterpoint.sh"]
