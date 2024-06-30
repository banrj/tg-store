import logging

LOGGER_LEVEL = logging.DEBUG


logger = logging.Logger('main_logger')
logger.setLevel(LOGGER_LEVEL)

# file_handler = logging.FileHandler('my_app.log')
console_handler = logging.StreamHandler()
formatter = logging.Formatter('{asctime} {levelname:10} [{pathname} def {funcName}] ::: {message}', style='{')

# file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# logger.addHandler(file_handler)
logger.addHandler(console_handler)  # Optional: Display log messages in the console

dispatcher_loger = logging.Logger('yc')
dispatcher_loger.setLevel(LOGGER_LEVEL)
