FROM python:3.9.13-buster

ENV POWERAUTO_PWD "autopass"

RUN    useradd -ms /bin/bash powerauto
RUN    mkdir /DataBroker/Sources/TosScannerReader/data/
RUN    echo powerauto:${POWERAUTO_PWD} | chpasswd
WORKDIR /var/www/tdScannerReader

#RUN    apt-get update

ADD    --chown=powerauto:powerauto /DataBroker/Sources/TosScannerReader/data/ /home/powerauto/data/

RUN    echo y | apt-get install unixodbc unixodbc-dev
RUN    echo y | apt-get install locales
RUN    echo y | apt-get install vsftpd
RUN    echo y | apt-get install libpam-pwdfile
RUN    sed -i 's/^# *\(en_US.UTF-8\)/\1/' /etc/locale.gen
RUN    locale-gen en_US.UTF-8  
ENV    LANG en_US.UTF-8  
ENV    LANGUAGE en_US:en  
ENV    LC_ALL en_US.UTF-8 
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

ADD start.sh /var/www/tdScannerReader/start.sh
RUN chmod +x /var/www/tdScannerReader/start.sh
CMD ["/var/www/tdScannerReader/start.sh"]