FROM phusion/baseimage:0.11
# docker.seafile.top/seafile-dev/seatable-thumbnail-server:1.3.0

# Aliyun ubuntu source
RUN rm -rf /etc/apt/sources.list
COPY scripts/my-ubuntu-source.list /etc/apt/sources.list

## Dev related libs
RUN apt-get update --fix-missing

# Nginx
RUN apt-get install -y nginx

# Mysql
RUN apt-get install -y mysql-client

# set python3.6 global
RUN apt-get install -y python3 python3-pip python3-setuptools python3-ldap
RUN python3.6 -m pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple && rm -r /root/.cache/pip
RUN rm -f /usr/bin/python && \
    rm -f /usr/bin/python3 && \
    rm -f /usr/bin/pip && \
    rm -f /usr/bin/pip3 && \
    ln -s /usr/bin/python3.6 /usr/bin/python && \
    ln -s /usr/bin/python3.6 /usr/bin/python3 && \
    ln -s /usr/local/bin/pip3.6 /usr/bin/pip && \
    ln -s /usr/local/bin/pip3.6 /usr/bin/pip3

RUN pip3 install uvicorn pillow pymysql sqlalchemy future \
    -i https://mirrors.aliyun.com/pypi/simple && rm -r /root/.cache/pip


# seatable-thumbnail
RUN mkdir -p /opt/seatable-thumbnail 
WORKDIR /opt/seatable-thumbnail
COPY src/seafile /opt/seatable-thumbnail/seafile
COPY src/seatable-thumbnail-server /opt/seatable-thumbnail/seatable-thumbnail-server

RUN ln -sf /opt/seatable-thumbnail/seafile/lib/libsearpc.so.1.0.2 /opt/seatable-thumbnail/seafile/lib/libsearpc.so.1
RUN ln -sf /opt/seatable-thumbnail/seafile/lib/libsearpc.so.1.0.2 /opt/seatable-thumbnail/seafile/lib/libsearpc.so
RUN ln -sf /opt/seatable-thumbnail/seafile/lib/libccnet.so.0.0.0 /opt/seatable-thumbnail/seafile/lib/libccnet.so.0
RUN ln -sf /opt/seatable-thumbnail/seafile/lib/libccnet.so.0.0.0 /opt/seatable-thumbnail/seafile/lib/libccnet.so


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