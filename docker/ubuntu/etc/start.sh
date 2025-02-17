#! /bin/sh

INSTANCE_HOME="/home/zope/"
CONFIG_FILE="/home/zope/etc/zope.conf"
ZOPE_RUN="/home/zope/venv/bin/runzope"
export INSTANCE_HOME

exec "$ZOPE_RUN" -C "$CONFIG_FILE" "$@"


