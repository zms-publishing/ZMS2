# Docker (Zope/ZEO) — local development

This project ships a Docker Compose setup to run **Zope** with a **ZEO** backend, plus an optional **debug** profile with code-server and debugger ports.

## Prerequisites

- Docker + Docker Compose (with support for `develop.watch`)
- Free host ports:
  - `8081` Zope-instance-1 publishing port
  - `8082` Zope-instance-2 publishing port
  - `8083` Zope-instance-3 publishing port
  - `808*` Zope-instance-* publishing port
  ---
  - `8888` VSCode Server
  - `8080` Zope-Debug-instance


## Services (docker-compose.yml)

- `zeo`: ZEO server
- `zope`: main Zope instance (publishes `8081+:8080`)
- `zope-debug` (profile `debug`): code-server + debug ports, depends on `zeo`

## Quickstart

From the repository root:

- Build and run:
  - `docker compose up --build`
- Open Zope:
  - http://localhost/

Stop / remove containers:

- `docker compose down`

## Environment file (.env)

Docker Compose resolves variables like `${INSTANCE_DIR}` and `${INSTANCE_MOUNT}` from a project `.env` file (or exported shell variables) before containers are started.

Recommended setup:

- Create or link a project `.env` file in the directory where `docker compose` is executed.
- For this project, you can reuse the instance env file:
  - `ln -s /home/zope/instance/zms2.env .env`

Typical variables to customize:

- `HOME_DIR`: Base path for all mounts.
- `INSTANCE_DIR`: Path used inside the container.
- `INSTANCE_MOUNT`: Host path to your local Zope instance.
- `VENV_DIR`: Python virtual environment path inside the container.
- `UID` / `GID`: Host user/group IDs to avoid file permission issues.

Example:

```env
UID=1000
GID=1000
HOME_DIR=/home/zope
VENV_DIR=${HOME_DIR}/venv
INSTANCE_DIR=${HOME_DIR}
INSTANCE_MOUNT=${HOME_DIR}/instance/zms2_dev
```

Important distinction:

- `env_file:` in `docker-compose.yml` sets runtime environment variables inside containers.
- `.env` (or `--env-file`) provides values for Compose file interpolation used in `build.args`, `volumes`, and similar fields.

## Debug profile (optional)

Starts a container with VSCode code-server intended for debugging.

- Run debug profile:
  - `docker compose --profile debug up --build`

Endpoints / ports:

- code-server: http://localhost:8888
- Zope ports exposed by the debug service: `8080`

## Volumes and persistence

Minimum bind mounts used by the containers:

- `docker/zope/etc/` → `/home/zope/etc/`
  - Zope/ZEO config files (e.g. `zope.conf`, `zeo.conf`, `zope_debug.conf`)
- `docker/zope/var/` → `/home/zope/var/`
  - persistent data (e.g. `Data.fs`), logs, caches
- `docker/zope/Extensions/` → `/home/zope/Extensions/`
  - shared Zope External Methods folder


## Configuration notes

- `docker/zope/etc/zeo.conf` defines the ZEO server and file storages in `/home/zope/var/`.
- `docker/zope/etc/zope.conf.tmpl` is a text-template for creating zope.conf-files with a portnumber-suffix.

## Useful commands

- Follow logs:
  - `docker compose logs -f zope`
  - `docker compose logs -f zeo`

## Troubleshooting (short)

- If host port `8080` is already in use, change the `ports:` mapping in `docker-compose.yml`.
- To reset the database, remove the contents of `docker/zope/var/` (this deletes `Data.fs`).
