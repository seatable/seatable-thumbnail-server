import os

SEATABLE_THUMBNAIL_SERVER_LETSENCRYPT = os.getenv(
    'SEATABLE_THUMBNAIL_SERVER_LETSENCRYPT', 'True')
SEATABLE_THUMBNAIL_SERVER_HOSTNAME = os.getenv(
    'SEATABLE_THUMBNAIL_SERVER_HOSTNAME', 'thumbnail.seatable.cn')

server_prefix = 'https://' if SEATABLE_THUMBNAIL_SERVER_LETSENCRYPT == 'True' else 'http://'
SERVER_URL = server_prefix + SEATABLE_THUMBNAIL_SERVER_HOSTNAME


# seafile
seafile_config_path = '/opt/seatable-thumbnail/conf/seafile.conf'
seafile_config = """
[fileserver]
port=8082

[database]
type = mysql
host = host
port = 3306
user = user
password = password
db_name = db_name
connection_charset = utf8
"""

if not os.path.exists(seafile_config_path):
    with open(seafile_config_path, 'w') as f:
        f.write(seafile_config)


# ccnet
ccnet_config_path = '/opt/seatable-thumbnail/conf/ccnet.conf'
ccnet_config = """
[General]
SERVICE_URL = %s/

[Database]
ENGINE = mysql
HOST = host
PORT = 3306
USER = user
PASSWD = password
DB = db_name
CONNECTION_CHARSET = utf8
""" % (SERVER_URL)

if not os.path.exists(ccnet_config_path):
    with open(ccnet_config_path, 'w') as f:
        f.write(ccnet_config)


# seatable-thumbnail
seatable_thumbnail_config_path = '/opt/seatable-thumbnail/conf/seatable_thumbnail_settings.py'
seatable_thumbnail_config = """
# mysql
MYSQL_USER = 'user'
MYSQL_PASSWORD = 'password'
MYSQL_HOST = 'host'
MYSQL_PORT = '3306'
DATABASE_NAME = 'db_name'

PLUGINS_REPO_ID = ''
"""

if not os.path.exists(seatable_thumbnail_config_path):
    with open(seatable_thumbnail_config_path, 'w') as f:
        f.write(seatable_thumbnail_config)


# nginx
nginx_config_path = '/opt/seatable-thumbnail/conf/nginx.conf'
nginx_common_config = """

    # for letsencrypt
    location /.well-known/acme-challenge/ {
        alias /var/www/challenges/;
        try_files $uri =404;
    }

    proxy_set_header X-Forwarded-For $remote_addr;

    location / {
        proxy_pass http://localhost:8088;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host $server_name;

        access_log      /opt/nginx-logs/seatable-thumbnail.access.log seatableformat;
        error_log       /opt/nginx-logs/seatable-thumbnail.error.log;
    }

    location /seafhttp {
        rewrite ^/seafhttp(.*)$ $1 break;
        proxy_pass http://127.0.0.1:8082;

        client_max_body_size 0;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;

        proxy_request_buffering off;
        proxy_connect_timeout  36000s;
        proxy_read_timeout  36000s;
        proxy_send_timeout  36000s;

        send_timeout  36000s;

    }

    # cloud.seatable.cn
    # location /thumbnail/ {
    #     proxy_pass https://thumbnail.seatable.cn;
    # }
    #
    # location /dtable-plugins/ {
    #     proxy_pass https://thumbnail.seatable.cn;
    # }
    #
    # location ~ /workspace/\d/asset/ {
    #     proxy_pass https://thumbnail.seatable.cn;
    #     proxy_redirect off; 
    # }
    #

}
"""

ssl_dir = '/opt/ssl/'
account_key = ssl_dir + SEATABLE_THUMBNAIL_SERVER_HOSTNAME + '.account.key'
domain_key = ssl_dir + SEATABLE_THUMBNAIL_SERVER_HOSTNAME + '.key'
domain_csr = ssl_dir + SEATABLE_THUMBNAIL_SERVER_HOSTNAME + '.csr'
signed_chain_crt = ssl_dir + SEATABLE_THUMBNAIL_SERVER_HOSTNAME + '.crt'


# init nginx https config after init http
def init_https():
    # init letsencrypt
    print('Start init letsencrypt')
    if not os.path.exists(domain_key) or not os.path.exists(signed_chain_crt):
        os.system('mkdir -p /var/www/challenges/')

        if not os.path.exists(account_key):
            os.system('openssl genrsa 4096 > %s' % account_key)
        if not os.path.exists(domain_key):
            os.system('openssl genrsa 4096 > %s' % domain_key)
        if not os.path.exists(domain_csr):
            os.system('openssl req -new -sha256 -key %s -subj "/CN=%s" > %s' %
                      (domain_key, SEATABLE_THUMBNAIL_SERVER_HOSTNAME, domain_csr))

        ret = os.system('python3 /scripts/acme-tiny-master/acme_tiny.py --account-key %s --csr %s --acme-dir /var/www/challenges/ > %s' %
                        (account_key, domain_csr, signed_chain_crt))

        if ret != 0:
            os.system('rm -f %s %s' % (signed_chain_crt, nginx_config_path))
            print('\nAuto init letsencrypt failed, delete nginx config anyway.')
            print('Please check your Domain and try again later, now quit.\n')
            import sys
            sys.exit()

        # crontab letsencrypt renew cert
        with open('/opt/ssl/renew_cert', 'w') as f:
            f.write('0 1 1 * * /scripts/renew_cert.sh 2>> /opt/ssl/letsencrypt.log\n')
        os.system('ln -s /opt/ssl/renew_cert /var/spool/cron/crontabs/root')

    #
    nginx_https_config = """
log_format seatableformat '\$http_x_forwarded_for \$remote_addr [\$time_local] "\$request" \$status \$body_bytes_sent "\$http_referer" "\$http_user_agent" \$upstream_response_time';

server {
    if ($host = %s) {
        return 301 https://$host$request_uri;
    }
    listen 80;
    server_name %s;
    return 404;
}

server {
    server_name %s;
    listen 443 ssl;

    ssl_certificate %s;
    ssl_certificate_key %s;
    ssl_session_timeout 5m;
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA:ECDHE-RSA-AES128-SHA:DHE-RSA-AES256-SHA:DHE-RSA-AES128-SHA;
    ssl_session_cache shared:SSL:50m;
    ssl_prefer_server_ciphers on;

""" % (SEATABLE_THUMBNAIL_SERVER_HOSTNAME, SEATABLE_THUMBNAIL_SERVER_HOSTNAME,
       SEATABLE_THUMBNAIL_SERVER_HOSTNAME, signed_chain_crt, domain_key) \
        + nginx_common_config

    with open(nginx_config_path, 'w') as f:
        f.write(nginx_https_config)
    os.system('nginx -s reload')


# init nginx http config
nginx_http_config = """
log_format seatableformat '$http_x_forwarded_for $remote_addr [$time_local] "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent" $upstream_response_time';

server {
    server_name %s;
    listen 80;

""" % (SEATABLE_THUMBNAIL_SERVER_HOSTNAME) + nginx_common_config

if not os.path.exists(nginx_config_path):
    with open(nginx_config_path, 'w') as f:
        f.write(nginx_http_config)

    if not os.path.exists('/etc/nginx/sites-enabled/default'):
        os.system(
            'ln -s /opt/seatable-thumbnail/conf/nginx.conf /etc/nginx/sites-enabled/default')
    os.system('nginx -s reload')

    # init https
    if SEATABLE_THUMBNAIL_SERVER_LETSENCRYPT == 'True' \
            and SEATABLE_THUMBNAIL_SERVER_HOSTNAME not in ('', '127.0.0.1'):
        init_https()


print('\nInit config success')
