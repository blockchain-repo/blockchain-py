
import os
import datetime
import logging.config
import bigchaindb

app_service_name = bigchaindb.config['app']['service_name']
app_setup_name = bigchaindb.config['app']['setup_name']
debug_to_console = "DEBUG" if bigchaindb.config['logger_config']['debug_to_console']==True else "INFO"
debug_to_file = "DEBUG" if bigchaindb.config['logger_config']['debug_to_file']==True else "INFO"

####log configure####
BASE_DIR = os.path.expandvars('$HOME')
LOG_DIR = os.path.join(BASE_DIR, "{}-log".format(app_service_name))
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR) 
PRO_LOG_FILE = "{}.log.{}".format(app_service_name, datetime.datetime.now().strftime("%Y%m%d%H%M%S"))

##log conf
LOG_CONF = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            'format': '%(asctime)s [%(name)s:%(lineno)d] [%(levelname)s] %(message)s'
        },
        'standard': {
            'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] [%(levelname)s] %(message)s'
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": debug_to_console,
            "formatter": "simple",
            "stream": "ext://sys.stdout"
        },
        "pro": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": debug_to_file,
            "formatter": "standard",
            "filename": os.path.join(LOG_DIR, PRO_LOG_FILE),
            'mode': 'w+',
            "maxBytes": 1024*1024*512,
            "backupCount": 20,
            "encoding": "utf8"
        }
    },
    "loggers": {
         "unichain": {
             "level": "INFO",
             "handlers": ["console", "pro"],
             "propagate": False
         }
    },
    "root": {
        'handlers': ["console","pro"],
        'level': "DEBUG",
        'propagate': False
    }
}
# root is in use

logging.config.dictConfig(LOG_CONF)
