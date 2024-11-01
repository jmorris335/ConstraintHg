from config import runInPlace
runInPlace()

from src.constrainthg.hypergraph import Hypergraph
from src.constrainthg.relations import Rincrement

Hg = Hypergraph()
ab = Hg.addEdge('A', 'B', Rincrement)
cb = Hg.addEdge('A', 'C', Rincrement)
bd = Hg.addEdge('B', 'D', Rincrement)
bce = Hg.addEdge(['B', 'C'], 'E', Rincrement)
cg = Hg.addEdge('C', 'G', Rincrement)
ed = Hg.addEdge('E', 'D', Rincrement)
di = Hg.addEdge('D', 'I', Rincrement)
ij = Hg.addEdge('I', 'J', Rincrement)
# jt = Hg.addEdge('J', 'T', Rincrement)
edh = Hg.addEdge(['E', 'D'], 'H', Rincrement)
hj = Hg.addEdge('H', 'J', Rincrement)
hg = Hg.addEdge('H', 'G', Rincrement)
ht = Hg.addEdge('H', 'T', Rincrement)
# gt = Hg.addEdge('G', 'T', Rincrement)

# Hg.printPaths('T')

inputs = {'A': 1}
t, found_values = Hg.solve('T', inputs, toPrint=True)