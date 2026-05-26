#!/bin/sh
# vim:sw=4:ts=4:et

set -e

entrypoint_log() {
    if [ -z "${ZOPE_ENTRYPOINT_QUIET_LOGS:-}" ]; then
        echo "$@"
    fi
}

ENTRYPOINT_D="/home/zope/entrypoint.d"

if ! /usr/bin/find "$ENTRYPOINT_D" -mindepth 1 -maxdepth 1 -type f -print -quit 2>/dev/null | read _; then
    entrypoint_log "$0: No files found in $ENTRYPOINT_D, skipping configuration"
    return 0 2>/dev/null || exit 0
fi

find "$ENTRYPOINT_D" -maxdepth 1 -follow -type f -print | sort -V | while read -r file; do
    case "$file" in
    *.envsh)
        if [ -x "$file" ]; then
            entrypoint_log "$0: Sourcing $file"
            . "$file"
        fi
        ;;
    *.sh)
        if [ -x "$file" ]; then
            entrypoint_log "$0: Executing $file"
            "$file"
        fi
        ;;
    *) ;;
    esac
done
