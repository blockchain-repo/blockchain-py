/**
 * Created by ryan on 28.01.16.
 *
 * Default Graphana installation: /usr/share/grafana/
 *
 * Put this file in: /usr/share/grafana/public/dashboards/
 */
var window, document, ARGS, $, jQuery;

const influxdb_host = 'localhost';
const influxdb_port = '8086';

const telegraf_flush_rate = '10';

const search_url = 'http://' + window.document.location.host + '/';

const db = 'telegraf';
const query_measurements = 'SHOW MEASUREMENTS';
const column_prefix = 'statsd';

const default_interval = '10s';
const url = search_url + 'api/datasources/proxy/1/query?db=' + db + '&q=' + encodeURIComponent(query_measurements);

var dashboard = {
    rows : [],
    title: 'BigchainDB Monitor',
    time: {
        from: 'now-5m',
        to: 'now'
    },
    refresh: '5s'
};

$.ajax({
    url: url,
    type: "GET",
    success: create_layout
});

return dashboard;

function create_layout(data) {
    var validation_mean_columns = filter_columns('validate_transaction', 'mean', data);
    var validation_count_columns = filter_columns('validate_transaction', 'count', data);

    var write_mean_columns = filter_columns('write_transaction', 'mean', data);
    var write_count_columns = filter_columns('write_transaction', 'count', data);

    var block_validation_mean_columns = filter_columns('validate_block', 'mean', data);
    var block_validation_count_columns = filter_columns('validate_block', 'count', data);

    var block_write_mean_columns = filter_columns('write_block', 'mean', data);
    var block_write_count_columns = filter_columns('write_block', 'count', data);

    var to_validate_queue = filter_columns('tx_queue', 'gauge', data);

    dashboard.rows.push({
        title: 'Validate Transaction',
        height: '300px',
        panels: [
            {
                id: 1,
                title: 'Transaction Validation Time',
                type: 'graph',
                fill: false,
                stack: false,
                span: 6,
                legend: {show: false},
                leftYAxisLabel: 'Validation time (ms)',
                targets: validation_mean_columns.map((x) => {
                    return {
                        measurement: x,
                        query: 'SELECT mean("value") FROM "' + x + '" GROUP BY time(' + default_interval + ') fill(null)',
                        dsType: 'influxdb',
                        resultFormat: 'time_series'
                    }
                })
            },
            {
                id: 2,
                title: 'Transaction Validation Rate',
                type: 'graph',
                fill: true,
                stack: true,
                span: 6,
                legend: {show: false},
                grid: {leftMin: 0},
                leftYAxisLabel: 'Validations/s',
                tooltip: {
                    value_type: 'individual',
                    shared: true
                },
                targets: validation_count_columns.map((x) => {
                    return {
                        measurement: x,
                        target: 'SELECT mean("value") FROM "' + x + '" GROUP BY time(' + default_interval + ') fill(null)',
                        dsType: 'influxdb',
                        resultFormat: 'time_series',
                        query: 'SELECT mean("value")/' + telegraf_flush_rate + ' FROM "' + x + '" WHERE $timeFilter GROUP BY time(' + default_interval + ') fill(null)',
                        rawQuery: true
                    }
                })
            }
        ]
    });

    dashboard.rows.push({
        title: 'Write Transaction',
        height: '300px',
        panels: [
            {
                id: 1,
                title: 'Transaction Write Time',
                type: 'graph',
                fill: false,
                stack: false,
                span: 6,
                legend: {show: false},
                leftYAxisLabel: 'Write time (ms)',
                targets: write_mean_columns.map((x) => {
                    return {
                        measurement: x,
                        query: 'SELECT mean("value") FROM "' + x + '" GROUP BY time(' + default_interval + ') fill(null)'
                    }
                })
            },
            {
                id: 2,
                title: 'Transaction Write Rate',
                type: 'graph',
                fill: true,
                stack: true,
                span: 6,
                legend: {show: false},
                grid: {leftMin: 0},
                leftYAxisLabel: 'Writes/s',
                tooltip: {
                    value_type: 'individual',
                    shared: true
                },
                targets: write_count_columns.map((x) => {
                    return {
                        measurement: x,
                        target: 'SELECT mean("value") FROM "' + x + '" GROUP BY time(' + default_interval + ') fill(null)',
                        dsType: 'influxdb',
                        resultFormat: 'time_series',
                        query: 'SELECT mean("value")/' + telegraf_flush_rate + ' FROM "' + x + '" WHERE $timeFilter GROUP BY time(' + default_interval + ') fill(null)',
                        rawQuery: true
                    }
                })
            }
        ]
    });

    dashboard.rows.push({
        title: 'Validate Block',
        height: '300px',
        panels: [
            {
                id: 1,
                title: 'Block Validation Time',
                type: 'graph',
                fill: false,
                stack: false,
                span: 6,
                legend: {show: false},
                leftYAxisLabel: 'Validation time (ms)',
                targets: block_validation_mean_columns.map((x) => {
                    return {
                        measurement: x,
                        query: 'SELECT mean("value") FROM "' + x + '" GROUP BY time(' + default_interval + ') fill(null)'
                    }
                })
            },
            {
                id: 2,
                title: 'Block Validation Rate',
                type: 'graph',
                fill: true,
                stack: true,
                span: 6,
                legend: {show: false},
                grid: {leftMin: 0},
                leftYAxisLabel: 'Validations/s',
                tooltip: {
                    value_type: 'individual',
                    shared: true
                },
                targets: block_validation_count_columns.map((x) => {
                    return {
                        measurement: x,
                        target: 'SELECT mean("value") FROM "' + x + '" GROUP BY time(' + default_interval + ') fill(null)',
                        dsType: 'influxdb',
                        resultFormat: 'time_series',
                        query: 'SELECT mean("value")/' + telegraf_flush_rate + ' FROM "' + x + '" WHERE $timeFilter GROUP BY time(' + default_interval + ') fill(null)',
                        rawQuery: true
                    }
                })
            }
        ]
    });

    dashboard.rows.push({
        title: 'Write Block',
        height: '300px',
        panels: [
            {
                id: 1,
                title: 'Block Write Time',
                type: 'graph',
                fill: false,
                stack: false,
                span: 6,
                legend: {show: false},
                leftYAxisLabel: 'Write time (ms)',
                targets: block_write_mean_columns.map((x) => {
                    return {
                        measurement: x,
                        query: 'SELECT mean("value") FROM "' + x + '" GROUP BY time(' + default_interval + ') fill(null)'
                    }
                })
            },
            {
                id: 2,
                title: 'Block Write Rate',
                type: 'graph',
                fill: true,
                stack: true,
                span: 6,
                legend: {show: false},
                grid: {leftMin: 0},
                leftYAxisLabel: 'Writes/s',
                tooltip: {
                    value_type: 'individual',
                    shared: true
                },
                targets: block_write_count_columns.map((x) => {
                    return {
                        measurement: x,
                        target: 'SELECT mean("value") FROM "' + x + '" GROUP BY time(' + default_interval + ') fill(null)',
                        dsType: 'influxdb',
                        resultFormat: 'time_series',
                        query: 'SELECT mean("value")/' + telegraf_flush_rate + ' FROM "' + x + '" WHERE $timeFilter GROUP BY time(' + default_interval + ') fill(null)',
                        rawQuery: true
                    }
                })
            }
        ]
    });

    dashboard.rows.push({
        title: 'Unvalidated Transaction Queue Size',
        span: 12,
        type: 'graph',
        height: '300px',
        panels: [
            {
                title: 'Unvalidated Transaction Queue Size',
                span: 12,
                type: 'graph',
                lines: false,
                fill: 1,
                bars: true,
                stack: true,
                legend: {
                    show: false
                },
                grid: {leftMin: 0},
                tooltip: {
                    value_type: 'individual',
                    shared: true
                },
                targets: to_validate_queue.map((x) => {
                    return {
                        measurement: x,
                        target: 'SELECT mean("value") FROM "' + x + '" GROUP BY time(' + default_interval + ') fill(null)',
                        dsType: 'influxdb',
                        resultFormat: 'time_series',
                        query: 'SELECT mean("value") FROM "' + x + '" WHERE $timeFilter GROUP BY time(' + default_interval + ') fill(null)',
                        rawQuery: true
                    }
                })
            }
        ]
    });
}

function filter_columns(column_type, aggregation, data) {
    return data.results[0].series[0].values
    .filter((x) => {
        t = x[0].split('_');
        return t[0] === column_prefix && t[t.length - 1] === aggregation;
    })
    .map((x) => {
        return x[0];
    })
    .filter((x) => {
        return x.indexOf(column_type) > -1;
    });
}