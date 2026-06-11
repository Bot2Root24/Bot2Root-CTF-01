#!/bin/bash
set -e
service cron start
ipsec start || true
exec /usr/sbin/sshd -D
