from config import runInPlace
runInPlace()

from src.constrainthg.hypergraph import Hypergraph
from src.constrainthg.relations import Rmean, Rincrement

hg = Hypergraph()

hg.addEdge('A', 'T', Rmean, via=lambda s1 : s1 > 3)
hg.addEdge('S', 'A', Rmean)
hg.addEdge('A', 'A', Rincrement)

hg.printPaths('T')

hg.solve('T', {'S': 0}, toPrint=True)