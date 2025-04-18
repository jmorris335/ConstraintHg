"""Initialization file for ConstraintHg."""

import logging

from constrainthg.hypergraph import *
import constrainthg.relations as R

logger = logging.getLogger('constrainthg')
logger.addHandler(logging.NullHandler())
