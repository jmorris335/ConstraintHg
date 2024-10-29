from config import runInPlace
runInPlace()

from src.constrainthg.hypergraph import Hypergraph, Node
import src.constrainthg.relations as R

hg = Hypergraph()

# Nodes
v = Node('v', 1.3)
del_t = Node('time step', 1.0)
del_x = Node('delta x')
x = Node('x')
x0 = Node('x_0', 0.0)
i = Node('i')
xn = Node('x_n')

# Functions
def cycleCounter(s2, *args, **kwargs):
    return s2 > 4

hg.addEdge([v, del_t], del_x, R.Rmultiply, label='vel*delta_t -> delta_x')
hg.addEdge([x, del_x], x, R.Rsum, label='x_i+delta_x -> x_i')
hg.addEdge({'s1': x, 's2':('s1', 'index')}, xn, R.equal('s1'), via=cycleCounter, label='x_i, i -> x_n')
hg.addEdge(x0, x, R.Rfirst, label='x0 -> x')

hg.printPaths(xn)

hg.solve(xn, toPrint=True)
