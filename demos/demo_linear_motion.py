"""
This script demonstrates a basic cycle, and using the index of a node to
break the cycle. The system being modeled is a body moving at constant
velocity, where we want to estimate the position of the body after ``n``
seconds.
"""

from constrainthg.hypergraph import Hypergraph
import constrainthg.relations as R

hg = Hypergraph()

# Nodes
velocity = hg.add_node('velocity', description='constant velocity')
delta_t = hg.add_node('delta_t', description='time step')
delta_x = hg.add_node('delta_x', description='distance moved per step')
x = hg.add_node('x', description='current position')
xn = hg.add_node('x_n', description='final position')
n = hg.add_node('n', description='maximum index to stop on')

# Edges
hg.add_edge(
    sources=[velocity, delta_t],
    target=delta_x,
    rel=R.Rmultiply,
    label='vel*delta_t -> delta_x',
)
hg.add_edge(
    sources=[x, delta_x],
    target=x,
    rel=R.Rsum,
    index_offset=1,
    label='x_i+delta_x -> x_i',
)
hg.add_edge(
    sources={'x': x, 'i': ('x', 'index'), 'n': n},
    target=xn,
    rel=R.Rfirst,
    via=lambda i, n, **kw : i >= n,
    label='x_i, i -> x_n',
)

# Show model structure
print(hg)
print(hg.print_paths(xn))

# Simulate
inputs = {
    x: 0.0,
    n: 4,
    velocity: 1.3,
    delta_t: 1.0,
}

hg.solve(xn, inputs=inputs, to_print=True)
