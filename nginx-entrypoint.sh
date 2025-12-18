#!/bin/sh
set -e

SSL_DIR=/etc/nginx/ssl/live/$NGINX_HOST_NAME
CERT=$SSL_DIR/fullchain.pem
KEY=$SSL_DIR/privkey.pem

# if certs are not exist, create self-signed
if [ ! -f "$CERT" ] || [ ! -f "$KEY" ]; then
    mkdir -p $SSL_DIR
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout $KEY -out $CERT \
        -subj "/CN=$NGINX_HOST_NAME"
fi

envsubst '\$NGINX_HOST_NAME' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

nginx -g 'daemon off;'
