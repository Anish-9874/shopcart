#!/bin/sh
set -eu

if [ "$(id -u)" -eq 0 ]; then
    app_uid="$(id -u shopcart)"
    media_uid="$(stat -c '%u' /app/media)"

    if [ "$media_uid" != "$app_uid" ]; then
        chown -R shopcart:shopcart /app/media
    fi

    exec setpriv --reuid=shopcart --regid=shopcart --init-groups "$@"
fi

exec "$@"
