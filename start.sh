#!/bin/sh
sed -i "s|listen_ipv6=YES|listen_ipv6=NO|g" /etc/vsftpd.conf
sed -i "s|listen=NO|listen=YES|g" /etc/vsftpd.conf
sed -i "s|local_enable=NO|local_enable=YES|g" /etc/vsftpd.conf
sed -i "s|xferlog_enable=NO|xferlog_enable=YES|g" /etc/vsftpd.conf
sed -i "s|#write_enable=YES|write_enable=YES|g" /etc/vsftpd.conf
echo "local_root=/home/powerauto/data" >> /etc/vsftpd.conf
echo "pasv_enable=YES" >> /etc/vsftpd.conf
echo "pasv_min_port=30090" >> /etc/vsftpd.conf
echo "pasv_max_port=30100" >> /etc/vsftpd.conf
echo "pasv_promiscuous=YES" >> /etc/vsftpd.conf
echo "chroot_local_user=YES" >> /etc/vsftpd.conf
echo "allow_writeable_chroot=YES" >> /etc/vsftpd.conf
echo "listen_port=30021" >> /etc/vsftpd.conf
echo "pasv_address=${PASV_ADDRESS}" >> /etc/vsftpd.conf
service vsftpd start
gunicorn --bind=0.0.0.0:${API_PORT} wsgi:app --timeout 600
