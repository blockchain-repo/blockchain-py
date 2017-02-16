FROM hub.c.163.com/library/debian:jessie

RUN echo "deb http://mirrors.163.com/ubuntu trusty main universe\n" > /etc/apt/sources.list && \
    apt-get update && \
    apt-get -y --force-yes --no-install-recommends install libfontconfig curl ca-certificates && \
    apt-get clean && \
    curl http://ogm2sl5zb.bkt.clouddn.com/grafana_4.0.2.deb > /tmp/grafana.deb && \
    dpkg -i /tmp/grafana.deb && \
    rm /tmp/grafana.deb && \
        curl -L http://ogm2sl5zb.bkt.clouddn.com/gosu-amd64 > /usr/sbin/gosu && \
    chmod +x /usr/sbin/gosu && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

VOLUME ["/var/lib/grafana", "/var/log/grafana", "/etc/grafana" ]


COPY ./run.sh /run.sh

COPY ./bigchaindb_dashboard.js /usr/share/grafana/public/dashboards/

ENV INFLUXDB_HOST **None**

ENTRYPOINT ["/run.sh"]
