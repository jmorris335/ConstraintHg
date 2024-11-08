from constrainthg.hypergraph import Hypergraph
import constrainthg.relations as R

hg = Hypergraph()
hg.add_edge(['A', 'B'], 'C', R.Rsum)
hg.add_edge('A', 'D', R.Rnegate)
hg.add_edge('B', 'E', R.Rnegate)
hg.add_edge(['D', 'E'], 'F', R.Rsum)
hg.add_edge('F', 'C', R.Rnegate)

print(hg.print_paths('C'))

print("**Inputs A and E**")
hg.solve('C', {'A':3, 'E':-7}, to_print=True)
print("**Inputs A and B**")
hg.solve('C', {'A':3, 'B':7}, to_print=True)
