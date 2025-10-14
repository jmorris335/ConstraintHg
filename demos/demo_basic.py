from constrainthg.hypergraph import Hypergraph
import constrainthg.relations as R

# Initialize the hypergraph
hg = Hypergraph()

# Add edges to the hypergraph
# Syntax is add_edge(<sources>, <target>, <relation>)
hg.add_edge(['A', 'B'], 'C', R.Rsum)  # A + B = C
hg.add_edge('A', 'D', R.Rnegate)      # -A = D
hg.add_edge('B', 'E', R.Rnegate)      # -B = E
hg.add_edge(['D', 'E'], 'F', R.Rsum)  # D + E = F
hg.add_edge('F', 'C', R.Rnegate)      # -F = C

# Print all the possible paths for simulating C
print(hg.print_paths('C'))

# Perform two simulations for C from two different sets of inputs
print("**Inputs A and E**")
hg.solve('C', {'A':3, 'E':-7}, to_print=True)
print("**Inputs A and B**")
hg.solve('C', {'A':3, 'B':7}, to_print=True)
