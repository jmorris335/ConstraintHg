from constrainthg.hypergraph import Hypergraph, Node, Edge
import constrainthg.relations as R

hg = Hypergraph()

# Nodes
floor = Node('floor', description='the number of a floor')
destination = Node('destination floor', super_nodes=[floor], description='floor number of destination')
curr_floor = Node('current floor', super_nodes=[floor], description='current_floor')
gap = Node('interfloor height', 10., description='height of a single floor')
floor_height = Node('height of floor', description='the height of a given floor')
dest_height = Node('destination height', super_nodes=[floor_height], description='the height of the destination floor')
height_tolerance = Node('height tolerance', 10, description='tolerance on measuring height')

error = Node('error', description='difference beetween destination and current position')
KP = Node('K_P', 1.0, description='proportional gain for PID')
KI = Node('K_I', 1.0, description='integral gain for PID')
KD = Node('K_D', 1.0, description='derivative gain for PID')
P = Node('P', description='proportional controller input')
I = Node('I', 0.0, description='integrative controller input')
D = Node('D', description='derivative controller input')
alpha = Node('alpha', 0.1, description='filter constant for low-pass filter')
error_f = Node('filtered error', 0.0, description='error filtered by low-pass filter')
error_f_prev = Node('prev filtered error', description='filtered error from the previous iteration')
max_pid = Node('max input', 10000, description='maximum controller input')
min_pid = Node('min input', -1000, description='minimum controller input')
pid_input = Node('PID input', description='input goverend by PID controller')
u = Node('controller input', description='input provided by controller')

mu_pass_m = Node('avg passenger mass', 65., description='mean passenger mass')
pass_m = Node('passenger mass', description='total passenger mass')
empty_m = Node('empty mass', 1000., description='mass of empty carriage')
occupancy = Node('occupancy', 0, description='persons occupying carriage')
g = Node('g', -9.8, description='gravitational acceleration')
F = Node('net force', description='net vertical force on carriage')
mass = Node('mass', description='total mass of carriage')
damping_coef = Node('c', 0.2, description='damping coefficient')
damping = Node('damping force', description='damping force')
height = Node('height', description='vertical position')
height_0 = Node('initial height', 0., description='initial height')
vel = Node('velocity', description='vertical velocity')
v_0 = Node('initial velocity', 0., description='initial velocity')
acc = Node('acceleration', description='vertical acceleration')
step = Node('step size', 1., description='step size')

goal = Node('goal', description='goal floor for passenger')
start = Node('start', description='start floor for passenger')
is_on = Node('is_on', description='true if passenger is on carriage')
boarding = Node('num boarding', description='number of persons boarding the carriage')
exiting = Node('num exiting', description='number of persons exiting the carriage')

# Custom relationships
def Rlowpassfilter(s1, s2, s3, **kwargs):
    """Filters s1, where s2 is the filter constant and s3 is previous filtered values."""
    return s1 * s2 + (1 - s2) * s3

def Rset_status(*args, **kwargs):
    """Sets the status of the passenger based on curr_floor, is_on, start, and goal (s1-s4)."""
    curr_floor = args[0] if 's1' not in kwargs else kwargs['s1']
    is_on = args[1] if 's2' not in kwargs else kwargs['s2']
    start = args[2] if 's3' not in kwargs else kwargs['s3']
    goal = args[3] if 's4' not in kwargs else kwargs['s4']

    if not is_on and (curr_floor == start):
        return True
    if is_on and (curr_floor == goal):
        return False
    return is_on

def Ris_boarding(*args, **kwargs):
    """Returns true if the passenger is boarding, 's1': curr_floor, 's2':onX, 
    's3':startX, 's4':goalX"""
    args, kwargs = R.get_keyword_arguments(args, kwargs, ['s1', 's2', 's3', 's4'])
    if kwargs['s2']:
        return False
    return kwargs['s1'] == kwargs['s3'] and kwargs['s4'] != kwargs['s1'] 
    
def Ris_exiting(*args, **kwargs):
    """Returns true if the passenger is exiting, 's1': curr_floor, 's2':onX, 's3':goalX."""
    args, kwargs = R.get_keyword_arguments(args, kwargs, ['s1', 's2', 's3'])
    return kwargs['s2'] and kwargs['s1'] == kwargs['s3']

# Connections
hg.add_edge({'s1': height, 's2': gap, 's3': height_tolerance}, curr_floor, 
           R.Rfloor_divide, label='(height,gap,height_tol)->current floor',
           via=lambda s1, s2, s3, **kwargs : abs(s1 % s2) < s3, index_offset=1)
hg.add_edge([gap, floor], floor_height, R.Rmultiply)
hg.add_edge([gap, destination], dest_height, R.Rmultiply)
hg.add_edge({'s1':dest_height, 's2':height}, error, R.Rsubtract, 
            index_offset=1, label='(dest,height)->error')

# PID
hg.add_edge([KP, error], P, R.Rmultiply)
hg.add_edge({'s1': KI,
            's2': error, 's5': ('s2', 'index'),
            's3': I, 's6': ('s3', 'index'),
            's4': step}, I, R.mult_and_sum(['s1', 's2', 's3'], 's4'),
            via=lambda s5, s6, **kwargs : s5 == s6 + 1)
hg.add_edge({'s1': error, 's5': ('s1', 'index'),
            's2': alpha,
            's3': error_f, 's6': ('s3', 'index'),
            's4': step}, error_f, Rlowpassfilter, 
            label='low_pass_filter->error_f',
            via=lambda s5, s6, **kwargs : s5 == s6 + 1)
hg.add_edge(error_f, error_f_prev, R.Rmean)
hg.add_edge({'s1': KD,
            's2': error_f, 's3': ('s2', 'index'),
            's4': error_f_prev, 's5': ('s4', 'index')}, D, R.Rmultiply,
            label='(KD, error_f, error_f_prev)->D',
            via=lambda s3, s5, **kwargs : s3 == s5 + 1)
hg.add_edge([P, I, D], pid_input, R.Rsum, label='PID', edge_props='LEVEL')
hg.add_edge([pid_input, min_pid], 'const_min_input', R.Rmax)
hg.add_edge(['const_min_input', max_pid], u, R.Rmin)

# Forces
hg.add_edge(v_0, vel, R.Rmean)
hg.add_edge(height_0, height, R.Rmean)
hg.add_edge([mu_pass_m, occupancy], pass_m, R.Rmultiply)
hg.add_edge([pass_m, empty_m], mass, R.Rsum)
hg.add_edge([g, mass], '/gm', R.Rmultiply, label='(g,mass)->/gm')
hg.add_edge({'s1': damping_coef, 's2':vel}, damping, R.Rmultiply, label='(c,vel,F)->damping')
hg.add_edge(damping, 'neg damping', R.Rnegate)
hg.add_edge([u, '/gm', 'neg damping'], F, R.Rsum, label='(u,/gm,-damping)->F')
hg.add_edge([F, mass], acc, R.Rdivide, label='(F,mass)->acc', edge_props='LEVEL')
hg.add_edge({'s1': acc, 's4': ('s1', 'index'),
            's2': vel, 's5': ('s2', 'index'),
            's3': step,}, vel, R.mult_and_sum(['s1', 's3'], 's2'),
            label='(acc,vel,step)->vel',
            via=lambda s4, s5, **kwargs: s4 == s5 + 1)
hg.add_edge({'s1': vel, 's4': ('s1', 'index'),
            's2': height, 's5': ('s2', 'index'),
            's3': step,}, height, R.mult_and_sum(['s1', 's3'], 's2'),
            label='(vel,height,step)->height',
            via=lambda s4, s5, **kwargs: s4 == s5 + 1)

# DES
boarding_edge = Edge('boarding edge', {}, boarding, R.Rsum, edge_props='LEVEL', index_offset=1)
exiting_edge = Edge('exiting edge', {}, exiting, R.Rsum, edge_props='LEVEL', index_offset=1)

def addPerson(label: str, goal_floor: int, start_floor: int, person_is_on: bool=False):
    """Adds a person to the model."""
    goalX = Node(f'goal {label}', goal_floor, super_nodes=goal, description=f'goal floor for passenger {label}')
    startX = Node(f'start {label}', start_floor, super_nodes=start, description=f'start floor for passenger {label}')
    onX = Node(f'{label} is on', person_is_on, super_nodes=is_on, description=f'true if passenger {label} is on carriage')
    is_boarding = Node(f'{label} is boarding', description=f'true if passenger {label} is boarding carriage')
    is_exiting = Node(f'{label} is exiting', description=f'true if passenger {label} is exiting carriage')

    hg.add_edge({'s1': curr_floor, 's2':onX, 's3':startX, 's4':goalX, 
                's5': ('s1', 'index'), 's6': ('s2', 'index')}, onX, Rset_status,
               label=f'(curr_floor,{label}:is_on,start,goal)->{label} is on',
               via=lambda s5, s6, **kwargs : s5 == s6 + 1)
    hg.add_edge({'s1': curr_floor, 's2':onX, 's3':startX, 's4':goalX,
                's5': ('s1', 'index'), 's6': ('s2', 'index')}, is_boarding, Ris_boarding,
                label=f'(curr_floor,{label}:is_on,start,goal)->{label} is boarding',
                via=lambda s5, s6, **kwargs : s5 == s6 + 1)
    hg.add_edge({'s1': curr_floor, 's2':onX, 's3':goalX,
                's4': ('s1', 'index'), 's5': ('s2', 'index')}, is_exiting, Ris_exiting,
                label=f'(curr_floor,{label}:is_on,goal)->{label} is exiting',
                via=lambda s4, s5, **kwargs : s4 == s5 + 1)
    boarding_edge.add_source_node(is_boarding)
    exiting_edge.add_source_node(is_exiting)

# people = [('A', 2, 0, False), ('B', 2, 0, False), ('C', 1, 3, False), ('D', 1, 0, True)]
people = [('A', 0, 3, False)]
for person in people:
    addPerson(*person)
hg.insert_edge(boarding_edge)
hg.insert_edge(exiting_edge)

hg.add_edge({'s1':occupancy, 's2':boarding, 's3':exiting, 's4': ('s1', 'index'), 
            's5': ('s2', 'index'), 's6': ('s3', 'index')}, occupancy, 
            lambda s1, s2, s3, **kwargs : s1 + s2 - s3, index_offset=1,
            label='(occ, boarding, exiting)->occupancy',
            via=lambda s4, s5, s6, **kwargs : s5 == s6 and s5 == s4 + 1)

# Simulation
inputs = {
    curr_floor: 0,
    error: 0,
    destination: 1,
}
hg.add_edge({'s1':occupancy, 's2':('s1', 'index')}, 'final value', R.Rfirst, 
           via=R.geq('s2', 3))

# hg.printPaths('final value', toPrint=True)
debug_nodes = {'A is on'} if False else None
debug_edges = {'(curr_floor,A:is_on,start,goal)->A is on'} if False else None
t, found_values = hg.solve('final value', inputs, toPrint=True, search_depth=1000,
                           debug_nodes=debug_nodes, debug_edges=debug_edges)
print(str(t) + (f', Index: {t.children[0].index}' if t is not None else ''))

# print("Generating:")
# print([str(e) for e in vel.generating_edges])
# print("Leading:")
# print([str(e) for e in vel.leading_edges])
