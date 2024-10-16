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
omega = Node("omega", 0.0)
c = Node("damping coeff", 1.0)
alpha0 = Node("alpha0", 0.0)
alpha = Node("alpha", 0.0)
time_step = Node("time_step", 0.5)

hg.addEdge([g, r], 'beta1', R.Rdivide, identify={g: 's1'})
hg.addEdge(theta, s_theta, R.Rsin)
hg.addEdge([s_theta, 'beta1'], F, R.Rmultiply)
hg.addEdge([omega, c], 'beta2', R.Rmultiply)
hg.addEdge(F, alpha, R.Rmean)
hg.addEdge([F, 'beta2'], alpha, R.Rsubtract, identify={F: 's1'})
hg.addEdge([alpha, time_step], 'delta omega', R.Rmultiply)
hg.addEdge([omega, 'delta omega'], omega, R.Rsum)
hg.addEdge([omega, time_step], 'delta theta', R.Rmultiply)
hg.addEdge([theta, 'delta theta'], theta, R.Rsum)
hg.addEdge(theta0, theta, R.Rmean)
hg.addEdge(omega0, omega, R.Rmean)
hg.addEdge(alpha0, alpha, R.Rmean)
hg.addEdge(theta, 'final_theta', R.Rmean, via=lambda *args, **kwargs : abs(R.Rmean(*args, **kwargs)) < 0.3)

hg.printPaths('final_theta')

hg.solve('final_theta', toPrint=True)