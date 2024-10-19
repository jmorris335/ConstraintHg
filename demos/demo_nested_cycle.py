from config import runInPlace
runInPlace()

from src.constrainthg.hypergraph import Hypergraph
from src.constrainthg.relations import Rmean, Rincrement

#Independent Cycles
independent = Hypergraph()
independent.addEdge('S', 'C', Rmean)
independent.addEdge('C', 'B', Rmean)
independent.addEdge('B', 'A', Rincrement)
independent.addEdge('A', 'T', Rmean, via=lambda s1 : s1 > 2)
independent.addEdge('C', 'F', Rmean)
independent.addEdge('F', 'G', Rmean)
independent.addEdge('G', 'C', Rincrement)
independent.addEdge('B', 'D', Rmean)
independent.addEdge('D', 'E', Rmean)
independent.addEdge('E', 'B', Rincrement)

#Overlapping Cycles
overlapping = Hypergraph()
overlapping.addEdge('S', 'C', Rmean)
overlapping.addEdge('A', 'B', Rmean)
overlapping.addEdge('B', 'C', Rincrement)
overlapping.addEdge('C', 'D', Rmean)
overlapping.addEdge('D', 'A', Rmean)
overlapping.addEdge('C', 'A', Rmean)
overlapping.addEdge('A', 'T', Rmean, via=lambda s1 : s1 > 2)

#Conjoined Cycles
conjoined = Hypergraph()
conjoined.addEdge('S', 'C', Rmean)
conjoined.addEdge('A', 'B', Rmean)
conjoined.addEdge('B', 'C', Rincrement)
conjoined.addEdge('B', 'D', Rmean)
conjoined.addEdge('D', 'E', Rmean)
conjoined.addEdge('E', 'B', Rincrement)
conjoined.addEdge('C', 'A', Rmean)
conjoined.addEdge('A', 'T', Rmean, via=lambda s1 : s1 > 2)

#Hyperloop
hyperloop = Hypergraph()
hyperloop.addEdge('S', 'B', Rmean)
hyperloop.addEdge(['A', 'B'], 'A', Rincrement)
hyperloop.addEdge('A0', 'A', Rmean)
hyperloop.addEdge('A', 'T', Rmean, via=lambda s1 : s1 > 2)

hyperloop.printPaths('T')

Tval = hyperloop.solve('T', {'S': 0, 'A0': 0}, toPrint=True)