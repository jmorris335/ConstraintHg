from config import runInPlace
runInPlace()

from src.constrainthg.hypergraph import Hypergraph, Node
import src.constrainthg.relations as R

hg = Hypergraph()

# Nodes
mu_pass_m = Node('average passenger mass', value=65., description='mean passenger mass')
pass_m = Node('passenger mass', description='total passenger mass')
empty_m = Node('empty mass', value=1000., description='mass of empty carriage')
occ = Node('occupency', value=3, description='persons occupying carriage')
g = Node('g', value=-9.8, description='gravitational acceleration')
F = Node('net force', description='net vertical force on carriage')
mass = Node('mass', description='total mass of carriage')
pid = Node('PID input', value=11800, description='PID force input on carriage')
damping_coef = Node('c', value=0.2, description='damping coefficient')
damping = Node('damping force', description='damping force')
height = Node('height', description='vertical position')
y_0 = Node('initial height', value=0., description='initial height')
vel = Node('velocity', description='vertical velocity')
v_0 = Node('initial velocity', value=0., description='initial velocity')
acc = Node('acceleration', description='vertical acceleration')
step = Node('step size', value=1., description='step size')
goalA = Node('goal A', value=2, description='goal floor for passenger A')
goalB = Node('goal B', value=2, description='goal floor for passenger B')
goalC = Node('goal C', value=2, description='goal floor for passenger C')
goalD = Node('goal D', value=0, description='goal floor for passenger D')
startA = Node('start A', value=1, description='start floor for passenger A')
startB = Node('start B', value=1, description='start floor for passenger B')
startC = Node('start C', value=0, description='start floor for passenger C')
startD = Node('start D', value=2, description='start floor for passenger D')
curr_floor = Node('current floor', value=0, description='current_floor')

# Custom relationships
def Rset_status(*args, **kwargs):
    """Sets the status of the elevator based on curr_floor (s1) and [is_on, start, goal] (s2)."""
    curr_floor = args[0] if 's1' not in kwargs else kwargs['s1']
    if 's3' in kwargs:
        is_on = kwargs['s2']
        start = kwargs['s3']
        goal = kwargs['s4']
    if 's2' in kwargs:
        is_on, start, goal = kwargs['s2']
    elif len(args) > 4:
        is_on, start, goal = args[1:4]
    elif len(args) == 3:
        is_on, start, goal = args
    elif len(args) > 1:
        is_on, start, goal = args[1]
    else:
        is_on, start, goal = args[0]

    if not is_on and (curr_floor == start):
        return True
    if is_on and (curr_floor == goal):
        return False
    return is_on

# Forces
hg.addEdge([mu_pass_m, occ], pass_m, R.Rmultiply)
hg.addEdge([pass_m, empty_m], mass, R.Rsum)
hg.addEdge([g, mass], '_gm', R.Rmultiply)
hg.addEdge([pid, '_gm'], F, R.Rsum)
hg.addEdge([damping_coef, v_0], damping, R.Rmultiply)
#TODO: address labeling issues with adding edges
hg.addEdge(['_fd', mass], acc, R.Rdivide)
hg.addEdge([F, mass], acc, R.Rdivide)
hg.addEdge([F, damping], '_fd', R.Rsubtract)
#TODO: replace v_0, y_0 with loop behavior
hg.addEdge([acc, step], 'del_v', R.Rmultiply)
hg.addEdge(['del_v', v_0], vel, R.Rsum)
hg.addEdge([vel, step], 'del_y', R.Rmultiply)
hg.addEdge(['del_y', y_0], height, R.Rsum)

# hg.printPaths(height)

hg.solve(height, toPrint=True)