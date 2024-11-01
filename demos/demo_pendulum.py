from constrainthg.hypergraph import Hypergraph, Node
import constrainthg.relations as R
import matplotlib.pyplot as plt

hg = Hypergraph()

## Nodes
g = Node("gravity", -10)
r = Node("radius", 1.0)
theta0 = Node("theta_0", 3.14159/6)
theta = Node("theta")
s_theta = Node("sine theta")
F = Node("gravitational force")
omega0 = Node("omega0", 0.0)
omega = Node("omega")
c = Node("damping coeff", 0.05)
alpha = Node("alpha")
time_step = Node("time_step", .01)

## Edges
hg.addEdge(theta0, theta, R.Rmean, label='theta0->theta')
hg.addEdge(omega0, omega, R.Rmean, label='omega0->omega')
hg.addEdge({'s1': g, 's2': r}, 'g/r', R.Rdivide, label='(g,r)->b1')
hg.addEdge(theta, s_theta, R.Rsin, label='theta->sine')
hg.addEdge([s_theta, 'g/r'], F, R.Rmultiply, label='(sine, b1)->F')
# hg.addEdge([omega, c], 'beta2', R.Rmultiply, label='(omega, c)->b2')
hg.addEdge(F, alpha, R.Rmean, label='F->alpha')
hg.addEdge({'s1':F, 's2':'beta2'}, alpha, R.Rsubtract, label='(F, b2)->alpha')
hg.addEdge([alpha, time_step], 'delta omega', R.Rmultiply, label='(alpha, t)->d_omega')
hg.addEdge({'s1':omega0, 's2':'delta omega', 's3':('s2', 'index')}, omega, 
           label='(omega0, d_omega)->omega',
           rel=lambda s1, s2, **kwargs : s1 + s2,
           via=lambda s3, **kwargs: s3 == 1)
hg.addEdge({'s1':omega, 's2':'delta omega', 's3':('s1', 'index'), 's4':('s2', 'index')}, omega, 
           label='(omega, d_omega)->omega',
           rel=lambda s1, s2, **kwargs : s1 + s2,
           via=lambda s3, s4, **kwargs: s4 == s3)
hg.addEdge([omega, time_step], 'delta theta', R.Rmultiply, label='(omega, t)->d_theta')
hg.addEdge({'s1':theta, 
            's2':'delta theta',
            's4':('s1', 'index'), 
            's5':('s2', 'index')}, theta, 
           label='(theta, d_theta)->theta',
           rel=lambda s1, s2, **kwargs : s1 + s2,
           via=lambda s4, s5, **kwargs: s4 == s5)

hg.addEdge({'s1':theta, 's2':('s1', 'index')}, 'final theta', R.equal('s1'), 
           via=lambda s2, **kwargs : s2 >= 4)
        #    via=lambda s1, s2, **kwargs : abs(s1) < .7 and abs(s2) < 1)

# hg.printPaths('final theta')

t, found_values = hg.solve('final theta', toPrint=False)
print(t.printTree())

print([f'{float(a):.2f}' for a in found_values[theta.label]])

# getTimes = lambda l : [time_step.static_value * i for i in range(len(l))]
# thetas = found_values[theta.label]
# omegas = found_values[omega.label]
# plt.plot(getTimes(thetas), thetas)
# plt.plot(getTimes(omegas), omegas)
# plt.legend(['theta', 'omega'])
# plt.xlabel('Time (s)')
# plt.ylabel('Rad, Rad/s')
# plt.title('Pendulum Simulation')
# plt.show()