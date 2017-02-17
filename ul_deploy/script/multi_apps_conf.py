
# from bigchaindb import _app_config

unichain_config = {}
with open('../../bigchaindb/__init__.py') as fp:
    exec(fp.read(), unichain_config)

if not unichain_config:
    _server_port = 9984
    _restore_server_port = 9986
    _service_name = "unichain"
    _setup_name = "UnichainDB"

else:
    base_unichain_config = unichain_config['_app_config']
    _service_name = base_unichain_config['service_name']
    _setup_name = base_unichain_config['setup_name']
    _server_port = base_unichain_config['server_port']
    _restore_server_port = base_unichain_config['restore_server_port']

app_config = {
    'server_port': _server_port,
    'restore_server_port': _restore_server_port,
    'service_name': _service_name,
    'setup_name': _setup_name,
}

