"""Utils for reading and setting configuration settings.

The value of each BigchainDB Server configuration setting is
determined according to the following rules:

* If it's set by an environment variable, then use that value
* Otherwise, if it's set in a local config file, then use that
  value
* Otherwise, use the default value (contained in
  ``bigchaindb.__init__``)
"""


import os
import copy
import json
import logging
import collections

from bigchaindb.common import exceptions
from bigchaindb.common.aes_crypt import ac

import bigchaindb


# TODO: move this to a proper configuration file for logging
logging.getLogger('requests').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

CONFIG_SERVER_PATH = os.environ.setdefault(
    'BIGCHAINDB_SERVER_CONFIG_PATH',
    os.path.join(os.path.expanduser('~'), '.{}'.format(bigchaindb.config['app']['server_config'])),
)
CONFIG_KEY_PATH = os.environ.setdefault(
    'BIGCHAINDB_KEY_CONFIG_PATH',
    os.path.join(os.path.expanduser('~'), '.{}'.format(bigchaindb.config['app']['key_config'])),
)
CONFIG_PARAM_PATH = os.environ.setdefault(
    'BIGCHAINDB_PARAM_CONFIG_PATH',
    os.path.join(os.path.expanduser('~'), '.{}'.format(bigchaindb.config['app']['param_config'])),
)


CONFIG_PREFIX = 'BIGCHAINDB'
CONFIG_SEP = '_'


def map_leafs(func, mapping):
    """Map a function to the leafs of a mapping."""

    def _inner(mapping, path=None):
        if path is None:
            path = []

        for key, val in mapping.items():
            if isinstance(val, collections.Mapping):
                _inner(val, path + [key])
            else:
                mapping[key] = func(val, path=path+[key])

        return mapping

    return _inner(copy.deepcopy(mapping))


# Thanks Alex <3
# http://stackoverflow.com/a/3233356/597097
def update(d, u):
    """Recursively update a mapping (i.e. a dict, list, set, or tuple).

    Conceptually, d and u are two sets trees (with nodes and edges).
    This function goes through all the nodes of u. For each node in u,
    if d doesn't have that node yet, then this function adds the node from u,
    otherwise this function overwrites the node already in d with u's node.

    Args:
        d (mapping): The mapping to overwrite and add to.
        u (mapping): The mapping to read for changes.

    Returns:
        mapping: An updated version of d (updated by u).
    """
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            r = update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


def file_config(server_filename=None,key_filename=None,param_filename=None):
    """Returns the config values found in a configuration file.

    Args:
        filename (str): the JSON file with the configuration values.
            If ``None``, CONFIG_DEFAULT_PATH will be used.

    Returns:
        dict: The config values in the specified config file (or the
              file at CONFIG_DEFAULT_PATH, if filename == None)
    """
    # logger.debug('On entry into file_config(), server_filename={},key_filename={},param_filename={}',format(server_filename),format(key_filename),format(param_filename))


# read server
    if server_filename is None:
        server_filename = CONFIG_SERVER_PATH
    logger.debug('file_config() will try to open `{}`'.format(server_filename))
    with open(server_filename) as f:
        try:
            server_config = json.load(f)
        except ValueError:
            pass
    logger.info('Configuration loaded from `{}`'.format(server_filename))

# read key
    if key_filename is None:
        key_filename = CONFIG_KEY_PATH
    logger.debug('file_config() will try to open `{}`'.format(key_filename))
    with open(key_filename) as f:
        try:
            key_config = json.load(f)
        except ValueError:
            with open(key_filename) as f:
                try:
                    line = f.readline()
                    de = ac.decrypt(line)
                    config = json.loads(de)
                except ValueError as err:
                    raise exceptions.ConfigurationError(
                        'Failed to parse the JSON/encrypt configuration from `{}`, {}'.format(key_filename, err)
                    )
            pass
    logger.info('Configuration loaded from `{}`'.format(key_filename))


# read param
    if param_filename is None:
        param_filename = CONFIG_PARAM_PATH
    logger.debug('file_config() will try to open `{}`'.format(param_filename))
    with open(param_filename) as f:
        try:
            param_config = json.load(f)
        except ValueError:
            pass
    logger.info('Configuration loaded from `{}`'.format(param_filename))

    # print("file_config   server_config:::",server_config)
    # print("file_config   key_config:::",key_config)
    # print("file_config   param_config:::",param_config)
    # TODO server_config + key_config + param_config  --> config ?
    config = dict(server_config, **key_config)
    config_all = dict(config, **param_config)

    print(config_all)
    return config_all


def env_config(config):
    """Return a new configuration with the values found in the environment.

    The function recursively iterates over the config, checking if there is
    a matching env variable. If an env variable is found, the func updates
    the configuration with that value.

    The name of the env variable is built combining a prefix (``BIGCHAINDB``)
    with the path to the value. If the ``config`` in input is:
    ``{'database': {'host': 'localhost'}}``
    this function will try to read the env variable ``BIGCHAINDB_DATABASE_HOST``.
    """

    def load_from_env(value, path):
        var_name = CONFIG_SEP.join([CONFIG_PREFIX] + list(map(lambda s: s.upper(), path)))
        return os.environ.get(var_name, value)

    return map_leafs(load_from_env, config)


def update_types(config, reference, list_sep=':'):
    """Return a new configuration where all the values types
    are aligned with the ones in the default configuration"""

    def _coerce(current, value):
        # Coerce a value to the `current` type.
        try:
            # First we try to apply current to the value, since it
            # might be a function
            return current(value)
        except TypeError:
            # Then we check if current is a list AND if the value
            # is a string.
            if isinstance(current, list) and isinstance(value, str):
                # If so, we use the colon as the separator
                return value.split(list_sep)

            try:
                # If we are here, we should try to apply the type
                # of `current` to the value
                return type(current)(value)
            except TypeError:
                # Worst case scenario we return the value itself.
                return value

    def _update_type(value, path):
        current = reference

        for elem in path:
            try:
                current = current[elem]
            except KeyError:
                return value

        return _coerce(current, value)

    return map_leafs(_update_type, config)


def set_config(config):
    """Set bigchaindb.config equal to the default config dict,
    then update that with whatever is in the provided config dict,
    and then set bigchaindb.config['CONFIGURED'] = True

    Args:
        config (dict): the config dict to read for changes
                       to the default config

    Note:
        Any previous changes made to ``bigchaindb.config`` will be lost.
    """
    # Deep copy the default config into bigchaindb.config
    bigchaindb.config = copy.deepcopy(bigchaindb._config)
    # Update the default config with whatever is in the passed config
    update(bigchaindb.config, update_types(config, bigchaindb.config))
    bigchaindb.config['CONFIGURED'] = True


def update_config(config):
    """Update bigchaindb.config with whatever is in the provided config dict,
    and then set bigchaindb.config['CONFIGURED'] = True

    Args:
        config (dict): the config dict to read for changes
                       to the default config
    """

    # Update the default config with whatever is in the passed config
    update(bigchaindb.config, update_types(config, bigchaindb.config))
    bigchaindb.config['CONFIGURED'] = True


def write_config(server_config,key_config,param_config, server_filename=None,key_filename=None,param_filename=None):
    """Write the provided configuration to a specific location.

    Args:
        config (dict): a dictionary with the configuration to load.
        filename (str): the name of the file that will store the new configuration. Defaults to ``None``.
            If ``None``, the HOME of the current user and the string ``.bigchaindb`` will be used.
    """

    if server_filename is None:
        server_filename = CONFIG_SERVER_PATH
    with open(server_filename, 'w') as f:
        json.dump(server_config, f, indent=4)

    if key_filename is None:
        key_filename = CONFIG_KEY_PATH
    with open(key_filename, 'w') as f:
        json.dump(key_config, f, indent=4)

    if param_filename is None:
        param_filename = CONFIG_PARAM_PATH
    with open(param_filename, 'w') as f:
        json.dump(param_config, f, indent=4)

def write_server_config(server_config,server_filename=None):
    """Write the provided configuration to a specific location.

    Args:
        config (dict): a dictionary with the configuration to load.
        filename (str): the name of the file that will store the new configuration. Defaults to ``None``.
            If ``None``, the HOME of the current user and the string ``.bigchaindb`` will be used.
    """

    if server_filename is None:
        server_filename = CONFIG_SERVER_PATH
    with open(server_filename, 'w') as f:
        json.dump(server_config, f, indent=4)


def write_key_config( key_config,  key_filename=None):
    """Write the provided configuration to a specific location.

    Args:
        config (dict): a dictionary with the configuration to load.
        filename (str): the name of the file that will store the new configuration. Defaults to ``None``.
            If ``None``, the HOME of the current user and the string ``.bigchaindb`` will be used.
    """
    if key_filename is None:
        key_filename = CONFIG_KEY_PATH
    with open(key_filename, 'w') as f:
        json.dump(key_config, f, indent=4)


def write_param_config(param_config,param_filename=None):
    """Write the provided configuration to a specific location.

    Args:
        config (dict): a dictionary with the configuration to load.
        filename (str): the name of the file that will store the new configuration. Defaults to ``None``.
            If ``None``, the HOME of the current user and the string ``.bigchaindb`` will be used.
    """
    if param_filename is None:
        param_filename = CONFIG_PARAM_PATH
    with open(param_filename, 'w') as f:
        json.dump(param_config, f, indent=4)


def write_config_encrypt(key_config, key_filename=None):
    """Write the provided configuration to a specific location.

    Args:
        config (dict): a dictionary with the configuration to load.
        filename (str): the name of the file that will store the new configuration. Defaults to ``None``.
            If ``None``, the HOME of the current user and the string ``.bigchaindb`` will be used.
    """
    if not key_filename:
        key_filename = CONFIG_KEY_PATH

    with open(key_filename, 'w') as f:
        encrypt_config = ac.encrypt(json.dumps(key_config))
        f.write(encrypt_config)


def autoconfigure(server_filename=None,key_filename=None,param_filename=None, config=None, force=False):
    """Run ``file_config`` and ``env_config`` if the module has not
    been initialized."""

    if not force and bigchaindb.config.get('CONFIGURED'):
        # logger.debug('System already configured, skipping autoconfiguration')
        return

    # start with the current configuration
    newconfig = bigchaindb.config

    # update configuration from file
    try:
        newconfig = update(newconfig, file_config(server_filename=server_filename,key_filename=key_filename,param_filename=param_filename))
    except FileNotFoundError as e:
        logger.warning('Cannot find config file `%s`.' % e.filename)

    # override configuration with env variables
    newconfig = env_config(newconfig)

    if config:
        newconfig = update(newconfig, config)

    set_config(newconfig)  # sets bigchaindb.config

if __name__ == '__main__':
    file_config()