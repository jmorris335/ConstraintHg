from config import runInPlace
runInPlace()

from src.constrainthg.hypergraph import Hypergraph
from src.constrainthg.relations import Rmean, Rincrement

hg = Hypergraph()
hg.addEdge('S', 'B', Rmean)
hg.addEdge('A', 'B', Rmean)
hg.addEdge('B', 'C', Rincrement)
hg.addEdge('C', 'A', Rmean)
hg.addEdge('A', 'T', Rmean, via=lambda a : a > 1)

hg.printPaths('T')

Tval = hg.solve('T', {'S': 0}, toPrint=True)

print(f'T = {Tval}')