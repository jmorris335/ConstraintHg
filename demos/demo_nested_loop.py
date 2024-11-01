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
# hg.addEdge([A, C], A, R.Rsum)
hg.addEdge({
    's1': A,
    's2': C,
    's3': ('s1', 'index'), 
    's4': ('s2', 'index')}, A,
    lambda s1, s2, **kwargs : sum((s1, s2)),
    via=lambda s3, s4, **kwargs : s3 == s4 + 0)
hg.addEdge(A, T, R.Rfirst, via=lambda s1, **kwargs : s1 >= 3)

tval, _ = hg.solve(T, toPrint=False)

print(tval)