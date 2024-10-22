from config import runInPlace
runInPlace()

from src.constrainthg.hypergraph import Hypergraph
from src.constrainthg.relations import Rmean, Rincrement, Rfirst

hg = Hypergraph()
hg.addEdge('S', 'B', Rmean)
hg.addEdge('B', 'A', Rfirst, pseudo='index')
hg.addEdge('A', 'B', Rmean)
hg.addEdge('A', 'T', Rmean, via=lambda s1 : s1 > 3)

hg.printPaths('T')

Tval = hg.solve('T', {'S': 10}, toPrint=True)

print(f'T = {Tval}')