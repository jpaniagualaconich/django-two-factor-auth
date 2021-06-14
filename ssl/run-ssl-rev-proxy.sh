#! /usr/bin/env sh

BASEDIR=$(dirname "$0")

mkdir -p "$BASEDIR/private"

mkcert -install

APP_NETLOC=${APP_NETLOC:-"127.0.0.1:8000"}
APP_DOMAIN=${APP_DOMAIN:-localhost}

KEY_FILE="$BASEDIR/private/$APP_DOMAIN.key"
CERT_FILE="$BASEDIR/private/$APP_DOMAIN.crt"

if [ ! -f $KEY_FILE ] || [ ! -f $CERT_FILE ]; then
    mkcert -key-file $KEY_FILE -cert-file $CERT_FILE $APP_DOMAIN
fi

echo "app domain is $APP_DOMAIN"
echo "will forward to $APP_NETLOC"

docker run --rm \
    --name sslreverseproxy \
    --network host \
    -e APP_NETLOC=$APP_NETLOC \
    -e APP_DOMAIN=$APP_DOMAIN \
    -v "$PWD/$BASEDIR/ssl-rev-proxy.nginx.conf.template:/etc/nginx/templates/default.conf.template" \
    -v "$PWD/$BASEDIR/private:/etc/ssl/private" \
    nginx
