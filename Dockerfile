FROM sofraserv/financedb_base:test

ENV POWERAUTO_PWD "autopass"

RUN    useradd -ms /bin/bash powerauto
RUN    echo powerauto:${POWERAUTO_PWD} | chpasswd
WORKDIR /var/www/tdScannerReader
RUN    mkdir /var/www/tdScannerReader/logs
RUN    mkdir -p /home/powerauto/data && chown powerauto /home/powerauto/data/ && chgrp powerauto /home/powerauto/data/

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