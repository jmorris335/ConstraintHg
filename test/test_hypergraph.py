from src.constrainthg.hypergraph import Hypergraph
import src.constrainthg.relations as R

class TestSimple():
    def test_simple_add(self):
        hg = Hypergraph()
        hg.addEdge(['A', 'B'], 'C', R.Rsum)
        inputs = {'A': 100, 'B': 12.9}
        assert hg.solve(inputs, 'C') == 112.9, "Sum should be 112.9"

    def test_simple_multiply(self):
        hg = Hypergraph()
        hg.addEdge(['A', 'B'], 'C', R.Rmultiply)
        inputs = {'A': 3, 'B': 1.5}
        assert hg.solve(inputs, 'C') == 4.5, "Product should be 4.5"

    def test_simple_subtract(self):
        hg = Hypergraph()
        hg.addEdge(['A', 'B'], 'C', R.Rsubtract)
        inputs = {'A': 3, 'B': 2}
        assert hg.solve(inputs, 'C') == 1, "Product should be 4.5"

    def test_simple_void(self):
        hg = Hypergraph()
        via_le10 = lambda *source : all([s < 10 for s in source])
        hg.addEdge(['A', 'B'], 'C', R.Rsum, via=via_le10)
        inputs = {'A': 100, 'B': 51}
        assert hg.solve(inputs, 'C') == None, "Should have invalid condition"
