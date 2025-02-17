#!/bin/bash
# The starting script works in three steps:
# 1. ZEO server in background (nohub)
# 2. Zope instance in foreground

instance_dir="/home/zope"

echo "Step-1: Starting ZEO"
nohup $instance_dir/bin/runzeo.sh --configure $instance_dir/etc/zeo.conf 1>/dev/null 2>/dev/null &

echo "Step-2: Starting ZOPE on port $zope_port"
# As foreground process:
$instance_dir/bin/runzope.sh

