from constrainthg.hypergraph import Hypergraph, Node
import constrainthg.relations as R
import matplotlib.pyplot as plt

hg = Hypergraph()

## Nodes
g = Node("gravity", -10)
r = Node("radius", 1.0)
theta0 = Node("theta_0", 3.14159/6)
theta = Node("theta")
d_theta = Node("delta theta")
s_theta = Node("sine theta")
F = Node("gravitational force")
omega0 = Node("omega0", 0.0)
omega = Node("omega")
d_omega = Node("delta omega")
c = Node("damping coeff", 0.05)
alpha = Node("alpha")
alpha0 = Node("alpha0", -999)
time_step = Node("time_step", .01)

## Functions
def differentiate(s1, s2, s3, **kwargs):
    """First order Euler differentiator."""
    return s1 * s3 + s2

## Edges
# hg.addEdge(theta0, theta, R.Rmean, label='theta0->theta')
hg.addEdge(alpha0, alpha, R.Rmean, label='alpha0->alpha')
hg.addEdge({'s1':theta0, 's2':alpha, 's3':('s2', 'index')}, theta, #Just to seed alpha's index
           lambda s1, **kwargs : s1, label='index setter', 
           via=lambda s3, **kwargs : s3 == 1)
hg.addEdge(omega0, omega, R.Rmean, label='omega0->omega')
hg.addEdge({'s1': g, 's2': r}, 'g/r', R.Rdivide, label='(g,r)->b1')
hg.addEdge(theta, s_theta, R.Rsin, label='theta->sine')
hg.addEdge([s_theta, 'g/r'], F, R.Rmultiply, label='(sine, b1)->F')
# hg.addEdge([omega, c], 'beta2', R.Rmultiply, label='(omega, c)->b2')
hg.addEdge(F, alpha, R.Rmean, label='F->alpha')
hg.addEdge({'s1':F, 's2':'beta2'}, alpha, R.Rsubtract, label='(F, b2)->alpha')

hg.addEdge({'s1': alpha, 's4': ('s1', 'index'),
            's2': omega, 's5': ('s2', 'index'),
            's3': time_step,}, omega, differentiate, 
            label='(alpha, omega, t)->omega',
            via=lambda s4, s5, **kwargs: s4 - 1 == s5)

# hg.addEdge({'s1': alpha, 's4': ('s1', 'index'),
#             's2': omega0,
#             's3': time_step,}, omega, differentiate, 
#             label='(alpha, omega0, t)->omega',
#             via=lambda s4, **kwargs: s4 == 1)

hg.addEdge({'s1': omega, 's4': ('s1', 'index'),
            's2': theta, 's5': ('s2', 'index'),
            's3': time_step,}, theta, differentiate, 
            label='(omega, theta, t)->theta',
            via=lambda s4, s5, **kwargs: s4 - 1 == s5)

# hg.addEdge([alpha, time_step], d_omega, R.Rmultiply, label='(alpha, t)->d_omega')
# hg.addEdge({'s1':omega0, 's2':alpha, 's3':('s2', 'index')}, omega, 
#            label='(omega0, d_omega)->omega',
#            rel=lambda s1, s2, **kwargs : s1 + s2,
#            via=lambda s3, **kwargs: s3 == 1)
# hg.addEdge([omega, d_omega], omega, R.Rsum, label='(omega, d_omega)->omega', edge_props='LEVEL')
# hg.addEdge([omega, time_step], d_theta, R.Rmultiply, label='(omega, t)->d_theta')
# hg.addEdge([theta, d_theta], theta, R.Rsum, label='(theta, d_theta)->theta', edge_props='LEVEL')
hg.addEdge({'s1':theta, 's2':('s1', 'index')}, 'final theta', R.equal('s1'), 
           via=lambda s2, **kwargs : s2 >= 400)
        #    via=lambda s1, s2, **kwargs : abs(s1) < .7 and abs(s2) < 1)

# hg.printPaths('final theta')

t, found_values = hg.solve('final theta', toPrint=False)
print(t)
# print(t.printTree())

# print([f'{float(a):.4f}' for a in found_values[theta.label]])

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