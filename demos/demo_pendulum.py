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
theta_i = Node("theta_i")
s_theta = Node("sine theta")
F = Node("gravitational force")
omega0 = Node("omega0", 0.0)
omega = Node("omega")
omega_i = Node("omega_i")
c = Node("damping coeff", 1.0)
alpha0 = Node("alpha0", 0.0)
alpha = Node("alpha")
alpha_i = Node("alpha_i")
time_step = Node("time_step", 0.05)

hg.addEdge([g, r], 'beta1', R.Rdivide, identify={g: 's1'}, label='(g,r)->b1')
hg.addEdge(theta, s_theta, R.Rsin, label='theta->sine')
hg.addEdge([s_theta, 'beta1'], F, R.Rmultiply, label='(sine, b1)->F')
# hg.addEdge([omega, c], 'beta2', R.Rmultiply, label='(omega, c)->b2')
hg.addEdge(F, alpha, R.Rmean, label='F->alpha')
hg.addEdge([F, 'beta2'], alpha, R.Rsubtract, identify={F: 's1'}, label='(F, b2)->alpha')

# hg.addEdge([alpha, time_step], omega, R.Rmultiply, label='(alpha, t)->omega')
# hg.addEdge([omega, time_step], theta, R.Rmultiply, label='(omega, t)->theta')


hg.addEdge(theta, theta_i, rel=R.Rfirst, pseudo='index', label='theta index')
hg.addEdge(omega, omega_i, rel=R.Rfirst, pseudo='index', label='omega index')
hg.addEdge(alpha, alpha_i, rel=R.Rfirst, pseudo='index', label='alpha index')
hg.addEdge([alpha, time_step], 'delta omega', R.Rmultiply, label='(alpha, t)->d_omega')

def indexIncrement(s1, s2, s3, s4):
    if s4 == s3 + 1:
        a = 2 + 2
    return s4 == s3

hg.addEdge([omega, 'delta omega', alpha_i, omega_i], omega, label='(omega, d_omega)->omega',
           identify={omega.label : 's1',
                     'delta omega' : 's2',
                     alpha_i.label : 's3',
                     omega_i.label : 's4'},
           rel=lambda s1, s2, s3, s4 : s1 + s2,
           via=indexIncrement)

hg.addEdge([omega, time_step], 'delta theta', R.Rmultiply, label='(omega, t)->d_theta')
hg.addEdge([theta, 'delta theta', omega_i, theta_i], theta, label='(theta, d_theta)->theta',
           identify={theta.label : 's1',
                     'delta theta' : 's2',
                     omega_i.label : 's3',
                     theta_i.label : 's4'},
           rel=lambda s1, s2, s3, s4 : s1 + s2,
           via=indexIncrement)

hg.addEdge(theta0, theta, R.Rmean, label='theta0->theta')
hg.addEdge(omega0, omega, R.Rmean, label='omega0->omega')
# hg.addEdge(alpha0, alpha, R.Rmean, label='alpha0->alpha')
hg.addEdge(theta, 'final_theta', R.Rmean, via=lambda *args, **kwargs : R.Rmean(*args, **kwargs) > 0.9)

hg.addEdge(theta_i, 'final_theta_i', R.Rmean, via=lambda s1 : s1 > 3)

# hg.printPaths('final_theta')

print(hg.solve('final_theta_i', toPrint=True))