FROM phusion/baseimage:focal-1.2.0
# docker.seafile.top/seafile-dev/seatable-thumbnail-server:1.x.x

## Dev related libs
RUN apt-get update --fix-missing

# Time zone
RUN export DEBIAN_FRONTEND=noninteractive && apt-get install -y tzdata

# Nginx
RUN apt-get install -y nginx

# Mysql
RUN apt-get install -y mysql-client

# set python3.8 global
RUN apt-get install -y python3.8 python3-pip python3-setuptools
RUN python3 -m pip install --upgrade pip && rm -r /root/.cache/pip && \
    rm -f /usr/bin/python && ln -s /usr/bin/python3 /usr/bin/python && \
    rm -f /usr/bin/pip && ln -s /usr/local/bin/pip3 /usr/bin/pip

RUN pip3 install uvicorn==0.16.0 pillow==10.2.* sqlalchemy==2.0.18 pymysql==1.0.* future==0.18.* requests==2.31.* redis==4.4.* django==4.2.* \
    -i https://pypi.tuna.tsinghua.edu.cn/simple/ && rm -r /root/.cache/pip


# seatable-thumbnail
RUN mkdir -p /opt/seatable-thumbnail 
WORKDIR /opt/seatable-thumbnail
COPY src/seafile /opt/seatable-thumbnail/seafile
COPY src/seatable-thumbnail-server /opt/seatable-thumbnail/seatable-thumbnail-server

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
