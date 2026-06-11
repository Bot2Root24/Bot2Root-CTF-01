#!/bin/bash
# Update vsftpd.conf with instance-specific passive ports
if [ -n "$PASV_MIN_PORT" ] && [ -n "$PASV_MAX_PORT" ]; then
    sed -i "s/^pasv_min_port=.*/pasv_min_port=$PASV_MIN_PORT/" /etc/vsftpd.conf
    sed -i "s/^pasv_max_port=.*/pasv_max_port=$PASV_MAX_PORT/" /etc/vsftpd.conf
fi
if [ -n "$PASV_ADDRESS" ]; then
    sed -i "s/^pasv_address=.*/pasv_address=$PASV_ADDRESS/" /etc/vsftpd.conf
fi
exec /usr/sbin/vsftpd /etc/vsftpd.conf
