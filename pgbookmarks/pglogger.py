import logging


def get_logger(log_level):
    logger = logging.getLogger()
    stream_handler = logging.StreamHandler()

    formatter = logging.Formatter(
        '[%(levelname)8s] %(name)29s |%(funcName)27s:%(lineno)4s| %(message)s')

    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    logger.setLevel(log_level)

    return logger


logger = get_logger(logging.WARN)
