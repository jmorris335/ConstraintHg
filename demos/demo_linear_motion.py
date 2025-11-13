"""
This script demonstrates a basic cycle, and using the index of a node to
break the cycle. The system being modeled is a body moving at constant
velocity, where we want to estimate the position of the body after ``n``
seconds.
"""

from constrainthg.hypergraph import Hypergraph
import constrainthg.relations as R

hg = Hypergraph()

# Define variables (nodes)
velocity = hg.add_node('velocity', description='constant velocity', units='m/s')
delta_t = hg.add_node('delta_t', description='time step', units='s')
delta_x = hg.add_node('delta_x', description='distance moved per step', units='m')
x = hg.add_node('x', description='current position', units='m')
xn = hg.add_node('x_n', description='final position', units='m')
n = hg.add_node('n', description='maximum index to stop on')

# Define relationships (edges)
hg.add_edge(
    sources=[velocity, delta_t],
    target=delta_x, #<- This is how much the object moves every step
    rel=R.Rmultiply,
    label='vel*delta_t -> delta_x',
)
hg.add_edge(
    sources=[x, delta_x],
    target=x, # The position of the object is the sum of delta_x and the previous position
    rel=R.Rsum,
    index_offset=1, # This indicates that current position's index should increase by 1
    label='x_i+delta_x -> x_i',
)
hg.add_edge(
    sources={
        'x': x,
        'i': ('x', 'index'), # This is a psuedo node. Read more `here <https://constrainthg.readthedocs.io/en/latest/tutorial/viability.html#psuedo-nodes>`_
        'n': n
    },
    target=xn,
    rel=R.equal('x'), #<- We're just setting xn equal to x
    via=lambda i, n: i > n,
    label='x_i, i -> x_n',
)

# Show model structure. Note the cycles
print(hg)
print(hg.summary(xn))

# Simulate the system.
inputs = {
    x: 0.0,
    n: 4, #<- Sets the maximum interation of the cycle to break at
    velocity: 1.5,
    delta_t: 1.0,
}

hg.solve(xn, inputs=inputs, to_print=True)

# An equivalent way to simulate the system that doesn't require psuedo
# uses the ``min_index`` argument instead:
hg.solve(x, inputs=inputs, min_index=5, to_print=True)
