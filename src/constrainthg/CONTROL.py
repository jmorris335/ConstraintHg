import logging

CYCLE_SEARCH_DEPTH = 1000
"""Maximum times to sequence a cycle before declaring it void."""

lg = logging.getLogger('Hypergraph')
lg.level = logging.DEBUG