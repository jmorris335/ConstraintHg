from constrainthg.hypergraph import Hypergraph, Node
import constrainthg.relations as R
import matplotlib.pyplot as plt

hg = Hypergraph()

## Nodes
g = Node("gravity", -10)
r = Node("radius", 0.5)
theta0 = Node("theta0", 3.14159/6)
theta = Node("theta")
d_theta = Node("delta theta")
s_theta = Node("sine theta")
F = Node("gravitational force")
omega0 = Node("omega0", 0.0)
omega = Node("omega")
d_omega = Node("delta omega")
c = Node("damping coeff", 1.5)
alpha = Node("alpha", starting_index=2)
time_step = Node("time_step", .01)

## Functions
def integrate(s1, s2, s3, **kwargs):
    """First order Euler integrator, where s3 is the timestep."""
    return s1 * s3 + s2

## Edges
hg.addEdge(theta0, theta, R.Rmean, label='theta0->theta')
hg.addEdge(omega0, omega, R.Rmean, label='omega0->omega')
hg.addEdge({'s1': g, 's2': r}, 'g/r', R.Rdivide, label='(g,r)->b1')
hg.addEdge(theta, s_theta, R.Rsin, label='theta->sine')
hg.addEdge([s_theta, 'g/r'], F, R.Rmultiply, label='(sine, b1)->F')
hg.addEdge([omega, c], 'beta2', R.Rmultiply, label='(omega, c)->b2')
# hg.addEdge(F, alpha, R.Rmean, label='F->alpha')
hg.addEdge({'s1':F, 's2':'beta2'}, alpha, R.Rsubtract, label='(F, b2)->alpha', edge_props='LEVEL')

hg.addEdge({'s1': alpha, 's4': ('s1', 'index'),
            's2': omega, 's5': ('s2', 'index'),
            's3': time_step,}, omega, integrate, 
            label='(alpha, omega, t)->omega',
            via=lambda s4, s5, **kwargs: s4 - 1 == s5)

hg.addEdge({'s1': omega, 's4': ('s1', 'index'),
            's2': theta, 's5': ('s2', 'index'),
            's3': time_step,}, theta, integrate, 
            label='(omega, theta, t)->theta',
            via=lambda s4, s5, **kwargs: s4 - 1 == s5)

hg.addEdge({'s1':theta, 's2':('s1', 'index'), 's3': omega}, 'final theta', R.equal('s1'), 
        #    via=lambda s2, **kwargs : s2 >= 400, label='final theta')
           via=lambda s1, s3, **kwargs : abs(s1) < .1 and abs(s3) < .1, edge_props='LEVEL')

# hg.printPaths('final theta')

t, found_values = hg.solve('final theta', toPrint=False)
print(t)
# print(t.printTree())

getTimes = lambda l : [time_step.static_value * i for i in range(len(l))]
thetas = found_values[theta.label]
omegas = found_values[omega.label]
plt.plot(getTimes(thetas), thetas)
plt.plot(getTimes(omegas), omegas)
plt.legend(['theta', 'omega'])
plt.xlabel('Time (s)')
plt.ylabel('Rad, Rad/s')
plt.title('Pendulum Simulation')
plt.show()