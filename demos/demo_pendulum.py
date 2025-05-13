from constrainthg.hypergraph import Hypergraph, Node
import constrainthg.relations as R
import matplotlib.pyplot as plt

#########################
### Nodes ##########
#########################

hg = Hypergraph()

# -- Nodes
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
alpha = Node("alpha")
time_step = Node("time_step", .03)

time = Node("t")

##########################
##### Relations ##########
##########################

# For complex systems, it is recommended to define these elsewhere and import
# See microgrid

def integrate(s1, s2, s3, **kwargs):
    return s1 * s3 + s2

############################
######Edges ################
############################

# Edges from Previous Pendulum Example, but they are updated to current
#best practice


hg.add_edge(theta0, 
            target= theta, 
            rel=R.Rmean, 
            label='theta0->theta')

hg.add_edge(omega0, 
            target=omega, 
            rel=R.Rmean, 
            label='omega0->omega')
# Note that the target (g/r) is not created in the initial node list.
# Targets and sources that are not located within the list are added. 

hg.add_edge({'s1': g, 's2': r}, 
            target='g/r', 
            rel=R.Rdivide, 
            label='(g,r)->b1')

# In case you are wondering why a dictionary is used here instead of a list or set,
# it is because the ordering of the arguments matters for this input equation
# g/r, and r/g are very different quantities. 


hg.add_edge(theta, 
            target=s_theta, 
            rel=R.Rsin, 
            label='theta->sine')
hg.add_edge({s_theta, 'g/r'}, 
            target=F, 
            rel=R.Rmultiply, 
            label='(sine, b1)->F')
hg.add_edge({omega, c}, 
            target='beta2', 
            rel=R.Rmultiply, 
            label='(omega, c)->b2')

# hg.addEdge(F, alpha, R.Rmean, label='F->alpha', index_offset=1)

hg.add_edge({'s1':F, 's2':'beta2'}, 
            target= alpha, 
            rel=R.Rsubtract, 
            label='(F, b2)->alpha', edge_props='LEVEL', index_offset=1)


# These following edges has been updated to utilize the updated, index_via function
hg.add_edge({'s1': alpha,'s2': omega,'s3': time_step}, 
            target=omega,
            rel=integrate, 
            label='(alpha, omega, t)->omega',
            index_via= lambda s1, s2, s3, **kwargs: s1 - 1 == s2)
            

hg.add_edge({'s1': omega,'s2': theta,'s3': time_step}, 
            target=theta, 
            rel=integrate, 
            label='(omega, theta, t)->theta',
            index_via=lambda s1, s2, s3, **kwargs: s1 - 1 == s2)

# The path to 'final theta' is only viable if the position and velocity of the pendulum are less than a threshold
hg.add_edge({'s1':theta,'s2':omega}, 
            target='final theta', 
            rel=R.equal('s1'), 
            via=lambda s1, s2, **kwargs : abs(s1) < .05 and abs(s2) < .05, edge_props='LEVEL')


t = hg.solve('final theta', to_print=False)
print(t)
# print(t.printTree())

getTimes = lambda l : [time_step.static_value * i for i in range(len(l))]
thetas = t.values[theta.label]
omegas = t.values[omega.label]
plt.plot(getTimes(thetas), thetas)
plt.plot(getTimes(omegas), omegas)
plt.legend(['theta', 'omega'])
plt.xlabel('Time (s)')
plt.ylabel('Rad, Rad/s')
plt.title('Pendulum Simulation')
plt.show()
