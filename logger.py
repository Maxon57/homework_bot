import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)
log_format = '%(asctime)s :: %(name)s:%(lineno)s :: %(levelname)s :: %(message)s'
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(
    filename='logger.log',
    maxBytes=50000000,
    backupCount=5
)
handler.setFormatter(logging.Formatter(log_format))
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)
