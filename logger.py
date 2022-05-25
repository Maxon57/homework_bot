import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger('homework')
logger.setLevel(logging.DEBUG)
FORMAT = '%(asctime)s :: %(name)s:%(lineno)s :: %(levelname)s :: %(message)s'
handler = RotatingFileHandler(filename='my_logger.log',
                              maxBytes=5000000,
                              backupCount=5,
                              encoding='utf-8'
                              )
handler.setFormatter(logging.Formatter(FORMAT))
handler.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter(FORMAT))
stream_handler.setLevel(logging.INFO)
logger.addHandler(handler)
logger.addHandler(stream_handler)
logger.debug('Приложение бот-ассистент стартовало')