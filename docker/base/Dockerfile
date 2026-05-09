FROM ubuntu:20.04

# Image name: zms2:ubuntu
LABEL org.opencontainers.image.title="zms2:ubuntu"

# Get environment variables from docker-compose.yml:
# So, image file must be created with docker-compose build
# ############################
# Use simple ARG defaults so Docker expands them correctly.
ARG INSTANCE_DIR=/home/zope
ARG VENV_DIR=/home/zope/venv
ARG IS_DEBUG=false
ARG UID=1000
ARG GID=1000
# ############################

# Non-interactive installs and default timezone to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive TZ=Europe/Berlin

RUN \
    --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    <<EOR
    set -xe

    # Ensure all system packages are up to date
    apt-get update
    apt-get --yes upgrade

    # Preconfigure timezone non-interactively
    echo "tzdata tzdata/Areas select Europe" | debconf-set-selections && \
    echo "tzdata tzdata/Zones/Europe select Berlin" | debconf-set-selections && \
    apt-get install --yes --no-install-recommends tzdata && \
    ln -fs /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

    # Install dependencies
    apt-get install --yes ca-certificates
    update-ca-certificates

    apt-get install --yes bash git curl lsof netcat inetutils-ping nano iproute2
    apt-get install --yes --no-install-recommends gettext-base
    apt-get install --yes build-essential
    apt-get install --yes python2 python2-dev
    # Install pip for Python 2 (pip 20.3) since Ubuntu 20.04 does not ship python2-pip
    curl -sS https://bootstrap.pypa.io/pip/2.7/get-pip.py -o /tmp/get-pip.py && \
        python2 /tmp/get-pip.py pip==20.3 && \
        rm /tmp/get-pip.py
    # Install virtualenv for creating Python2 virtual environments
    python2 -m pip install virtualenv
    apt-get install --yes libsasl2-dev libldap2-dev libssl-dev libsqlite3-dev
    apt-get install --yes memcached libmemcached-tools
    apt-get install --yes mariadb-client default-libmysqlclient-dev
    apt-get install --yes slapd ldap-utils
    apt-get install --yes libnss3 libxss1 libasound2 libatk1.0-0 libgtk-3-0 libx11-xcb1 libxcb1
EOR


# ------------------------------
# Add Packages needed for VSCode
RUN apt-get update && apt-get install -y apt-transport-https ca-certificates gnupg curl && \
    curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/repos/vscode stable main" > /etc/apt/sources.list.d/vscode.list && \
    rm -rf /var/lib/apt/lists/*
# ------------------------------

# Set host's UID/GID to allow sharing of production files as bind mounts
RUN groupadd --gid $GID zope
RUN adduser --disabled-password --uid $UID --gid $GID zope

# Grant zope passwordless sudo for development purposes if IS_DEBUG is set to true
RUN if [ "$IS_DEBUG" = "true" ]; then \
    echo "Debug mode is ON. Granting zope passwordless sudo." && \
    apt-get update && \
    apt-get install -y sudo && \
    echo 'zope ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers && \
    adduser zope sudo; \
    else \
    echo "Debug mode is OFF. Not granting zope passwordless sudo."; \
    fi

USER zope
# Create Zope Instance
ENV INSTANCE_DIR=$INSTANCE_DIR
ENV VIRTUAL_ENV=$VENV_DIR
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN virtualenv --python=python2 $VIRTUAL_ENV

WORKDIR $VIRTUAL_ENV/bin
RUN bash -c "source activate"

RUN ./pip install git+https://github.com/zms-publishing/ZMS2.git@master#egg=ZMS
RUN ./pip install -r https://raw.githubusercontent.com/zms-publishing/zms3/master/requirements-extra.txt

# # Create Zope Instance
# RUN ./mkzopeinstance --dir ${INSTANCE_DIR} --user admin:admin
# COPY ./var ${INSTANCE_DIR}/var

# EXPOSE 3306
# EXPOSE 8080
# EXPOSE 8085
# EXPOSE 8086
# EXPOSE 8087

# Finally Start Zope by Script
# ENTRYPOINT ["/bin/sh -c"]
# ENTRYPOINT ["bash", "-c", "sleep infinity"]
# CMD ["$INSTANCE_HOME/bin/zopectl","fg"]
# CMD ["$INSTANCE_HOME/bin/runzope","-X","debug-mode=on"]cd
