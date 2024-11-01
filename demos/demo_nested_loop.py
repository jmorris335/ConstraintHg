from constrainthg.hypergraph import Hypergraph, Node
import constrainthg.relations as R

hg = Hypergraph()

A = Node('A')
B = Node('B')
C = Node('C')
S = Node('S', 0)
T = Node('T')

hg.addEdge(S, A, R.Rfirst)
hg.addEdge(A, B, R.Rincrement)
hg.addEdge(B, C, R.Rincrement)
hg.addEdge([A, C], A, R.Rsum, edge_props='LEVEL')
hg.addEdge(A, T, R.Rfirst, via=R.geq('s1', 7))

tval, _ = hg.solve(T, toPrint=True)

print(tval)