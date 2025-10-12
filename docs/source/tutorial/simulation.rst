Simulation
==========

**Simulation** is the act of artificially establishing information about a system. It's synonyms are prediciton, inference, estimation, and decision-making. Performing a simulation is the act of transforming a set of observed values (inputs) into an unobserved, unknown variable (the output).

Running Our First Simulation
----------------------------

Usually we create simulations *imperatively*, by taking our inputs and specifying a procedure to transform them into the output. But a constraint hypergraph allows these procedures to be discovered automatically, allowing high-level *declarative* modeling. Each path in a hypergraph represents a possible simulation we can run. To setup a simulation, we use the pathfinding algorithms in ConstraintHg to find a path from a set of inputs to our desired output.

Validation
__________

First, make sure that all the nodes are connected to each other correctly by recursively printing out the hypergraph: 

.. code-block:: python

    print(hg.printPaths('theta'))

You should get the following output:

.. code-block::

    ──theta, index=1, cost=1
        ├──theta0, index=1
        ├◯─theta[CYCLE], index=1
        │  └──theta0, index=1
        ├◯─omega, index=1, cost=1
        │  ├◯─omega[CYCLE], index=1
        │  ├◯─alpha, index=1, cost=4
        │  │  └──gravitational force, index=1, cost=3
        │  │     ├◯─sine theta, index=1, cost=1
        │  │     │  └──theta[CYCLE], index=1
        │  │     │     └──theta0, index=1
        │  │     └●─g/r, index=1, cost=1
        │  │        ├◯─radius, index=1
        │  │        └●─gravity, index=1
        │  ├●─time_step, index=1
        │  └──omega0, index=1
        └●─time_step, index=1

Solving
__________

Once you've checked the model, solve for :math:`\alpha` by calling the :ref:`solve <solve_method>` method on the hypergraph class. It really is that easy! Note that you can pass initial values to the `solve` method, but we don't have to since we set these when we first created the Nodes.

.. code-block:: python

    alpha_tnode = hg.solve(alpha_val)
    print(alpha_tnode)

This returns:

.. code-block::

    alpha=-10, index=2, cost=5

The object returned by ``Hypergraph.solve`` is a :ref:`TNode <tnode_class>`, which stands for tree node. It recursively defines the simulation path ending at :math:`\alpha`, and allows us to trace back out the simulation. For instance, calling ``alpha_tnode.print_tree()`` returns the simulation:

.. code-block::

    └──alpha=-10, index=2, cost=5
        └──gravitational force=-10, index=1, cost=4
            ├──sine theta=0.5, index=1, cost=2
            │  └──theta=0.5236, index=1, cost=1
            │     └──theta0=0.5236, index=1
            └──g/r=-20, index=1, cost=1
                ├──radius=0.5, index=1
                └──gravity=-10, index=1

This time with values specified for the nodes. To find this path, the solver runs a Breadth-First Search, which starts from all the inputs defined for the system and iteratively searches all possible paths until one is found leading to the output. This is shown in the animation below:

.. figure:: https://github.com/user-attachments/assets/cb8387cc-e005-4ed9-9247-2599f76f323b
    :alt: Animation of solving a constraint hypergraph
    :width: 681px
    :align: center
    :name: animationfig

    *Visualization of a constraint hypergraph being solved by ConstraintHg*

.. note:: The values for all the nodes in the simulation are stored in a dict, which you can access by calling ``alpha_tnode.values``. The format is ``{<label> : [val1, val2, ...]}``.

Deeper Searching
----------------

It's more common to want to find many values of :math:`\alpha` or :math:`\theta`, not just the first one, especially since we have set up our cycle so effectively. To do this we can set the minimum cycle index of the output that the solver should return, set by the ``min_index`` argument for the :ref:`Hypergraph.solve <solve_method>` method. For instance, calling ``hg.solve(alpha, min_index=3)`` returns:

.. code-block::

    └──alpha=-9.844, index=3, cost=11
        └──gravitational force=-9.844, index=2, cost=10
            ├──sine theta=0.4922, index=2, cost=9
            │  └──theta=0.5146, index=2, cost=8
            │     ├──theta=0.5236, index=1, cost=1
            │     │  └──theta0=0.5236, index=1
            │     ├──omega=-0.3, index=2, cost=7
            │     │  ├──omega=0, index=1, cost=1
            │     │  │  └──omega0=0, index=1
            │     │  ├──alpha=-10, index=2, cost=5
            │     │  │  └──gravitational force=-10, index=1, cost=4
            │     │  │     ├──sine theta=0.5, index=1, cost=2
            │     │  │     │  └──theta=0.5236, index=1, cost=1 (derivative)
            │     │  │     └──g/r=-20, index=1, cost=1
            │     │  │        ├──radius=0.5, index=1
            │     │  │        └──gravity=-10, index=1
            │     │  └──time_step=0.03, index=1
            │     └──time_step=0.03, index=1
            └──g/r=-20, index=1, cost=1 (derivative)

Model Selection
---------------

Up to know the hypergraph we have made looks something like this (with intermediate nodes removed):

.. figure:: https://github.com/user-attachments/assets/5512efdb-629c-46e7-9ac4-f919afc1442e
    :alt: CHG of a pendulum
    :width: 883px
    :align: center
    :name: chg_pend_advanced
    
    *Pendulum hypergraph*

The astute reader might have noticed that we have not added damping to the hypergraph yet. That's not because we don't know how, the edge is simple to add:

.. code-block:: python

    hg.add_edge({'s1':F, 's2':'beta2'}, alpha, R.Rsubtract, 
            label='(F, b2)->alpha', edge_props='LEVEL', index_offset=1)

.. Hint:: Use the `edge_props` attribute as shorthand to set a viability condition that the indexes of all source nodes should be equivalent.

This gives us competing models: two different ways to solve for :math:`\alpha`. The pathfinding algorithm deals with this by treating both branches as viable, so that the path with the minimum cost will be returned as the optimum simulation. We haven't assigned edge weights, so this means the path with the least number of steps would be the one returned. To get our model to use our damping relationship, we can either comment out the other edge (with the label ``F->alpha``), or we can give that edge a very high weighting to make it more expensive to traverse. To do that, write:

.. code-block:: python

    hg.add_edge(
        {'F': F},
        target=alpha,
        rel=R.Rmean,
        index_offset=1,
        disposable=['F'],
        weight=100, # <- Add this line in
        label='F->alpha',
    )

Because we added the disposable tag, our solver can handle the complexity of the diverging branches. Let's try running a simulation over 3 seconds. If you plot the found :math:`\theta` values against time, you should get a plot similar to the following:

.. code-block:: python
    theta_tnode = hg.solve(theta, min_index=170)
    thetas, omegas = theta_tnode.values['theta'], theta_tnode.values['omega']
    time = hg.solve(time, min_index=170).values['time']

    import matplotlib.pyplot as plt
    length = min(len(time), len(thetas), len(omegas))
    plt.plot(time[:length], thetas[:length])
    plt.plot(time[:length], omegas[:length])
    plt.show()

.. figure:: https://github.com/user-attachments/assets/217ed55a-7ed3-41d2-a8ae-77f039f4c540
    :alt: Simulation results of damped pendulum
    :width: 693
    :align: center
    :name: chg_simulation_advanced

    *Results of simulation solving for settling time of damped pendulum.*

.. note:: We solve the hypergraph twice in this example, since time is not part of the simulation path. That means we didn't need to know time to solve for :math:`\theta`.

Logging
-------

Now that we can run simulations, the next step is debugging. 