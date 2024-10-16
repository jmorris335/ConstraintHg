from config import runInPlace
runInPlace()

from src.constrainthg.hypergraph import Hypergraph, Node
import src.constrainthg.relations as R

hg = Hypergraph()

# Nodes
v = Node('velocity', 1.0)
del_t = Node('time step', 1.0)
del_x = Node('delta x')
x = Node('position')
x0 = Node('initial position', 0.0)
i = Node('index', 0)
xn = Node('final position')

# Functions
def cycleCounter(*args, **kwargs):
    args, kwargs = R.getKeywordArguments(args, kwargs, 's2')
    return kwargs['s2'] > 3

hg.addEdge([v, del_t], del_x, R.Rmultiply, label='set delta x')
hg.addEdge([x, del_x], x, R.Rsum, label='set x_i')
hg.addEdge([x, i], xn, R.Rfirst, via=cycleCounter, identify={x: 's1', i: 's2'}, label='set x_n')
hg.addEdge(x, i, R.Rfirst)
hg.addEdge(x0, x, R.Rfirst)

# hg.printPaths(xn)

hg.solve(xn, toPrint=True)
