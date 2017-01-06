
import os
import sys
import datetime
import logging
import logging.config

####log configure####
BASE_DIR = os.path.expandvars('$HOME')
LOG_DIR = os.path.join(BASE_DIR, "unichain_order_log")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR) 
PRO_LOG_FILE = "unichain_order.log." + datetime.datetime.now().strftime("%Y%m%d%H%M%S")

LOG_CONF = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            'format': '%(asctime)s [%(name)s:%(lineno)d] [%(levelname)s]- %(message)s'
        },
        'standard': {
            'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] [%(levelname)s]- %(message)s'
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple",
            "stream": "ext://sys.stdout"
        },
        "pro": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
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
             "propagate": True
         }
    },
    "root": {
        'handlers': ["console","pro"],
        'level': "DEBUG",
        'propagate': False
    }
}
logging.config.dictConfig(LOG_CONF)
