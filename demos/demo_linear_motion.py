from constrainthg.hypergraph import Hypergraph, Node
import constrainthg.relations as R

hg = Hypergraph()

# Nodes
v = Node('v', 1.3)
del_t = Node('time step', 1.0)
del_x = Node('delta x')
x = Node('x')
x0 = Node('x_0', 0.0)
i = Node('i')
xn = Node('x_n')

hg.add_edge([v, del_t], del_x, R.Rmultiply, label='vel*delta_t -> delta_x')
hg.add_edge([x, del_x], x, R.Rsum, label='x_i+delta_x -> x_i')
hg.add_edge({'s1': x, 's2':('s1', 'index')}, xn, R.equal('s1'), via=R.geq('s2', 4), label='x_i, i -> x_n')
hg.add_edge(x0, x, R.Rfirst, label='x0 -> x')

hg.print_paths(xn)

hg.solve(xn, toPrint=True)
