from constrainthg import *
from constrainthg.hypergraph import *

import pytest

class TestPackage:
    def test_package_wildcard_imports(self):
        """tests wildcard (*) imports using all dunder."""
        assert isinstance(hypergraph.Hypergraph(), hypergraph.Hypergraph)

    def test_hypergraph_wildcard_imports(self):
        """tests wildcard (*) imports for hypergraph module."""
        a, b = Node('label_a'), Node('label_b')
        assert isinstance(TNode('label', 'node_label'), TNode)
        assert isinstance(a, Node)
        assert isinstance(Edge('label', a, b, lambda *a : True), Edge)
        assert isinstance(Hypergraph(), Hypergraph)