from src.constrainthg.hypergraph import Hypergraph
import src.constrainthg.relations as R

class TestCycles:
    hg = Hypergraph()
    hg.addEdge('A', 'B', R.Rmean)
    hg.addEdge('S', 'B', R.Rmean)
    hg.addEdge('B', 'C', R.Rincrement)
    hg.addEdge('C', 'A', R.Rmean)
    hg.addEdge('A', 'T', R.Rmean, via=lambda a : a > 5)

    def test_cycles_simple(self):
        assert self.hg.solve('T', {'S': 0}, toPrint=True) == 6