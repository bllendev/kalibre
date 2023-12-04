LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

import os
ENVIRONMENT = os.environ.get("ENVIRONMENT", default="development")
if ENVIRONMENT == "production":
    # Add mail_admins handler for production environment
    LOGGING['handlers']['mail_admins'] = {
        'level': 'ERROR',
        'class': 'django.utils.log.AdminEmailHandler',
    }
    LOGGING['loggers']['django']['handlers'].append('mail_admins')


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
