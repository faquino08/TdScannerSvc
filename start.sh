#!/bin/sh
echo "pasv_address=${PASV_ADDRESS}" >> /etc/vsftpd.conf
service vsftpd start
gunicorn --bind=0.0.0.0:${API_PORT} wsgi:app --timeout 600