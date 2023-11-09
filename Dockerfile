FROM sofraserv/financedb_base:test

ENV POWERAUTO_PWD "autopass"

RUN    useradd -ms /bin/bash powerauto
RUN    echo powerauto:${POWERAUTO_PWD} | chpasswd
WORKDIR /var/www/tdScannerReader
RUN    mkdir /var/www/tdScannerReader/logs

ADD    --chown=powerauto:powerauto /DataBroker/Sources/TosScannerReader/data/ /home/powerauto/data/

RUN    echo y | apt-get install vsftpd
RUN    sed -i "s|listen_ipv6=YES|listen_ipv6=NO|g" /etc/vsftpd.conf
RUN    sed -i "s|listen=NO|listen=YES|g" /etc/vsftpd.conf
RUN    sed -i "s|local_enable=NO|local_enable=YES|g" /etc/vsftpd.conf
RUN    sed -i "s|xferlog_enable=NO|xferlog_enable=YES|g" /etc/vsftpd.conf
RUN    sed -i "s|#write_enable=YES|write_enable=YES|g" /etc/vsftpd.conf

RUN    echo "local_root=/home/powerauto/data" >> /etc/vsftpd.conf
RUN    echo "pasv_enable=YES" >> /etc/vsftpd.conf
RUN    echo "pasv_min_port=30090" >> /etc/vsftpd.conf
RUN    echo "pasv_max_port=30100" >> /etc/vsftpd.conf
RUN    echo "pasv_promiscuous=YES" >> /etc/vsftpd.conf
RUN    echo "chroot_local_user=YES" >> /etc/vsftpd.conf
RUN    echo "allow_writeable_chroot=YES" >> /etc/vsftpd.conf
RUN    echo "listen_port=30021" >> /etc/vsftpd.conf

EXPOSE 21/tcp
EXPOSE 22/tcp
EXPOSE 10090/tcp
EXPOSE 10091/tcp
EXPOSE 10092/tcp
EXPOSE 10093/tcp
EXPOSE 10094/tcp
EXPOSE 10095/tcp
EXPOSE 10096/tcp
EXPOSE 10097/tcp
EXPOSE 10098/tcp
EXPOSE 10099/tcp
EXPOSE 10100/tcp
EXPOSE 18080

COPY   requirements.txt requirements.txt
RUN    pip3 install -r requirements.txt

COPY   . /var/www/tdScannerReader
RUN    mkdir /var/www/tdScannerReader/DataBroker/Sources/TosScannerReader/data

ADD start.sh /var/www/tdScannerReader/start.sh
RUN chmod +x /var/www/tdScannerReader/start.sh
CMD ["/var/www/tdScannerReader/start.sh"]