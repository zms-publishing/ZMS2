FROM ubuntu:16.04

# ############################
# Get environment variables from docker-compose.yml (and its env file):
# So, image file must be created with docker-compose build
# ############################
ARG INSTANCE_DIR
ARG VENV_DIR
ARG IS_DEBUG
ARG UID
ARG GID
# ############################

RUN apt-get update && apt-get install -y ca-certificates
RUN update-ca-certificates
RUN apt-get -y upgrade

# Install Zope/ZEO Dependencies
RUN apt-get install -y bash
RUN apt-get install -y wget
RUN apt-get install -y curl
RUN apt-get install -y --no-install-recommends gettext-base 
RUN apt-get install -y lsof netcat inetutils-ping nano
RUN apt-get install -y build-essential
RUN apt-get install -y git
RUN apt-get install -y python2.7
RUN apt-get install -y python-pip
RUN apt-get install -y python-minimal
RUN apt-get install -y python-dev
RUN apt-get install -y python-setuptools
RUN apt-get install -y python-virtualenv
RUN apt-get install -y libsasl2-dev
RUN apt-get install -y libldap2-dev
RUN apt-get install -y libssl-dev
RUN apt-get install -y libsqlite3-dev

# Install memcached
RUN apt-get update && \
	apt-get install -y memcached libmemcached-tools && \
	rm -rf /var/lib/apt/lists/*

# Install only MariaDB client libs
RUN apt-get update && \
	apt-get install -y mariadb-client libmysqlclient-dev && \
	rm -rf /var/lib/apt/lists/*

# Install slapd and ldap-utils without prompting for password
RUN echo "slapd slapd/internal/generated_adminpw password password" | debconf-set-selections && \
	echo "slapd slapd/internal/adminpw password password" | debconf-set-selections && \
	echo "slapd slapd/password2 password password" | debconf-set-selections && \
	echo "slapd slapd/password1 password password" | debconf-set-selections && \
	echo "slapd slapd/dump_database_destdir string /var/backups/slapd-VERSION" | debconf-set-selections && \
	echo "slapd slapd/domain string example.com" | debconf-set-selections && \
	echo "slapd shared/organization string Example Inc." | debconf-set-selections && \
	apt-get update && \
	apt-get install -y slapd ldap-utils && \
	rm -rf /var/lib/apt/lists/*

RUN python2 -m pip install pip==20.3

# Set host's UID/GID to allow sharing of production files as bind mounts
ENV UID=${UID:-1000}
ENV GID=${GID:-1000}
RUN groupadd --gid $GID zope
RUN adduser --disabled-password --uid $UID --gid $GID zope

USER zope
# Create Zope Instance
ENV INSTANCE_DIR=${INSTANCE_DIR}
ENV VIRTUAL_ENV=${VENV_DIR}
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV SHELL=/bin/bash
WORKDIR $VIRTUAL_ENV/bin

# Install ZMS and Zope in a Virtual Environment
RUN python2 -m pip install pip==20.3
RUN virtualenv --python=python2  $VIRTUAL_ENV
# RUN ./pip install --trusted-host zopefoundation.github.io -r https://zopefoundation.github.io/Zope/releases/2.13.29/requirements.txt
RUN ./pip install -r https://raw.githubusercontent.com/zms-publishing/zms3/master/requirements.txt
RUN ./pip install git+https://github.com/zms-publishing/ZMS2.git@master#egg=zms
RUN ./pip install Products.PluginRegistry==1.4
RUN ./pip install Products.LDAPUserFolder==2.27
RUN ./pip install Products.PluggableAuthService==1.11.0
RUN ./pip install Products.LDAPMultiPlugins==1.14
RUN ./pip install Products.ZSQLMethods==2.13.4
RUN ./pip install MySQL-python==1.2.5
RUN ./pip install Products.ZSQLiteDA==0.6.1
RUN ./pip install Products.ZMySQLDA==3.1.1
RUN ./pip install Products.SQLAlchemyDA
RUN ./pip install SQLAlchemy
RUN ./pip install Pillow
RUN ./pip install feedparser
RUN ./pip install xhtml2pdf==0.2.4
RUN ./pip install requests beautifulsoup4 lxml Markdown pyScss python-docx
RUN ./pip install python-memcached==1.59
RUN ./pip install --no-deps Products.mcdutils==2.0
# IMPORTANT: Install zExceptions last to avoid conflicts with other packages
RUN ./pip install -U --no-deps zExceptions
RUN ./pip install -U --no-deps zope.interface==4.1.3


# # Create Zope Instance (uncomment if needed)
# RUN ./mkzopeinstance --dir ${INSTANCE_DIR} --user admin:admin
# COPY ./var ${INSTANCE_DIR}/var

