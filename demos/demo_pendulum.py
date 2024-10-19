from config import runInPlace
runInPlace()

from src.constrainthg.hypergraph import Hypergraph, Node
import src.constrainthg.relations as R

hg = Hypergraph()

# Nodes
g = Node("gravity", -9.81)
r = Node("radius", 1.0)
theta0 = Node("theta_0", 3.14159/4)
theta = Node("theta")
s_theta = Node("sine theta")
F = Node("gravitational force")
omega0 = Node("omega0", 0.0)
omega = Node("omega")
c = Node("damping coeff", 1.0)
alpha0 = Node("alpha0", 0.0)
alpha = Node("alpha")
time_step = Node("time_step", 0.5)

hg.addEdge([g, r], 'beta1', R.Rdivide, identify={g: 's1'}, label='(g,r)->b1')
hg.addEdge(theta, s_theta, R.Rsin, label='theta->sine')
hg.addEdge([s_theta, 'beta1'], F, R.Rmultiply, label='(sine, b1)->F')
hg.addEdge([omega, c], 'beta2', R.Rmultiply, label='(omega, c)->b2')
hg.addEdge(F, alpha, R.Rmean, label='F->alpha')
hg.addEdge([F, 'beta2'], alpha, R.Rsubtract, identify={F: 's1'}, label='(F, b2)->alpha')
hg.addEdge([alpha, time_step], 'delta omega', R.Rmultiply, label='(alpha, t)->d_omega')
hg.addEdge([omega, 'delta omega'], omega, R.Rsum, label='(omega, d_omega)->omega')
hg.addEdge([omega, time_step], 'delta theta', R.Rmultiply, label='(omega, t)->d_theta')
hg.addEdge([theta, 'delta theta'], theta, R.Rsum, label='(theta, d_theta)->theta')
hg.addEdge(theta0, theta, R.Rmean, label='theta0->theta')
# hg.addEdge(omega0, omega, R.Rmean, label='omega0->omega')
# hg.addEdge(alpha0, alpha, R.Rmean, label='alpha0->alpha')
hg.addEdge(theta, 'final_theta', R.Rmean, via=lambda *args, **kwargs : abs(R.Rmean(*args, **kwargs)) < 0.3)

# hg.printPaths('omega')

hg.solve(omega, toPrint=True)