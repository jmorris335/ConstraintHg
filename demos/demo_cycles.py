from config import runInPlace
runInPlace()

from src.constrainthg.hypergraph import Hypergraph
from src.constrainthg.relations import Rmean, Rincrement

hg = Hypergraph()
hg.addEdge('S', 'A', Rmean)
hg.addEdge('A', 'B', Rmean)
hg.addEdge('B', 'C', Rmean)
hg.addEdge('C', 'A', Rincrement)
hg.addEdge('A', 'T', Rmean, via=lambda a : a > 0)

Tval = hg.solve('T', {'S': 0}, toPrint=True)

print(f'T = {Tval}')