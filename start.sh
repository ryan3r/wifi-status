#!/bin/ash

mkdir /run/nginx
/usr/sbin/nginx -c /etc/nginx/nginx.conf
python3 /root/server.py
