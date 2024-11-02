import logging

# create logger
logger = logging.getLogger(__name__)

fh = logging.FileHandler("constrainthg.log")
fh.setLevel(logging.DEBUG)
logger.info('Package begin execution')

log_formatter = logging.Formatter(
    fmt="[{asctime} | {levelname}]: {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    )
fh.setFormatter(log_formatter)
logger.addHandler(fh)

logger.setLevel(logging.DEBUG)
