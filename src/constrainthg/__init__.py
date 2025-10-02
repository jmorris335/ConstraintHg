'''
ConstraintHg
============

A kernel for systems modeling and simulation.
'''

__copyright__ = 'Copyright (c) 2025 John Morris'
__license__ = 'Licensed under the Apache License, Version 2.0'
__title__ = 'constrainthg'
__all__ = ['hypergraph', 'relations']

import logging

from constrainthg.hypergraph import *
import constrainthg.relations as R

logger = logging.getLogger('constrainthg')
logger.addHandler(logging.NullHandler())
