from constrainthg.hypergraph import Hypergraph, Node
import constrainthg.relations as R

# Define hypergraph
hg = Hypergraph()

#########################
### Nodes ###############
#########################

g = hg.add_node(Node('gravity', -10))
r = hg.add_node(Node('radius', 0.5))
theta0 = hg.add_node(Node('theta0', 3.14159/6))
theta = hg.add_node(Node('theta'))
d_theta = hg.add_node(Node('delta theta'))
s_theta = hg.add_node(Node('sine theta'))
F = hg.add_node(Node('gravitational force'))
omega0 = hg.add_node(Node('omega0', 0.0))
omega = hg.add_node(Node('omega'))
d_omega = hg.add_node(Node('delta omega'))
c = hg.add_node(Node('damping coeff', 1.5))
alpha = hg.add_node(Node('alpha'))
time_step = hg.add_node(Node('time_step', .03))
time = Node('time', 0.)

##########################
### Relations ############
##########################

def Rintegrate(step, slope, initial_val, *args, **kwargs):
    """First order Eulerian integrator."""
    return step * slope + initial_val

##########################
### Edges ################
##########################

hg.add_edge(
    sources=theta0,
    target=theta,
    rel=R.Rmean,
    label='theta0->theta',
)

hg.add_edge(
    sources=omega0,
    target=omega,
    rel=R.Rmean,
    label='omega0->omega',
)

# In case you are wondering why a dictionary is used here instead of a
# list or set, it is because the ordering of the arguments matters for
# this input equation g/r, and r/g are very different quantities. 
hg.add_edge(
    sources={'s1': g, 's2': r},
    target='g/r',
    rel=R.Rdivide,
    label='(g,r)->b1',
)

hg.add_edge(
    sources=theta,
    target=s_theta,
    rel=R.Rsin,
    label='theta->sine',
)

# Note that the target (g/r) is not created in the initial node list.
# Targets and sources that are not located within the list are added. 
hg.add_edge(
    sources={'s_theta': s_theta, 'g/r': 'g/r'},
    target=F,
    rel=R.Rmultiply,
    disposable=['s_theta'],
    label='(sine, b1)->F',
)

hg.add_edge(
    sources={'omega': omega, 'c': c},
    target='beta2',
    rel=R.Rmultiply,
    disposable=['omega'],
    label='(omega, c)->b2',
)

hg.add_edge(
    sources={'F': F},
    target=alpha,
    rel=R.equal('F'),
    index_offset=1,
    disposable=['F'],
    # weight=100,
    label='F->alpha',
)

# This path adds damping to the model. It competes with the simple pendulum edge.
# hg.add_edge(
#     sources={'s1': F, 's2': 'beta2'},
#     target=alpha,
#     rel=R.Rsubtract,
#     edge_props=['LEVEL', 'DISPOSE_ALL'],
#     index_offset=1,
#     label='(F, b2)->alpha',
# )

hg.add_edge(
    sources={'slope': alpha, 'initial_val': omega, 'step': time_step},
    target=omega,
    rel=Rintegrate,
    index_via=lambda slope, initial_val, **kw: slope - 1 == initial_val,
    disposable=['slope', 'intial_val'],
    label='(alpha, omega, time_step)->omega',
)

hg.add_edge(
    sources={'slope': omega, 'initial_val': theta, 'step': time_step},
    target=theta,
    rel=Rintegrate,
    index_via=lambda slope, initial_val, **kw: slope - 1 == initial_val,
    disposable=['slope', 'intial_val'],
    label='(omega, theta, time_step)->theta',
)

hg.add_edge(
    sources={'time': time, 'step': time_step},
    target=time,
    rel=R.Rsum,
    index_offset=1,
    disposable=['time'],
    label='(time,step)->time'
)

# The path to 'resting_theta' is only viable if the position and velocity
# of the pendulum are less than a threshold
hg.add_edge(
    sources={'s1': theta, 's2': omega}, 
    target='resting_theta', 
    rel=R.equal('s1'), 
    via=lambda s1, s2, *args, **kwargs : max(abs(s1), abs(s2)) < .05,
    edge_props=['LEVEL', 'DISPOSE_ALL'],
    label='calc_resting_theta',
)

############################
### Simulate ###############
############################

# print(hg.print_paths(alpha))

output_tnode = hg.solve(
    target='theta',
    min_index=100,
    # logging_level=10,
    # debug_edges=['(alpha, omega, t)->omega'],
)
print(output_tnode)
# print(output_tnode.print_tree())

############################
### Plot ###################
############################

theta = hg.solve(theta, min_index=100)
thetas, omegas = theta.values['theta'], theta.values['omega']
time = hg.solve(time, min_index=100).values['time']

import matplotlib.pyplot as plt
length = min(len(time), len(thetas), len(omegas))
plt.plot(time[:length], thetas[:length])
plt.plot(time[:length], omegas[:length])
plt.legend(['theta', 'omega'])
plt.xlabel('Time (s)')
plt.ylabel('Rad, Rad/s')
plt.title('Pendulum Simulation')
plt.show()
