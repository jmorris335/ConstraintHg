from constrainthg.hypergraph import Hypergraph, Node, Edge, TNode
import constrainthg.relations as R

import matplotlib.pyplot as plt #For visualization, not necessary for simulation

hg = Hypergraph()

# Nodes
## Nodes (variables) for elevator stops
floor = hg.add_node(Node('floor', description='the number of a floor', units='floor'))
destination_floor = hg.add_node(Node('destination_floor', super_nodes=[floor], description='floor number of destination', units='floor'))
current_floor = hg.add_node(Node('current_floor', super_nodes=[floor], description='current_floor', units='floor'))
gap = hg.add_node(Node('gap', 10., description='height of a single floor', units='m'))
floor_height = hg.add_node(Node('floor_height', description='the height of a given floor', units='m'))
dest_height = hg.add_node(Node('destination_height', super_nodes=[floor_height], description='the height of the destination floor', units='m'))
height_tolerance = hg.add_node(Node('height_tolerance', 10, description='tolerance on measuring height', units='m'))

## Nodes for motor controller
error = hg.add_node(Node('error', description='difference beetween destination and current position', units='m'))
KP = hg.add_node(Node('K_P', 271, description='proportional gain for PID'))
KI = hg.add_node(Node('K_I', 35, description='integral gain for PID'))
KD = hg.add_node(Node('K_D', -0.79, description='derivative gain for PID'))
P = hg.add_node(Node('P', description='proportional controller input', units='N'))
I = hg.add_node(Node('I', 0.0, description='integrative controller input', units='N'))
D = hg.add_node(Node('D', description='derivative controller input', units='N'))
alpha = hg.add_node(Node('alpha', 0.5, description='filter constant for low-pass filter'))
error_f = hg.add_node(Node('filtered error', 0.0, description='error filtered by low-pass filter', units='m'))
error_f_prev = hg.add_node(Node('prev filtered error', description='filtered error from the previous iteration', units='m'))
max_pid = hg.add_node(Node('max input', 10000, description='maximum controller input', units='N'))
min_pid = hg.add_node(Node('min input', -1000, description='minimum controller input', units='N'))
pid_input = hg.add_node(Node('PID input', 0., description='input goverend by PID controller', units='N'))
u = hg.add_node(Node('controller input', description='input provided by controller', units='N'))

## Nodes for elevator dynamics
mu_pass_m = hg.add_node(Node('avg passenger mass', 75., description='mean passenger mass', units='kg'))
pass_m = hg.add_node(Node('passenger mass', description='total passenger mass', units='kg'))
empty_m = hg.add_node(Node('empty mass', 1000., description='mass of empty carriage', units='kg'))
occupancy = hg.add_node(Node('occupancy', 0, description='persons occupying carriage', units='persons'))
g = hg.add_node(Node('g', -9.8, description='gravitational acceleration', units='m/s^2'))
F = hg.add_node(Node('net force', description='net vertical force on carriage', units='N'))
mass = hg.add_node(Node('mass', description='total mass of carriage', units='kg'))
damping_coef = hg.add_node(Node('c', 50, description='damping coefficient', units='kg/s'))
damping = hg.add_node(Node('damping force', description='damping force', units='N'))
height = hg.add_node(Node('height', description='vertical position', units='m'))
height_0 = hg.add_node(Node('initial height', 0., description='initial height', units='m'))
vel = hg.add_node(Node('velocity', description='vertical velocity', units='m/s'))
v_0 = hg.add_node(Node('initial velocity', 0., description='initial velocity', units='m/s'))
acc = hg.add_node(Node('acceleration', description='vertical acceleration', units='m/s^2'))
step = hg.add_node(Node('step', 0.1, description='time step size', units='s'))
time = hg.add_node(Node('time', 0., description='current time', units='s'))
counterweight = hg.add_node(Node('counterweight', -850., description='counterweight for carriage', units='kg'))

## Nodes for passengers
goal = hg.add_node(Node('goal', description='goal floor for passenger', units='floor'))
start = hg.add_node(Node('start', description='start floor for passenger', units='floor'))
is_on = hg.add_node(Node('is_on', description='true if passenger is on carriage', units='bool'))
boarding = hg.add_node(Node('num boarding', description='number of persons boarding the carriage', units='persons'))
exiting = hg.add_node(Node('num exiting', description='number of persons exiting the carriage', units='persons'))

# Custom relationships
def Rlowpassfilter(s1, s2, s3, **kwargs):
    """Filters s1, where s2 is the filter constant and s3 is previous
    filtered values.
    """
    return s1 * s2 + (1 - s2) * s3

def Rset_status(*args, **kwargs):
    """Sets the status of the passenger based on curr_floor, is_on,
    start, and goal (s1-s4).
    """
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
    """Returns true if the passenger is boarding, 's1': curr_floor,
    's2':onX, 's3':startX, 's4':goalX.
    """
    args, kwargs = R.get_keyword_arguments(args, kwargs, ['s1', 's2', 's3', 's4'])
    if kwargs['s2']:
        return False
    return kwargs['s1'] == kwargs['s3'] and kwargs['s4'] != kwargs['s1'] 
    
def Ris_exiting(*args, **kwargs):
    """Returns true if the passenger is exiting, 's1': curr_floor,
    's2':onX, 's3':goalX.
    """
    args, kwargs = R.get_keyword_arguments(args, kwargs, ['s1', 's2', 's3'])
    return kwargs['s2'] and kwargs['s1'] == kwargs['s3']

# Edges
hg.add_edge(
    sources={'time': time, 'step': step},
    target=time,
    rel=R.Rsum,
    index_offset=1,
    disposable=['time'],
    label='increment time',
)

## Hybrid connection relationships
hg.add_edge(
    sources={'s1': height, 's2': gap, 's3': height_tolerance},
    target=current_floor, 
    rel=R.Rfloor_divide,
    via=lambda s1, s2, s3, **kwargs : abs(s1 % s2) < s3,
    index_offset=1,
    label='(height,gap,height_tol)->current floor',
)
hg.add_edge(
    sources={'gap': gap, 'floor': current_floor},
    target=floor_height,
    rel=R.Rmultiply,
    disposable=['floor'],
    label='calc_current_floor_height',
)
hg.add_edge(
    sources={'gap':gap, 'floor':destination_floor},
    target=dest_height,
    rel=R.Rmultiply,
    disposable=['floor'],
    label='calc destination floor height',
)
hg.add_edge(
    sources={'s1':dest_height, 's2':height},
    target=error,
    rel=R.Rsubtract, 
    index_offset=1,
    label='(dest,height)->error',
)

## Motor controller relationships
hg.add_edge({'KP': KP, 'error': error}, P, R.Rmultiply, disposable=['error'])
hg.add_edge(
    sources={'s1': KI, 's2': error, 's3': I, 's4': step},
    target=I,
    rel=R.mult_and_sum(['s1', 's2', 's4'], 's3'),
    index_via=lambda s2, s3, **kw : s2 == s3 + 1,
    disposable=['s2', 's3'],
)
hg.add_edge(
    sources={'s1': error, 's2': alpha, 's3': error_f},
    target=error_f,
    rel=Rlowpassfilter, 
    index_via=lambda s1, s3, **kw : s1 == s3 + 1,
    disposable=['s1', 's3'],
    label='low_pass_filter->error_f',
)
hg.add_edge(error_f, error_f_prev, R.Rmean)
hg.add_edge(
    sources={'s1':error_f, 's2':error_f_prev},
    target='error_f_diff',
    rel=R.Rsubtract,
    index_via=lambda s1, s2, **kw : s1 == s2 + 1,
    edge_props=['DISPOSE_ALL'],
)
# hg.add_edge(
#     sources={'s1':'error_f_diff', 's2':step},
#     target='error_derivative',
#     rel=R.Rdivide,
#     disposable=['s1'],
# )
# hg.add_edge(
#     sources={'KD': KD, 'error': 'error_derivative'},
#     target=D,
#     rel=R.Rmultiply,
#     disposable=['error'],
#     label='KD,error_f_diff->D',
# )
hg.add_edge(
    sources={'s1': KD, 's2': error_f, 's3': error_f_prev},
    target=D,
    rel=R.Rmultiply,
    index_via=lambda s2, s3, **kw : s2 == s3 + 1,
    disposable=['s2', 's3'],
    label='(KD, error_f, error_f_prev)->D',
)
hg.add_edge(
    sources=[P, I, D],
    target=pid_input,
    rel=R.Rsum,
    edge_props=['LEVEL', 'DISPOSE_ALL'],
    label='PID',
)
hg.add_edge(
    sources={'pid': pid_input, 'min': min_pid},
    target='const_min_input',
    rel=R.Rmax,
    disposable=['pid'],
    label='apply_lower_bound_to_u',
)
hg.add_edge(
    sources={'pid': 'const_min_input', 'max': max_pid},
    target=u,
    rel=R.Rmin,
    disposable=['pid'],
    label='apply_upper_bound_to_u',
)

## Forces
hg.add_edge(v_0, vel, R.Rmean)
hg.add_edge(height_0, height, R.Rmean)
hg.add_edge(
    sources={'mu': mu_pass_m, 'occ': occupancy},
    target=pass_m,
    rel=R.Rmultiply,
    disposable=['occ'],
)
hg.add_edge(
    sources={'pass_m': pass_m, 'empty_m': empty_m, 'c_weight': counterweight},
    target=mass,
    rel=R.Rsum,
    disposable=['pass_m'],
)
hg.add_edge(
    sources={'g': g, 'm': mass},
    target='/gm',
    rel=R.Rmultiply,
    disposable=['m'],
    label='(g,mass)->/gm',
)
hg.add_edge(damping, 'neg damping', R.Rnegate)
hg.add_edge(
    sources={'s1': damping_coef, 's2':vel},
    target=damping,
    rel=R.Rmultiply,
    label='(c,vel,F)->damping',
)
hg.add_edge(
    sources=[u, '/gm', 'neg damping'],
    target=F,
    rel=R.Rsum,
    label='(u,/gm,-damping)->F',
    edge_props=['LEVEL', 'DISPOSE_ALL']
)
hg.add_edge(
    sources={'s1':F,'s2':mass},
    target=acc,
    rel=R.Rdivide,
    label='(F,mass)->acc',
    edge_props=['LEVEL', 'DISPOSE_ALL'],
    index_offset=1,
)
hg.add_edge(
    sources={'s1': acc, 's2': vel, 's3': step,},
    target=vel,
    rel=R.mult_and_sum(['s1', 's3'], 's2'),
    index_via=lambda s1, s2, **kw : s1 == s2 + 1,
    disposable=['s1', 's2'],
    label='(acc,vel,step)->vel',
)
hg.add_edge(
    sources={'s1': vel, 's2': height, 's3': step},
    target=height,
    rel=R.mult_and_sum(['s1', 's3'], 's2'),
    label='(vel,height,step)->height',
    index_via=lambda s1, s2, **kw : s1 == s2 + 1,
    disposable=['s1', 's2'],
)

# Discrete Event Simulation (DES) and passengers
boarding_edge = Edge('boarding edge', {}, boarding, R.Rsum, edge_props=['LEVEL', 'DISPOSE_ALL'])
exiting_edge = Edge('exiting edge', {}, exiting, R.Rsum, edge_props=['LEVEL', 'DISPOSE_ALL'])

def addPerson(label: str, goal_floor: int, start_floor: int, person_is_on: bool=False):
    """Adds a person to the model."""
    goalX = hg.add_node(Node(f'goal {label}', goal_floor, super_nodes=goal, description=f'goal floor for passenger {label}'))
    startX = hg.add_node(Node(f'start {label}', start_floor, super_nodes=start, description=f'start floor for passenger {label}'))
    onX = hg.add_node(Node(f'{label} is on', person_is_on, super_nodes=is_on, description=f'true if passenger {label} is on carriage'))
    is_boarding = hg.add_node(Node(f'{label} is boarding', description=f'true if passenger {label} is boarding carriage'))
    is_exiting = hg.add_node(Node(f'{label} is exiting', description=f'true if passenger {label} is exiting carriage'))

    hg.add_edge(
        sources={'s1': current_floor, 's2':onX, 's3':startX, 's4':goalX},
        target=onX,
        rel=Rset_status,
        index_via=lambda s1, s2, **kw : s1 == s2 + 1,
        disposable=['s1', 's2'],
        label=f'(curr_floor,{label}:is_on,start,goal)->{label} is on',
    )
    hg.add_edge(
        sources={'s1': current_floor, 's2':onX, 's3':startX, 's4':goalX},
        target=is_boarding,
        rel=Ris_boarding,
        index_via=lambda s1, s2, **kw : s1 == s2 + 1,
        disposable=['s1', 's2'],
        label=f'(curr_floor,{label}:is_on,start,goal)->{label} is boarding',
    )
    hg.add_edge(
        sources={'s1': current_floor, 's2':onX, 's3':goalX},
        target=is_exiting,
        rel=Ris_exiting,
        index_via=lambda s1, s2, **kw : s1 == s2 + 1,
        disposable=['s1', 's2'],
        label=f'(curr_floor,{label}:is_on,goal)->{label} is exiting',
    )
    boarding_edge.add_source_node(is_boarding)
    exiting_edge.add_source_node(is_exiting)

people = [
    ('A', 2, 0, False),
    ('B', 2, 0, False),
    ('C', 1, 3, False),
    ('D', 1, 0, True)
]
for person in people:
    addPerson(*person)
hg.insert_edge(boarding_edge)
hg.insert_edge(exiting_edge)

hg.add_edge(
    sources={'s1':occupancy, 's2':boarding, 's3':exiting},
    target=occupancy, 
    rel=lambda s1, s2, s3, **kwargs : s1 + s2 - s3,
    index_via=lambda s1, s2, s3, **kw : s2 == s3 and s2 == s1 + 1,
    edge_props=['DISPOSE_ALL'],
    label='(occ, boarding, exiting)->occupancy',
)

# Simulation inputs
inputs = {
    current_floor: 0,
    error: 0,
    destination_floor: 1,
}

def main():
    t = hg.solve(
        target=height,
        inputs=inputs,
        min_index=100,
    )
    print(t)
    # visualize(t)

def visualize(t: TNode):
    """Optional function for ploting results."""
    nodes = [height, occupancy, error]
    times = hg.solve(time, min_index=len(t.values['height'])).values['time']
    title='Hybrid Elevator Simulation'
    dashes = ['--', ':', '-.']
    legend = []

    for node in nodes:
        dash = dashes[nodes.index(node) % len(dashes)]
        legend_label = node.label + f', ({node.units})' if node.units is not None else ''
        values = t.values[node.label]
        plt.plot(times[:len(values)], values[:len(times)], 'k', lw=2, linestyle=dash) 
        legend.append(legend_label)

    plt.legend(legend)
    plt.ylabel('Variables')
    plt.xlabel('Time (s)')
    plt.title('Hybrid Elevator Simulation')
    plt.show()


if __name__ == '__main__':
    main()
