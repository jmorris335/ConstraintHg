=================================
Getting Started with ConstraintHg
=================================

This page introduces the ConstraintHg package. For the theory of constraint hypergraphs, see the `Overview <https://github.com/jmorris335/ConstraintHg/wiki/Overview>`_ page.

Tutorial
========

The goal of the ConstraintHg package is to allow developers to create universal, simulatable system models. To help motivate the concepts, this tutorial will follow along with the pendulum demo in the `demos package <https://github.com/jmorris335/ConstraintHg/blob/main/demos/demo_pendulum.py>`_. This example builds a model of a pendulum with damping, with dynamic equations given as:

- :math:`\alpha = -\frac{g}{r}\sin\theta` *(no damping)*
- :math:`\alpha = -\frac{g}{r}\sin\theta - c\omega` *(damping)*
- :math:`\omega_{i+1} = \Delta{}t * \alpha_{i+1} + \omega_i`
- :math:`\theta_{i+1} = \Delta{}t * \omega_{i+1} + \theta`

Where :math:`r` is the radius, :math:`g` is the gravitational acceleration, and :math:`\theta`, :math:`\omega`, and :math:`\alpha` are the angular position, velocity, and acceleration respectively. Note that the last two equations define a Eulerian first-order integration. 

Initialization
--------------

You'll need to start by importing the package into your script.

.. code-block:: python

    from constrainthg.hypergraph import Hypergraph, Node
    import constrainthg.relations as R

Each variable in the system should have its own node in the hypergraph. The easiest way to do this is to initialize the variables as nodes. The syntax is ``Node(<label>, <initial value>)``. Other parameters can be called such as units and descriptions which are convenient for documentation. 

.. code-block:: python

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

In the above we also defined some intermediate notes, these are variables that didn't show up in the original equations, but which will show up in the graph. This is because algebra often condenses multiple operations into a single equation, though for the hypergraph its better to break these operations out so that we can interface with the hidden variables. 

Edges
-----

Each edge in a constraint hypergraph maps the values of its source set to the value of its target node. Mathematically this is just function mapping, though you can think of it as assigning a value of a node to every ordered pair of another set of variables. For example, given nodes :math:`A, B \coloneq \lbrace 1, 2 \rbrace`, and :math:`C \coloneq \lbrace -1, 0, 1 \rbrace`, we could define a hyperedge such that:

======  ======  ======
 **A**   **B**   **C**
======  ======  ======
   1       1       0 
   1       2       -1 
   2       1       1 
   2       2       0
======  ======  ======

Note that every possible pair :math:`A` and :math:`B` need to be mapped to a corresponding value in :math:`C`. We'll see later on how to take a subset of values  in the relation only. Such a method could encode this table, or we could just note that :math:`C = A - B`. To pass this relationship into the hypergraph, we would just need to pass along a method that took in a value of :math:`A`, a value of :math:`B`, and returned the correct value of :math:`C`. The package requires these methods to take in an arbitrary set of inputs specified by ``*args, **kwargs``, as well as any keywords for specific arguments. For the example above, we might write a method like the following:

.. code-block:: python

    def subtract_A_from_B(A, B, *args, **kwargs):
    return A - B

To simplify coding, many relationships with the proper format have been specified in the `relations.py <https://github.com/jmorris335/ConstraintHg/blob/main/src/constrainthg/relations.py>`_ module. These are imported into the script with `import constrainthg.relations as R`, and then called as `R.Rsubtract` for example. We'll use mostly these provided relations in the demo, but we will need one custom function for the Eulerian integration. Let's define it now so we can pass it later on:

.. code-block:: python

    def integrate(s1, s2, s3, **kwargs):
        """First order Euler integrator, where s3 is the timestep."""
        return s1 * s3 + s2

*Note that the keywords are `s1`, `s2`, etc. The "s" stands for source, as in "source node one". This is the default keyword scheme. Although you can define you own naming scheme in most cases, the documentation uses this convention.*

Returning to the pendulum, let's put in some of the more simple edges. First we need to make the hypergraph:

.. code-block:: python

    hg = Hypergraph()

and then call the ``Hypergraph.add_edge()`` method. The syntax is ``add_edge([<node1>, <node2>, ...], <target_node>, <relation>, <label>)``. You can also pass specific keyword arguments by passing a dictionary of source nodes rather than a list, this allows you to reference the nodes by the passed keywords in the constraint method. The ``label`` is a string ID that helps us uniquely identify the edge.

.. code-block:: python

    hg.add_edge(theta0, theta, R.Rmean, label='theta0->theta')
    hg.add_edge(omega0, omega, R.Rmean, label='omega0->omega')
    hg.add_edge({'s1': g, 's2': r}, 'g/r', R.Rdivide, label='(g,r)->b1') #dictionary of source nodes ensures 'g' is the numerator.
    hg.add_edge(theta, s_theta, R.Rsin, label='theta->sine')
    hg.add_edge(`s_theta, 'g/r'], F, R.Rmultiply, label='(sine, b1)->F')
    hg.add_edge(`omega, c], 'beta2', R.Rmultiply, label='(omega, c)->b2')

Cycles
------

Normal constraint networks do not permit cycles, and for good reason. A cycle indicates that the value of a variable is dependent upon itself, an illogical proposition. However, there are many instances where variables can have multiple values, such as a variable that varies in time. In this case each progressive value of the variable *can* be dependent upon previous values of itself. This kind of relationships can be modeled easily enough: just make a different node for every instance of a variable. Let's say for example, that we wanted to solve for the position :math:`x` of a car moving at constant velocity :math:`v`. The first step would be to set the starting position :math:`x_0` and add it to the hypergraph. We can then add another node for the position after :math:`\Delta{}t` seconds had gone by and call it :math:`x_1`. The relationship between :math:`x_1` and :math:`x_0` is :math:`x_1 = x_0 + v\Delta{}t`, which we can easily make into a hyperedge. We could repeat this process for the position after :math:`2\Delta{}t` seconds had gone by, noting that :math:`x_2 = x_1 + v\Delta{}t`. This results in a drawn out hypergraph similar to the one shown in :ref:`Figure 1 <chg_simple>`.

.. figure:: https://github.com/user-attachments/assets/d42a03a5-9fd8-4e62-81bd-92a99c94b77e
    :alt: Simple CHG
    :width: 681px
    :align: center
    :name: chg_simple

    A simple hypergraph explicitly mapping out the relationships between variables

But it's not difficult to recognize a more succinct relationship: :math:`x_{i+1} = x_i + v\Delta{}t`. But how do we add the variables :math:`x_i` and :math:`x_{i+1}` to the hypergraph? The trick is to use cycles. Cycles enable arbitrary indexing of a variable, allowing us to express these recursive type expressions without have to explicitly map out every singe instance of a variable, as shown in `Figure 2 <chg_nonsimple>`. 

.. figure:: https://github.com/user-attachments/assets/cb8387cc-e005-4ed9-9247-2599f76f323b
    :alt: Non-simple CHG with a cycle
    :width: 681px
    :align: center
    :name: chg_nonsimple
    
    A non-simple hypergraph with a cycle

Though useful to the point of being essential to a constraint hypergraph's Cycles also cause significant technical problems that have to be addressed. The first is that we need a way to identify which instance of a variable is being referenced in the graph, because :math:`x_1` might be related to :math:`x_0`, but :math:`x_{308}` is not! So we introduce a *index* that allows us to note which version of a variable we're dealing with. ConstraintHg will keep track of indices for us, but whenever we have a cycle (where a variable becomes dependent upon itself) we need to manually indicate the index to employ. 

This occurs in the pendulum when we integrate the values (refer to the last two equations given at the beginning). In these cases, we have to indicate that the acceleration :math:`\alpha` being solved for by the model is really :math:`alpha_{i+1}`. The way to do this is supplying the ``index_offset`` parameter to the ``add_edge`` function call:

.. code-block:: python

    hg.addEdge(F, alpha, R.Rmean, label='F->alpha', index_offset=1)

This indicates that the node `alpha` is constrained to be the value of the node `F` and that whenever this constraint is applied the index of `alpha` should be increased by one.

Conditional Viability
---------------------

You might also have times when you need to reference a variable at a specific index, say the initial value of a variable, or the one from a previous instance. For example, equation 3 :math:`\left( \omega_{i+1} = \Delta{}t * \alpha_{i+1} + \omega_i \right)` should only reference a the latest solved instance of :math:`\alpha`: :math:`\alpha_{i+1}`. In this case you can access the index of a variable by passing it as another source node. The syntax for doing so is ``<label of the index psuedonode>: (<label of the actual node>, 'index')``. You can see this in the following calls for integrating :math:`\omega` and :math:`\theta`:

.. code-block:: python

    hg.add_edge({'s1': alpha, 's4': ('s1', 'index'),
                's2': omega, 's5': ('s2', 'index'),
                's3': time_step,}, omega, integrate,
                label='(alpha, omega, t)->omega',
                via=lambda s4, s5, **kwargs: s4 - 1 == s5)

    hg.add_edge({'s1': omega, 's4': ('s1', 'index'),
                's2': theta, 's5': ('s2', 'index'),
                's3': time_step,}, theta, integrate, 
                label='(omega, theta, t)->theta',
                via=lambda s4, s5, **kwargs: s4 - 1 == s5) 

*Note that these calls require you to provide a keyword label for each source node, so the set of source nodes must be passed as a `dict`.*

A new parameter being passed in the above code is ``via``, which stands for "viability." The ``via`` condition is a boolean function that must be satisfied in order for the edge to be solved. These arguments have the same syntax as the normal relation, meaning you can call specific function keywords and must allow for other inputs using `*args, **kwargs`. The default argument for ``via`` always returns true, meaning that an edge is always solveable. In the case above though, we override this viability with our own function that specifies that the index of ``alpha`` (labeled as ``s4``) must be one greater than the index of ``omega`` (labeled as ``s5``). 

Conditional viability is a powerful concept that allows us to create relationships between only a subset of values in a variable. For instance, say you have a variable for whether a door is open, with possible values ``['is_open', 'is_closed']``, and another variable specifying whether the door is locked, with values ``['is_locked', 'is_unlocked']``. You want to indicate that the door is always unlocked if it is open. But you don't necessarily know if the door is locked if it's closed. In order to add the edge, you'll need to add a viability method that resolves to true only if the door is open. Such an edge might look like: ``lambda door_status, *args, **kwargs : door_status == 'is_open'``. Then, if the door is not open, the edge will not be solved.

Simulation
----------

We're finally ready to simulate our hypergraph. You can first make sure that all the nodes connected to each other correctly by recursively printing out the hypergraph:

.. code-block:: python

    hg.printPaths('theta')

Once you've checked the model, solve for :math:`\alpha` by calling the `solve` method on the hypergraph class. It really is that easy! Note that you can pass initial values to the `solve` method, but we don't have to since we set these when we first created the Nodes.

.. code-block:: python

    alpha_val, found_values = hg.solve(alpha_val, to_print=True)
    print(t)

The values returned by ``solve`` are a ``TNode`` and a dictionary of the values found for each variable. This might not be every variable in the graph, because we might not have needed every variable in order to solve for the value of :math:`\alpha`. The ``TNode`` is a special type of node that structured as a recursive tree. This is because a path through a hypergraph is always a tree, so our valid solution solving for :math:`\alpha` is actually a tree with our initial values as leaves and the solved value (:math:`\alpha`) as its root. Setting the parameter ``to_print`` to ``True`` causes the solver to print out this path, which is fine for a short path like this. Longer paths can take longer to print than they do to solve though, so the default for this parameter is ``False``.

Printing the ``TNode`` outputs it's value, index, and cost. Note that we didn't pass a cost (or weight) to any of our edges, so they each assumed a default cost of 1.0. The takeaway from this is that the cost here indicates how many edges are in our solution tree, or how many steps the solver took in the found path. Because the solver performs a BFS minimizing cost, this will always be the shortest path (if such a path can be found), though we can change this by changing the default costs.

It's more common to want to find many values of :math:`\alpha` or :math:`\theta`, not just the first one, especially since we have set up our cycle so effectively. To do this we can create a new node that is the same value of :math:`\theta` but which can only be set if the index of :math:`\theta` is a specified amount, say five. Then we solve for this new node, which will guarantee that the value of :math:`\theta` will have to have been solved for at least five times.

.. code-block:: python

    hg.add_edge({'s1':theta, 's2':('s1', 'index'), 'final theta', R.equal('s1'), 
            via=lambda s2, *args, **kwargs : s2 >= 5, label='final theta')

    final_theta, found_values = hg.solve('final theta')

Model complexity
----------------

Up to know the hypergraph we have made looks something like this (with intermediate nodes removed):

.. figure:: https://github.com/user-attachments/assets/5512efdb-629c-46e7-9ac4-f919afc1442e
    :alt: CHG of a pendulum
    :width: 883px
    :align: center
    :name: chg_pend
    
    Pendulum hypergraph

The astute reader might have noticed that we have not added damping to the hypergraph yet. That's not because we don't know how, the edge is simple to add:

.. code-block:: python

    hg.add_edge({'s1':F, 's2':'beta2'}, alpha, R.Rsubtract, 
            label='(F, b2)->alpha', edge_props='LEVEL', index_offset=1)

*Note that the `edge_props` attribute is shorthand to set a viability condition that the indexes of all source nodes must be equivalent.*

However, the problem is that we've now combined multiple models with cycles. If you add the damping edge and solve for :math:`\theta`, you might notice that solving for the first (or second) instance of :math:`\theta` works fine. Same with :math:`\theta_3, \theta_4,` and even :math:`\theta_5`. However, much more than this and you get dramatic slowdown. Is that because the solver is broken?

Actually, it's because we've found a chokepoint: combining multiple model options with a cycle. Now every time the solver goes around the cycle it will find two possible values for :math:`\alpha`: one considering damping, and one without. Each of these values represents a unique path through the graph that must be advanced by the solver--after all, the solver doesn't know which one of these paths will wind up being the one that ends up solving for the final node. However, because of the way we have our model set up, each value for :math:`\alpha` gets used to solve for a new value of :math:`\theta` and :math:`\omega`, creating new paths, each of which will result in the generation of two new values of :math:`\alpha`. If you do an analysis, the bifurcation results in the creation of :math:`n_i = n_{i-1}(n_{i-1} + 1)` new paths for every :math:`i`-th cycle we iterate through. The number of paths at each cycle are shown in the following table:

===========   ===========
 :math:`i`     Paths (n)
===========   ===========
    0             1 
    1             2 
    2             6 
    3             42 
    4            1,806 
    5          3,263,442 
    6          10,650,056,950,806
===========   ===========

As can be seen from the table, this isn't just exponential growth, this is factorial exponential growth, growing so quickly that after just 8 cycles the number of paths outnumbers the number of atoms in the universe by nearly 8 to 1. Though pruning strategies exist, the best way to handle this is to bite the bullet and to avoid cycles with competing models. If you're building a hypergraph for model selection, then keep your cycles short or expand them out explicitly like in `Figure 1 <chg-simple>` If you need high-index count cycling, then turn off competing edges so that you don't generate multiple possible values for the variables in the cycle. 

In this case, we'll comment out the less-accurate edge predicting alpha without damping, leaving only the damping model in our hypergraph. Then we can change the viability function for our final node to only be true (thus ending the simulation) when :math:`\theta` and :math:`\omega` are below a certain magnitude, indicating settling. For instance: 

.. code-block:: python

    hg.add_edge({'s1':theta, 's2':('s1', 'index'), 's3': omega}, 'final theta', R.equal('s1'), 
            #    via=lambda s2, **kwargs : s2 >= 5, label='final theta')
            via=lambda s1, s3, **kwargs : abs(s1) < .05 and abs(s3) < .05, edge_props='LEVEL')

If you solve this graph, the solver will have to iterate through the cycle hundreds of times before it finds a solution, but it can do that fairly easily now that we've turned off the competing model. If you plot the found :math:`\theta` values against time, you should get a plot similar to the following:

.. figure:: https://github.com/user-attachments/assets/217ed55a-7ed3-41d2-a8ae-77f039f4c540
    :alt: Simulation results of damped pendulum
    :width: 693
    :align: center
    :name: chg_simulation

    Results of simulation solving for settling time of damped pendulum.

