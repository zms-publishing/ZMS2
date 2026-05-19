#!/bin/sh
# vim:sw=4:ts=4:et

set -e

entrypoint_log() {
    if [ -z "${ZOPE_ENTRYPOINT_QUIET_LOGS:-}" ]; then
        echo "$@"
    fi
}

if /usr/bin/find "/home/zope/entrypoint.d/" -mindepth 1 -maxdepth 1 -type f -print -quit 2>/dev/null | read v; then
    entrypoint_log "$0: /home/zope/entrypoint.d/ is not empty, will attempt to perform configuration"

    find "/home/zope/entrypoint.d/" -follow -type f -print | sort -V | while read -r f; do
        case "$f" in
        *.envsh)
            if [ -x "$f" ]; then
                entrypoint_log "$0: Sourcing $f"
                . "$f"
            else
                entrypoint_log "$0: Ignoring $f, not executable"
            fi
            ;;
        *.sh)
            if [ -x "$f" ]; then
                entrypoint_log "$0: Launching $f"
                "$f"
            else
                entrypoint_log "$0: Ignoring $f, not executable"
            fi
            ;;
        *) entrypoint_log "$0: Ignoring $f" ;;
        esac
    done

    entrypoint_log "$0: Configuration complete; ready for start up"
else
    entrypoint_log "$0: No files found in /home/zope/entrypoint.d/, skipping configuration"
fi
