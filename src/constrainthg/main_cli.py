"""Main caller for ConstaintHg, showing a basic demo."""

from constrainthg.hypergraph import Hypergraph
from constrainthg import relations as R

print("ConstraintHg, a kernel for systems modeling and simulation...\n")
print("Demo:")

hg = Hypergraph(setup_logger=True)
hg.add_edge(['A', 'B'], 'C', R.Rsum)
hg.add_edge('A', 'D', R.Rnegate)
hg.add_edge('B', 'E', R.Rnegate)
hg.add_edge(['D', 'E'], 'F', R.Rsum)
hg.add_edge('F', 'C', R.Rnegate)

print(hg.print_paths('C'))

print("**Inputs A and E**")
hg.solve('C', {'A': 3, 'E': -7}, to_print=True)
print("**Inputs A and B**")
hg.solve('C', {'A': 3, 'B': 7}, to_print=True)
