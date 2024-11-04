from src.constrainthg.hypergraph import *
import src.constrainthg.relations as R

import logging

logger = logging.getLogger(__name__)

fh = logging.FileHandler("constrainthg.log")
fh.setLevel(logging.INFO)
logger.info('Package begin execution')

log_formatter = logging.Formatter(
    fmt="[{asctime} | {levelname}]: {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
    )
fh.setFormatter(log_formatter)
logger.addHandler(fh)

logger.setLevel(logging.INFO)
