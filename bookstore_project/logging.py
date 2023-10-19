# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# logging decorator
import functools
import logging

logger = logging.getLogger(__name__)

def log(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        logger.info(f"Entering function {f.__name__}")
        result = f(*args, **kwargs)
        logger.info(f"Exiting function {f.__name__}")
        return result
    return wrapper
