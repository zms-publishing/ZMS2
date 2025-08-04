# @work...

## <kbd>DE</kbd> | ZMS2-Reconstruction

Das ZMS2-Dockerfile verwendet die Python2-Requirements von ZMS3, um hier einen seinerzeit aktuellen Zope2-App-Server-Stand abzubbilden. Der Customlayer kann ohne pip-basierte Installation integriert werden, indem einfach der des existente produktive Products-Folder in den instance-Folder kopiert wird.
Falls neuere Products-Versionen verwendet werden als auf dem live-System, dann sind ggf. einige Stellen zu patchen, weil sich bestimmte Module-Namen geändert haben:




1. from Globals import HTMLFile, MessageDialog, INSTANCE_HOME, Acquisition ==> import Acquisition
   * /home/zope/instance/Products/exUserFolder/PropSources/mysqlPropSource/mysqlPropSource.py, line 23
   * /home/zope/instance/Products/exUserFolder/PropSources/pgPropSource/pgPropSource.py, line 24,
   * /home/zope/instance/Products/exUserFolder/PropSources/cmfPropSource/cmfPropSource.py, line 28
   * /home/zope/instance/Products/exUserFolder/PropSources/usPropSource/usPropSource.py, line 6

2. import zExceptions \
	raise zExceptions.Unauthorized(self.docLogin(self, request))\
   *Module Products.exUserFolder.exUserFolder, line 957, in challenge, TypeError: exceptions must be old-style classes or derived from BaseException, not str*

# Zope Configuration Files

## `instance/etc/zeo.conf`

```xml
# ZEO configuration file
%define INSTANCE_HOME /home/zope/instance
%define VIRTUAL_ENV /home/zope/venv

<zeo>
    # address 0.0.0.0:8100
    address  $INSTANCE_HOME/var/zeosocket
    read-only false
    pid-filename $INSTANCE_HOME/var/ZEO.pid
    invalidation-queue-size 100
    # monitor-address PORT
    # transaction-timeout SECONDS
</zeo>

<filestorage 1>
    path $INSTANCE_HOME/var/Data.fs
</filestorage>

<eventlog>
  <logfile>
    path $INSTANCE_HOME/log/zeo.log
  </logfile>
</eventlog>

<runner>
  program $INSTANCE_HOME/bin/runzeo
  socket-name $INSTANCE_HOME/var/zeo.zdsock
  daemon true
  forever false
  backoff-limit 10
  exit-codes 0, 2
  directory $INSTANCE_HOME
  default-to-interactive true
  # user zope
  python $VIRTUAL_ENV/bin/python
  zdrun $VIRTUAL_ENV/lib/python2.7/site-packages/zdaemon/zdrun.py

  # This logfile should match the one in the zeo.conf file.
  # It is used by zdctl's logtail command, zdrun/zdctl doesn't write it.
  logfile $INSTANCE_HOME/log/zeo.log
</runner>
```


## `instance/etc/zope.conf.tmpl`

```xml
# Environment variable substitution:
# Created at $CONF_TS
# - READ_ONLY: Set to true to start Zope in read-only mode.
# - HTTP_PORT: The container port on which the Zope port is mapped to.
%define READ_ONLY $READ_ONLY
%define HTTP_PORT $HTTP_PORT


# Zope configuration variables
%define INSTANCE_HOME /home/zope/instance
%define VIRTUAL_ENV /home/zope/venv
%import ZEO

instancehome $INSTANCE_HOME
# ip-address 0.0.0.0

# debug-mode on

<http-server>
	# In the container Zope is running on default port 8080
	address 8080
</http-server>

<zodb_db main>
	mount-point /
	cache-size 5000
	<zeoclient>
		# server localhost:9999
		server $INSTANCE_HOME/var/zeosocket
		storage 1
		name zeostorage
		var $INSTANCE_HOME/var
		cache-size 20MB
		client $INSTANCE_HOME/var/zms_zeo_$HTTP_PORT
		read-only $READ_ONLY
	</zeoclient>
</zodb_db>

<zodb_db temporary>
	# Temporary storage database (for sessions)
	<temporarystorage>
		name temporary storage for sessioning
	</temporarystorage>
	mount-point /temp_folder
	container-class Products.TemporaryFolder.TemporaryContainer
</zodb_db>

<eventlog>
  level info
  <logfile>
    path $INSTANCE_HOME/log/event_$HTTP_PORT.log
    level info
  </logfile>
</eventlog>

<logger access>
  level WARN
  <logfile>
    path $INSTANCE_HOME/log/Z2_$HTTP_PORT.log
    format %(message)s
  </logfile>
</logger>
```

