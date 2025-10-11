Modeling
========

ConstraintHg is a model *organizer*. That means it can take a given model and structure it so that other models can connect to it without information or meaning being lost. However, you still have to do all the work of providing the model. It is often more convenient to do this work in a different framework. The pendulum example, for instance, can be modeled using Newtonian physics, or setting up the standard Euler-Langrange equations.

.. note:: If you want to see a discussion of modeling the pendulum dynamics, check out the overview :ref:`here <pendulum_example>`.

In the linked example, we derive the following constraint hypergraph, which we'll now setup in the Python script.

.. figure:: https://github.com/user-attachments/assets/5512efdb-629c-46e7-9ac4-f919afc1442e
    :alt: CHG of a pendulum
    :width: 883px
    :align: center
    :name: chg_pend_intro
    
    *Constraint hypergraph of the pendulum.*

The first thing to do is to initialize the hypergraph:

.. code-block::

    hg = Hypergraph()

There are a few options you can call when initializing this, such as setting up logging. More information is available at the :ref:`API <hypergraph_init>`. Now we can start passing in the variables.

Nodes
-----

The constraint hypergraph has several variables which we'll want to include in our model. Think of a the set of variables as all the information we might want to know about the pendulum. Each variable becomes a node in the graph.

.. code-block:: python

    g = hg.add_node("gravity", -10)
    r = hg.add_node("radius", 0.5)
    theta0 = hg.add_node("theta0", 3.14159/6)
    theta = hg.add_node("theta")
    d_theta = hg.add_node("delta theta")
    s_theta = hg.add_node("sine theta")
    F = hg.add_node("gravitational force")
    omega0 = hg.add_node("omega0", 0.0)
    omega = hg.add_node("omega")
    d_omega = hg.add_node("delta omega")
    c = hg.add_node("damping coeff", 1.5)
    alpha = hg.add_node("alpha")
    time_step = hg.add_node("time_step", .03)

The ``hg.add_node()`` method returns a :ref:`Node <node_class>` object, which we can use later to set up the edges in the graph.

In the above we also defined some intermediate notes, these are variables that didn't show up in the original equations, but which will show up in the graph. This is because algebra often condenses multiple operations into a single equation, though for the hypergraph its better to break these operations out so that we can interface with the hidden variables. 

Edges
-----
Each edge in a constraint hypergraph maps the values of its source set to the value of its target node. Mathematically this is just function mapping, though you can think of it as assigning a value of a node to every ordered pair of another set of variables. For example, given nodes :math:`A, B := \lbrace 1, 2 \rbrace`, and :math:`C := \lbrace -1, 0, 1 \rbrace`, we could define a hyperedge such that:

======  ======  ======
 **A**   **B**   **C**
======  ======  ======
   1       1       0 
   1       2       -1 
   2       1       1 
   2       2       0
======  ======  ======

Note that every possible pair :math:`A` and :math:`B` need to be mapped to a corresponding value in :math:`C`. We'll see later on how to take a subset of values  in the relation only. Such a method could encode this table, or we could just note that :math:`C = A - B`. To pass this relationship into the hypergraph, we would just need to pass along a method that took in a value of :math:`A`, a value of :math:`B`, and returned the correct value of :math:`C`. 

The package requires these methods to take in an arbitrary set of inputs specified by ``*args, **kwargs``, as well as any keywords for specific arguments. For the example above, we might write a method like the following:

.. code-block:: python

    def subtract_A_from_B(A, B, *args, **kwargs):
        return A - B

To simplify coding, many relationships with the proper format have been specified in the :doc:`relations </api/relations>` module. These were imported into the script with ``import constrainthg.relations as R``, and then called as ``R.Rsubtract`` for example. We'll use mostly these provided relations in the demo, but we will need one custom function for the Eulerian integration. Let's define it now so we can pass it later on:

.. code-block:: python

    def integrate(step, slope, initial_val, **kwargs):
        """First order Euler integrator."""
        return step * slope + initial_val

Returning to the pendulum, let's put in some of the more simple edges. The main method here is :ref:`Hypergraph.add_edge <meth_add_edge>`, whose syntax is ``add_edge([<node1>, <node2>, ...], <target_node>, <relation>, <label>)``. You can also pass specific keyword arguments by passing a dictionary of source nodes rather than a list, this allows you to reference the nodes by the passed keywords in the constraint method. The ``label`` is an optional string ID that helps us uniquely identify the edge.

.. code-block:: python

    hg.add_edge(theta0, theta, R.Rmean, label='theta0->theta')
    hg.add_edge(omega0, omega, R.Rmean, label='omega0->omega')
    hg.add_edge({'s1': g, 's2': r}, 'g/r', R.Rdivide, label='(g,r)->b1') #dictionary of source nodes ensures 'g' is the numerator.
    hg.add_edge(theta, s_theta, R.Rsin, label='theta->sine')
    hg.add_edge([s_theta, 'g/r'], F, R.Rmultiply, label='(sine, b1)->F')
    hg.add_edge([omega, c], 'beta2', R.Rmultiply, label='(omega, c)->b2')
    hg.add_edge(F, alpha, R.Rmean, label='F->alpha')

Printing
--------

Now that we have our basic hypergraph, it's a good idea to query its structure to make sure we put everything in the right place. The package has :ref:`some <conn_class>` basic functionality for printing the paths in a Hypergraph to the terminal.

.. note:: A **path** in a hypergraph is a chain of edges through the hypergraph. In a hypergraph, this chain appears as a tree.

Let's start by printing all the possible paths for calculating the angular acceleration (:math:`\alpha`) of the pendulum. To do this, add the following line to the script and run the program:

.. code-block:: python

    print(hg.print_paths(alpha))

You should get the following output in your terminal:

.. code-block::

    └──alpha, index=1, cost=5
        └──gravitational force, index=1, cost=4
            ├◯─sine theta, index=1, cost=2
            │  └──theta, index=1, cost=1
            │     └──theta0, index=1
            └●─g/r, index=1, cost=1
                ├◯─radius, index=1
                └●─gravity, index=1

Each section of the output corresponds to an node in a path that eventually leads to ``alpha``. The source nodes for the edges leading to the higher are indented on the next lines. If there is one source node, then it's given with a single angle pipe ``└──``. Otherwise, for multiple sources, the nodes are specified with circles ``├◯─``. The last source node for an edge is distinguished with a filled circle ``└●─``.

In our output, you can see that there is only one path for calculating ``alpha``, with five edges in the path. 

.. note:: The ``cost`` of a node is taken by summing the weights of all edges in the path leading up to it. The method prints the minimum summation. Since we used the default edge weight of 1, here the cost indicates how many edges form the shortest path to the given node.

We can start :doc:`simulating </tutorial/simulation>` any path in the graph immediately, but to get full functionality we also need to learn about cycles, as well as figure out what the ``index`` parameter means. Click :doc:`here <cycles>` to go to the next step or use the navigation below.