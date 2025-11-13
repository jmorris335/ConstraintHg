from constrainthg.hypergraph import Hypergraph
from constrainthg import relations as R

import pytest

class TestHypergraphBehavior():
    def test_simple_add(self):
        hg = Hypergraph()
        hg.add_edge(['A', 'B'], 'C', R.Rsum)
        t = hg.solve('C', {'A': 100, 'B': 12.9},)
        assert t.value == 112.9, "Sum should be 112.9"

    def test_simple_multiply(self):
        hg = Hypergraph()
        hg.add_edge(['A', 'B'], 'C', R.Rmultiply)
        t = hg.solve('C', {'A': 3, 'B': 1.5},)
        assert t.value == 4.5, "Product should be 4.5"

    def test_simple_subtract(self):
        hg = Hypergraph()
        hg.add_edge({'s1':'A', 's2':'B'}, 'C', R.Rsubtract)
        t = hg.solve('C', {'A': 3, 'B': 2})
        assert t.value == 1, "Subtraction should be 1"

    def test_simple_void(self):
        hg = Hypergraph()
        via_le10 = lambda *args, **kwargs : all([s < 10 for s in R.extend(args, kwargs)])
        hg.add_edge(['A', 'B'], 'C', R.Rsum, via=via_le10)
        t = hg.solve('C', {'A': 100, 'B': 51})
        assert t == None, "Should have invalid condition"

    def test_branching(self):
        """Tests hyperedges and complex branching."""
        hg = Hypergraph()
        hg.add_edge('A', 'B', R.Rincrement)
        hg.add_edge('A', 'C', R.Rincrement)
        hg.add_edge('B', 'D', R.Rincrement)
        hg.add_edge(['B', 'C'], 'E', R.Rincrement)
        hg.add_edge('E', 'D', R.Rincrement)
        hg.add_edge('C', 'G', R.Rincrement)
        hg.add_edge('D', 'I', R.Rincrement)
        hg.add_edge('I', 'J', R.Rincrement)
        hg.add_edge('J', 'T', R.Rincrement)
        hg.add_edge(['E', 'D'], 'H', R.Rincrement)
        hg.add_edge('H', 'J', R.Rincrement)
        hg.add_edge('H', 'G', R.Rincrement)
        hg.add_edge('H', 'T', R.Rincrement)
        # hg.add_edge('G', 'T', R.Rincrement)
        t = hg.solve('T', {'A': 1})
        assert t.value == 6
        assert t.cost == 5

    def test_cycles_simple(self):
        """Tests that cycles can be solved."""
        hg = Hypergraph()
        hg.add_edge('A', 'B', R.Rmean)
        hg.add_edge('S', 'B', R.Rmean)
        hg.add_edge('B', 'C', R.Rincrement)
        hg.add_edge('C', 'A', R.Rmean)
        hg.add_edge('A', 'T', R.Rmean, via=lambda a : a > 5)
        t = hg.solve('T', {'S': 0})
        assert t.value == 6

    def test_loops(self):
        """Tests simple loops."""
        hg = Hypergraph()
        hg.add_edge('A', 'T', R.Rmean, via=R.geq('s1', 3))
        hg.add_edge('S', 'A', R.Rmean)
        hg.add_edge('A', 'A', R.Rincrement)

        t = hg.solve('T', {'S': 0})
        assert t.value == 3
        assert t.cost == 5

    def test_independent_cycles(self):
        """Two nested cycles that are completely peripheral to the outer cycle."""
        hg = Hypergraph()
        hg.add_edge('S', 'C', R.Rmean)
        hg.add_edge('C', 'B', R.Rmean)
        hg.add_edge('B', 'A', R.Rincrement)
        hg.add_edge('A', 'T', R.Rmean, via=lambda s1 : s1 > 2)
        hg.add_edge('C', 'F', R.Rmean)
        hg.add_edge('F', 'G', R.Rmean)
        hg.add_edge('G', 'C', R.Rincrement)
        hg.add_edge('B', 'D', R.Rmean)
        hg.add_edge('D', 'E', R.Rmean)
        hg.add_edge('E', 'B', R.Rincrement)

        t = hg.solve('T', {'S': 0})
        assert t.value == 3
        assert t.cost == 10

    def test_overlapping_cycles(self):
        """A cycle that has the same start and entry point as a greater cycle."""
        hg = Hypergraph()
        hg.add_edge('S', 'C', R.Rmean)
        hg.add_edge('A', 'B', R.Rmean)
        hg.add_edge('B', 'C', R.Rincrement)
        hg.add_edge('C', 'D', R.Rmean)
        hg.add_edge('D', 'A', R.Rmean)
        hg.add_edge('C', 'A', R.Rmean)
        hg.add_edge('A', 'T', R.Rmean, via=lambda s1 : s1 > 2)

        t = hg.solve('T', {'S': 0})
        assert t.value == 3
        assert t.cost == 12

    def test_conjoined_cycles(self):
        """Two cycles that are conjoined at a single node (figure eight)."""
        hg = Hypergraph()
        hg.add_edge('S', 'C', R.Rmean)
        hg.add_edge('A', 'B', R.Rmean)
        hg.add_edge('B', 'C', R.Rincrement, via=lambda s1 : s1 % 3 == 0)
        hg.add_edge('B', 'D', R.Rmean)
        hg.add_edge('D', 'E', R.Rmean)
        hg.add_edge('E', 'B', R.Rincrement)
        hg.add_edge('C', 'A', R.Rmean)
        hg.add_edge('A', 'T', R.Rmean, via=R.geq('s1', 3))

        t = hg.solve('T', {'S': 0})
        assert t.value == 4
        assert t.cost == 15

    def test_hyperloop_cycles(self):
        """A cycle with a hyperedge."""
        hg = Hypergraph()
        hg.add_edge('S0', 'B', R.Rmean)
        hg.add_edge(['A', 'B'], 'A', R.Rincrement)
        hg.add_edge('S1', 'A', R.Rmean)
        hg.add_edge('A', 'T', R.Rmean, via=R.geq('s1', 4))

        t = hg.solve('T', {'S0': 0, 'S1': 0})
        assert t.value == 4
        assert t.cost == 7

    def test_reuse_cycles(self):
        """Example showing cycle path switching."""
        hg = Hypergraph()
        hg.add_edge('S1', 'A', R.Rmean)
        hg.add_edge('A', 'C', R.Rmean)
        hg.add_edge('C', 'A', R.Rincrement, index_offset=1)
        hg.add_edge('S2', 'B', R.Rmean)
        hg.add_edge('B', 'C', R.Rmean)
        hg.add_edge('C', 'B', R.Rmean, index_offset=1)
        hg.add_edge(['A', 'B'], 'T', R.Rsum, via=lambda s1, s2 : min(s1, s2) >= 5)

        t = hg.solve('T', {'S1': 1, 'S2': 4})
        print(t.get_tree())
        assert t.value == 10
        assert t.cost == 6

    def test_nested_loop(self):
        """A loop nested in a cycle."""
        hg = Hypergraph()
        hg.add_edge('S', 'A', R.Rfirst)
        hg.add_edge('A', 'B', R.Rincrement)
        hg.add_edge('B', 'C', R.Rincrement)
        hg.add_edge(['A', 'C'], 'A', R.Rsum, edge_props='LEVEL', index_offset=1)
        hg.add_edge('A', 'T', R.Rfirst, via=R.geq('s1', 7))

        t = hg.solve('T', {'S': 0})
        assert t.value == 14
        assert t.cost == 11

    def test_indexing(self):
        """Tests a cycle with basic indexing."""
        hg = Hypergraph()
        hg.add_edge('S', 'B', R.Rmean)
        hg.add_edge({'s1':'B', 's2': ('s1', 'index')}, 'A', R.equal('s2'))
        hg.add_edge('A', 'B', R.Rmean, index_offset=1)
        hg.add_edge('A', 'T', R.Rmean, via=R.geq('s1', 4))

        t = hg.solve('T', {'S': 10})
        assert t.value == 4
        assert t.cost == 9

    def test_edge_order_irrelevant(self):
        """Tests that the order in which edges are provided does not affect the graphs
        searchability."""
        hg = Hypergraph()
        hg.add_edge('S', 'D', R.Rincrement)
        hg.add_edge('S', 'A', R.Rincrement)
        hg.add_edge('A', 'B', R.Rincrement, label='ZZZ')
        hg.add_edge(['A', 'B'], 'C', R.Rincrement, label='AAA')
        hg.add_edge({'d': 'D', 'c': 'C'}, 'T', R.Rincrement)
        t, i = 1, 1
        while t is not None and i < 50:
            t = hg.solve('T', {'S': 1})
            i += 1
        assert i == 50, "Configurations may have been non-deterministic"
        assert t is not None, "Solution should always be discoverable"
        assert t.value == 5, "Graph calculation is incorrect"