"""Main caller for ConstaintHg, showing a basic demo."""

from constrainthg.hypergraph import Hypergraph
from constrainthg import relations as R

print("ConstraintHg, a hypergraph modeling toolbox for systems engineering...\n")
print("Demo:")

hg = Hypergraph()
hg.addEdge(['A', 'B'], 'C', R.Rsum)
hg.addEdge('A', 'D', R.Rnegate)
hg.addEdge('B', 'E', R.Rnegate)
hg.addEdge(['D', 'E'], 'F', R.Rsum)
hg.addEdge('F', 'C', R.Rnegate)

print(hg.printPaths('C'))

print("**Inputs A and E**")
hg.solve('C', {'A':3, 'E':-7}, toPrint=True)
print("**Inputs A and B**")
hg.solve('C', {'A':3, 'B':7}, toPrint=True)
