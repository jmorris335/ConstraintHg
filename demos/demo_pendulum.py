from constrainthg.hypergraph import Hypergraph, Node
import constrainthg.relations as R
import matplotlib.pyplot as plt

hg = Hypergraph()

# Nodes
g = Node("gravity", -10)
r = Node("radius", 1.0)
theta0 = Node("theta_0", 3.14159/4)
theta = Node("theta")
s_theta = Node("sine theta")
F = Node("gravitational force")
omega0 = Node("omega0", 0.0)
omega = Node("omega")
c = Node("damping coeff", 0.05)
alpha = Node("alpha")
time_step = Node("time_step", 0.01)


hg.addEdge(theta0, theta, R.Rmean, label='theta0->theta')
# hg.addEdge(omega0, omega, R.Rmean, label='omega0->omega')
hg.addEdge({'s1': g, 's2': r}, 'beta1', R.Rdivide, label='(g,r)->b1')
hg.addEdge(theta, s_theta, R.Rsin, label='theta->sine')
hg.addEdge([s_theta, 'beta1'], F, R.Rmultiply, label='(sine, b1)->F')
# hg.addEdge([omega, c], 'beta2', R.Rmultiply, label='(omega, c)->b2')
hg.addEdge(F, alpha, R.Rmean, label='F->alpha')
# hg.addEdge({'s1':F, 's2':'beta2'}, alpha, R.Rsubtract, label='(F, b2)->alpha')
hg.addEdge([alpha, time_step], 'delta omega', R.Rmultiply, label='(alpha, t)->d_omega')

hg.addEdge('delta omega', omega, R.Rmean)
hg.addEdge('delta theta', theta, R.Rmean)


# hg.addEdge({'s1':omega, 's2':'delta omega', 's3':('s1', 'index'), 's4':('s2', 'index')}, omega, 
#            label='(omega, d_omega)->omega',
#            rel=lambda s1, s2, **kwargs : s1 + s2,
#            via=lambda s3, s4, **kwargs: s3 >= s4)
hg.addEdge([omega, time_step], 'delta theta', R.Rmultiply, label='(omega, t)->d_theta')
# hg.addEdge({'s1':theta, 
#             's2':'delta theta',
#             's3':'delta omega',
#             's4':('s1', 'index'), 
#             's5':('s2', 'index'),
#             's6':('s3', 'index')}, theta, 
#            label='(theta, d_theta)->theta',
#            rel=lambda s1, s2, **kwargs : s1 + s2,
#            via=lambda s4, s5, s6, **kwargs: s4 >= s5 and s4 >= s6)

# hg.addEdge({'s1':theta, 's2':omega, 's3':('s1', 'index')}, 'final theta', R.equal('s1'), 
#            via=lambda s2, **kwargs : s2 > 10)
        #    via=lambda s1, s2, **kwargs : abs(s1) < .7 and abs(s2) < 1)

hg.addEdge({'s1':theta, 's2':('s1', 'index')}, 'final theta', R.equal('s1'), 
           via=lambda s2, **kwargs : s2 > 20)

hg.printPaths('final theta')

t, found_values = hg.solve('final theta', toPrint=True)

# print(found_values[theta.label][-1])

getTimes = lambda l : [time_step.static_value * i for i in range(len(l))]
thetas = found_values[theta.label]
omegas = found_values[omega.label]
plt.plot(getTimes(thetas), thetas)
plt.plot(getTimes(omegas), omegas)
plt.legend(['theta', 'omega'])
plt.show()