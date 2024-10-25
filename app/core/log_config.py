import logging

from app import settings as app_config


logger = logging.Logger('main_logger')
logger.setLevel(app_config.LOGGER_LEVEL)

# file_handler = logging.FileHandler('my_app.log')
console_handler = logging.StreamHandler()
formatter = logging.Formatter('{asctime} {levelname} [{funcName}] ::: {message}', style='{')

# file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# logger.addHandler(file_handler)
logger.addHandler(console_handler)  # Optional: Display log messages in the console