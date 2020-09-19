# seatable-thumbnail-server-docker

## Deploy

1. mkdir -p /opt/seatable-thumbnail/shared/
2. vim /opt/seatable-thumbnail/docker-compose.yml
3. docker-compose up
4. vim /opt/seatable-thumbnail/shared/seatable-thumbnail/conf/*
5. vim /opt/seatable-thumbnail/shared/seatable-thumbnail/seafile-license.txt
6. docker exec -d seatable-thumbnail /scripts/seatable-thumbnail.sh

## Build

1. cp seatable_thumbnail docker/src/seatable-thumbnail-server/seatable_thumbnail
2. cp main.py docker/src/seatable-thumbnail-server/main.py
3. cp seafile docker/src/seafile (seafile folder was in seatable-pro-server_1.x.x.tar.gz)
4. docker build -t docker.seafile.top/seafile-dev/seatable-thumbnail-server:1.x.x ./
