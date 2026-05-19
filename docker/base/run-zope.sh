#!/bin/bash

# execute all scripts in ~/docker-entrypoint.d/*.sh on each startup
. bin/entrypoint.sh

exec runzope --configure <(envsubst '$HTTP_PORT' '$READ_ONLY' <etc/zope.conf)
