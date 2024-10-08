if not __package__:
    import os
    import sys
    package_source_path = os.path.dirname(os.path.dirname(__file__))
    sys.path.insert(0, package_source_path)

from src.constrainthg.hypergraph import Hypergraph

def rel_increment(*source):
    return max(source) + 1

Hg = Hypergraph()
ab = Hg.addEdge('A', 'B', rel_increment)
cb = Hg.addEdge('A', 'C', rel_increment)
bd = Hg.addEdge('B', 'D', rel_increment)
bce = Hg.addEdge(['B', 'C'], 'E', rel_increment)
cg = Hg.addEdge('C', 'G', rel_increment)
ed = Hg.addEdge('E', 'D', rel_increment)
di = Hg.addEdge('D', 'I', rel_increment)
ij = Hg.addEdge('I', 'J', rel_increment)
jt = Hg.addEdge('J', 'T', rel_increment)
edh = Hg.addEdge(['E', 'D'], 'H', rel_increment)
hj = Hg.addEdge('H', 'J', rel_increment)
hg = Hg.addEdge('H', 'G', rel_increment)
ht = Hg.addEdge('H', 'T', rel_increment)
gt = Hg.addEdge('G', 'T', rel_increment)

# Hg.printPaths('T')

inputs = {'A': 1}
Tval = Hg.DFS(inputs, 'T', toPrint=True)

print(f'T = {Tval}')