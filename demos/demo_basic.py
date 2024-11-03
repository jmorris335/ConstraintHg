from constrainthg.hypergraph import Hypergraph
import constrainthg.relations as R

hg = Hypergraph()
hg.addEdge(['A', 'B'], 'C', R.Rsum)
hg.addEdge('A', 'D', R.Rnegate)
hg.addEdge('B', 'E', R.Rnegate)
hg.addEdge(['D', 'E'], 'F', R.Rsum)
hg.addEdge('F', 'C', R.Rnegate)

print("**Inputs A and E**")
hg.solve('C', {'A':3, 'E':-7}, toPrint=True)
print("**Inputs A and B**")
hg.solve('C', {'A':3, 'B':7}, toPrint=True)
