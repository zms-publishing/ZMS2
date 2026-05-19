# Docker (Zope/ZEO) — local development

This project ships a Docker Compose setup to run **Zope** with a **ZEO** backend, plus an optional **debug** profile with code-server and debugger ports.

## Prerequisites

- Docker + Docker Compose (with support for `develop.watch`)
- Free host ports:
  - `80` (default Zope)
  - Debug profile: `8080`, `5678`, `8085`, `8086`

## Services (docker-compose.yml)

- `zeo`: ZEO server (internal port `8090`, not published to host)
- `zope`: main Zope instance (publishes `80:80`)
- `zope-debug` (profile `debug`): code-server + debug ports, depends on `zeo`

## Quickstart

From the repository root:

- Build and run:
  - `docker compose up --build`
- Open Zope:
  - http://localhost/

Stop / remove containers:

- `docker compose down`

## Debug profile (optional)

Starts a container intended for debugging, including VSCode code-server and debugpy port forwarding.

- Run debug profile:
  - `docker compose --profile debug up --build`

Endpoints / ports:

- code-server: http://localhost:8080
- debugpy: `localhost:5678`
- Zope ports exposed by the debug service: `8085`, `8086`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HTTP_PORT` | `8080` | HTTP port Zope listens on. Substituted into `zope.conf` via `envsubst`. |
| `READ_ONLY` | `false` | Set to `true` to start Zope in ZEO read-only mode. Useful for staging/production replicas. |

Both variables are substituted into `zope.conf` at startup by `run-zope.sh` using `envsubst`.

## Entrypoint Scripts

On every startup, `run-zope.sh` sources `bin/entrypoint.sh`, which executes all scripts in `/home/zope/entrypoint.d/` in sorted order:

- `*.sh` — executed as subprocess (must be executable)
- `*.envsh` — sourced into the current shell (must be executable)
- other files — ignored

Mount your scripts via the `docker/zope/entrypoint.d/` volume. Example: `docker/zope/entrypoint.d/10-example.sh`.

Set `ZOPE_ENTRYPOINT_QUIET_LOGS=1` to suppress entrypoint log output.

## Volumes and persistence

Bind mounts used by the containers:

- `docker/zope/etc/` → `/home/zope/etc/`
  - Zope/ZEO config files (e.g. `zope.conf`, `zeo.conf`, `zope_debug.conf`)
- `docker/zope/var/` → `/home/zope/var/`
  - persistent data (e.g. `Data.fs`), logs, caches
- `docker/zope/Extensions/` → `/home/zope/Extensions/`
  - shared Zope External Methods folder
- `docker/zope/entrypoint.d/` → `/home/zope/entrypoint.d/`
  - startup hook scripts (see Entrypoint Scripts above)

## Configuration notes

- `docker/zope/etc/zope.conf` is configured as a **ZEO client** and connects to `zeo:8090` for both `main` and `temporary` storages.
- `docker/zope/etc/zeo.conf` defines the ZEO server and file storages in `/home/zope/var/`.
- `docker/zope/etc/zope_debug.conf` is a standalone (filestorage) debug config and defaults to HTTP port `8085`.
- `zope.conf` logs to both files (with `$HTTP_PORT` suffix to avoid conflicts) and to **stdout/stderr** for `docker compose logs` visibility.
- `READ_ONLY` is substituted into the `<zeoclient>` `read-only` directive. Set `READ_ONLY=true` to prevent writes to the ZEO backend.

## Live development workflow

Compose `develop.watch` is configured to:

- `sync+restart` on changes in `./Products` → `/home/zope/Products`
- trigger `rebuild` on changes to `docker/base/Dockerfile*`, `requirements*.txt`, `setup.py`, `setup.cfg`

## Useful commands

- Follow logs:
  - `docker compose logs -f zope`
  - `docker compose logs -f zeo`

## Troubleshooting (short)

- If host port `80` is already in use, change the `ports:` mapping in `docker-compose.yml`.
- To reset the database, remove the contents of `docker/zope/var/` (this deletes `Data.fs`).
