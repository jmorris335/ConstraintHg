from constrainthg.hypergraph import Hypergraph
from constrainthg import relations as R

class TestHypergraph():
    def test_simple_add(self):
        hg = Hypergraph()
        hg.addEdge(['A', 'B'], 'C', R.Rsum)
        t, fv = hg.solve('C', {'A': 100, 'B': 12.9},)
        assert t.value == 112.9, "Sum should be 112.9"

    def test_simple_multiply(self):
        hg = Hypergraph()
        hg.addEdge(['A', 'B'], 'C', R.Rmultiply)
        t, fv = hg.solve('C', {'A': 3, 'B': 1.5},)
        assert t.value == 4.5, "Product should be 4.5"

    def test_simple_subtract(self):
        hg = Hypergraph()
        hg.addEdge(['A', 'B'], 'C', R.Rsubtract)
        t, fv = hg.solve('C', {'A': 3, 'B': 2},)
        assert t.value == 1, "Product should be 4.5"

    def test_simple_void(self):
        hg = Hypergraph()
        via_le10 = lambda *args, **kwargs : all([s < 10 for s in R.extend(args, kwargs)])
        hg.addEdge(['A', 'B'], 'C', R.Rsum, via=via_le10)
        t, fv = hg.solve('C', {'A': 100, 'B': 51})
        assert t == None, "Should have invalid condition"

    def test_branching(self):
        """Tests hyperedges and complex branching."""
        hg = Hypergraph()
        hg.addEdge('A', 'B', R.Rincrement)
        hg.addEdge('A', 'C', R.Rincrement)
        hg.addEdge('B', 'D', R.Rincrement)
        hg.addEdge(['B', 'C'], 'E', R.Rincrement)
        hg.addEdge('E', 'D', R.Rincrement)
        hg.addEdge('C', 'G', R.Rincrement)
        hg.addEdge('D', 'I', R.Rincrement)
        hg.addEdge('I', 'J', R.Rincrement)
        hg.addEdge('J', 'T', R.Rincrement)
        hg.addEdge(['E', 'D'], 'H', R.Rincrement)
        hg.addEdge('H', 'J', R.Rincrement)
        hg.addEdge('H', 'G', R.Rincrement)
        hg.addEdge('H', 'T', R.Rincrement)
        # hg.addEdge('G', 'T', R.Rincrement)
        t, fv = hg.solve('T', {'A': 1})
        assert t.value == 6
        assert t.cost == 5

    def test_cycles_simple(self):
        """Tests that cycles can be solved."""
        hg = Hypergraph()
        hg.addEdge('A', 'B', R.Rmean)
        hg.addEdge('S', 'B', R.Rmean)
        hg.addEdge('B', 'C', R.Rincrement)
        hg.addEdge('C', 'A', R.Rmean)
        hg.addEdge('A', 'T', R.Rmean, via=lambda a : a > 5)
        t, fv = hg.solve('T', {'S': 0})
        assert t.value == 6

    def test_loops(self):
        """Tests simple loops."""
        hg = Hypergraph()
        hg.addEdge('A', 'T', R.Rmean, via=R.geq('s1', 3))
        hg.addEdge('S', 'A', R.Rmean)
        hg.addEdge('A', 'A', R.Rincrement)

        t, fv = hg.solve('T', {'S': 0})
        assert t.value == 4
        assert t.cost == 6

    def test_independent_cycles(self):
        """Two nested cycles that are completely peripheral to the outer cycle."""
        hg = Hypergraph()
        hg.addEdge('S', 'C', R.Rmean)
        hg.addEdge('C', 'B', R.Rmean)
        hg.addEdge('B', 'A', R.Rincrement)
        hg.addEdge('A', 'T', R.Rmean, via=lambda s1 : s1 > 2)
        hg.addEdge('C', 'F', R.Rmean)
        hg.addEdge('F', 'G', R.Rmean)
        hg.addEdge('G', 'C', R.Rincrement)
        hg.addEdge('B', 'D', R.Rmean)
        hg.addEdge('D', 'E', R.Rmean)
        hg.addEdge('E', 'B', R.Rincrement)

        t, fv = hg.solve('T', {'S': 0})
        assert t.value == 3
        assert t.cost == 10

    def test_overlapping_cycles(self):
        """A cycle that has the same start and entry point as a greater cycle."""
        hg = Hypergraph()
        hg.addEdge('S', 'C', R.Rmean)
        hg.addEdge('A', 'B', R.Rmean)
        hg.addEdge('B', 'C', R.Rincrement)
        hg.addEdge('C', 'D', R.Rmean)
        hg.addEdge('D', 'A', R.Rmean)
        hg.addEdge('C', 'A', R.Rmean)
        hg.addEdge('A', 'T', R.Rmean, via=lambda s1 : s1 > 2)

        t, fv = hg.solve('T', {'S': 0})
        assert t.value == 3
        assert t.cost == 12

    def test_conjoined_cycles(self):
        """Two cycles that are conjoined at a single node (figure eight)."""
        hg = Hypergraph()
        hg.addEdge('S', 'C', R.Rmean)
        hg.addEdge('A', 'B', R.Rmean)
        hg.addEdge('B', 'C', R.Rincrement, via=lambda s1 : s1 % 3 == 0)
        hg.addEdge('B', 'D', R.Rmean)
        hg.addEdge('D', 'E', R.Rmean)
        hg.addEdge('E', 'B', R.Rincrement)
        hg.addEdge('C', 'A', R.Rmean)
        hg.addEdge('A', 'T', R.Rmean, via=R.geq('s1', 3))

        t, fv = hg.solve('T', {'S': 0})
        assert t.value == 4
        assert t.cost == 15

    def test_hyperloop_cycles(self):
        """A cycle with a hyperedge."""
        hg = Hypergraph()
        hg.addEdge('S0', 'B', R.Rmean)
        hg.addEdge(['A', 'B'], 'A', R.Rincrement)
        hg.addEdge('S1', 'A', R.Rmean)
        hg.addEdge('A', 'T', R.Rmean, via=R.geq('s1', 3))

        t, fv = hg.solve('T', {'S0': 0, 'S1': 0})
        assert t.value == 4
        assert t.cost == 7

    def test_reuse_cycles(self):
        """Example showing cycle path switching."""
        hg = Hypergraph()
        hg.addEdge('S1', 'A', R.Rmean)
        hg.addEdge('A', 'C', R.Rmean)
        hg.addEdge('C', 'A', R.Rincrement)
        hg.addEdge('S2', 'B', R.Rmean)
        hg.addEdge('B', 'C', R.Rmean)
        hg.addEdge('C', 'B', R.Rmean)
        hg.addEdge(['A', 'B'], 'T', R.Rsum, via=lambda s1, s2 : min(s1, s2) > 5)

        t, fv = hg.solve('T', {'S1': 1, 'S2': 4})
        assert t.value == 12
        assert t.cost == 8

    def test_nested_loop(self):
        """A loop nested in a cycle."""
        hg = Hypergraph()
        hg.addEdge('S', 'A', R.Rfirst)
        hg.addEdge('A', 'B', R.Rincrement)
        hg.addEdge('B', 'C', R.Rincrement)
        hg.addEdge(['A', 'C'], 'A', R.Rsum, edge_props='LEVEL')
        hg.addEdge('A', 'T', R.Rfirst, via=R.geq('s1', 7))

        t, fv = hg.solve('T', {'S': 0})
        assert t.value == 14
        assert t.cost == 11