#!/bin/sh -e

DASHBOARD_SCRIPT="/usr/share/grafana/public/dashboards/bigchaindb_dashboard.js"

if [ "${INFLUXDB_HOST}" == "**None**" ]; then
    unset INFLUXDB_HOST
fi

if [ -n "${INFLUXDB_HOST}" ]; then
    sed -i -u "s#const influxdb_host = .*#const influxdb_host = \'${INFLUXDB_HOST}\';#g" ${DASHBOARD_SCRIPT}
fi

connect_db() {
    while ! curl 'http://admin:admin@localhost:3000/'
    do
        echo "$(date) - waiting for Grafana to be ready"
        sleep 5
    done
    curl 'http://admin:admin@localhost:3000/api/datasources' -X POST -H 'Content-Type: application/json;charset=UTF-8' --data-binary '{"name": "influx", "type": "influxdb","url": "http://'"${INFLUXDB_HOST}"':8086", "access": "proxy", "isDefault": true, "database": "telegraf", "user": "root", "password":"root"}'
}

connect_db &

chown -R grafana:grafana /var/lib/grafana /var/log/grafana

# grafana-cli plugins install jdbranham-diagram-panel

exec gosu grafana /usr/sbin/grafana-server  \
  --homepath=/usr/share/grafana             \
  --config=/etc/grafana/grafana.ini         \
  cfg:default.paths.data=/var/lib/grafana   \
  cfg:default.paths.logs=/var/log/grafana   \
  cfg:default.paths.plugins=/var/lib/grafana/plugins

