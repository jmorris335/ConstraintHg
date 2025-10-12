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

Now that we can run simulations, the next step is debugging. It can be tricky to debug a constraint hypergraph. Traditional debugging methods are less effective since we're composing the functions inside a larger library. The best way to see what's going on during pathfinding is to use the logging options for ConstraintHg.

.. note:: ConstraintHg uses the default logging library. To learn how logging works, check out this tutorial `here <https://docs.python.org/3/howto/logging.html#basic-logging-tutorial>`_.

Enabling Logging
________________

By default, logging is turned off. There are two places that you can turn it on though: when initializing the :ref:`Hypergraph <hypergraph_class>` and when calling the :ref:`Hypergraph.solve <solve_method>` method. The preferred way to setup logging is to set the `logging level <https://docs.python.org/3/library/logging.html#logging-levels>`_. Logging levels are an enumerated type corresponding to a number. The lower the logging level, the more verbose the outputted log.

You can pass either the enumerated type or a plain integer to ConstraintHg to setup logging. To set the logging level to 20 (INFO) you might try:

.. code-block:: python

    from logging import INFO
    hg = Hypergraph(logging_level=logging.INFO)

.. code-block:: python

    hg.solve(<output>, logging_level=20)

If you setup the logger as an argument to ``Hypergraph.solve`` then the software logs only for that single simulation run, before resetting to whatever the logging level was before the simulation call.

Logging Levels
______________

The five enumerated logging levels are (from the `docs <https://docs.python.org/3/library/logging.html#logging-levels>`_):
    - logging.NOTSET: 0
    - logging.DEBUG: 10
    - logging:INFO: 20
    - logging.WARNING: 30
    - logging.ERROR: 40
    - logging:CRITICAL: 50

The level you pass determines how verbose the log output will be. ConstraintHg logs on the following levels, with higher levels include all items logged on lower ones:
    - logging.DEBUG (10): all edges and found combinations are listed, as well as search trees at each explored node.
    - logging.DEBUG+1 (11): debugging report is logged after a search is complete.
    - logging.DEBUG+2 (12): edges passed to `debug_edges` and nodes passed to `debug_nodes` as arguments to `Hypergraph.solve` are logged, as well as search trees at each explored node.
    - logging.INFO (20): start and end of a search are logged.
    - Warnings and errors are handled by the logging package (logging.WARNING and logging.ERROR). Note that these will *not* print to `sys.stderr`, though they will normally get raised and returned by the library.

General Debugging
_________

The log will show up in a file named ``constrainthg.log``. Here's an example log for simulating the pendulum at level 10 (DEBUG)::

    [2025-10-11 23:24 | INFO]: Begin search for theta
    [2025-10-11 23:24 | DEBUG]: Search trees: gravity, radius, theta0, omega0, damping coeff, time_step, time
    [2025-10-11 23:24 | DEBUG]: Exploring <gravity#0>, index=1:
    [2025-10-11 23:24 | DEBUG]: - Edge 0=<(g,r)->b1>, target=<g/r>:
    [2025-10-11 23:24 | DEBUG]: Search trees: radius, theta0, omega0, damping coeff, time_step, time
    [2025-10-11 23:24 | DEBUG]: Exploring <radius#0>, index=1:
    [2025-10-11 23:24 | DEBUG]: - Edge 0=<(g,r)->b1>, target=<g/r>:
    [2025-10-11 23:24 | DEBUG]:    - Combo 0: radius#0 (1), gravity#0 (1)-> <g/r=-20, index=1, cost=1>
    [2025-10-11 23:24 | DEBUG]: Search trees: theta0, omega0, damping coeff, time_step, time, g/r
    [2025-10-11 23:24 | DEBUG]: Exploring <theta0#0>, index=1:
    [2025-10-11 23:24 | DEBUG]: - Edge 0=<theta0->theta>, target=<theta>:
    [2025-10-11 23:24 | DEBUG]:    - Combo 0: theta0#0 (1)-> <theta=0.5236, index=1, cost=1>
    [2025-10-11 23:24 | DEBUG]: Search trees: omega0, damping coeff, time_step, time, g/r, theta
    [2025-10-11 23:24 | DEBUG]: Exploring <omega0#0>, index=1:
    [2025-10-11 23:24 | DEBUG]: - Edge 0=<omega0->omega>, target=<omega>:
    [2025-10-11 23:24 | DEBUG]:    - Combo 0: omega0#0 (1)-> <omega=0, index=1, cost=1>
    [2025-10-11 23:24 | DEBUG]: Search trees: damping coeff, time_step, time, g/r, theta, omega
    [2025-10-11 23:24 | DEBUG]: Exploring <damping coeff#0>, index=1:
    [2025-10-11 23:24 | DEBUG]: - Edge 0=<(omega, c)->b2>, target=<beta2>:
    [2025-10-11 23:24 | DEBUG]: Search trees: time_step, time, g/r, theta, omega
    [2025-10-11 23:24 | DEBUG]: Exploring <time_step#0>, index=1:
    [2025-10-11 23:24 | DEBUG]: - Edge 0=<(alpha, omega, t)->omega>, target=<omega>:
    [2025-10-11 23:24 | DEBUG]: - Edge 1=<(omega, theta, t)->theta>, target=<theta>:
    [2025-10-11 23:24 | DEBUG]: - Edge 2=<(time,time)->time>, target=<time>:
    [2025-10-11 23:24 | DEBUG]: Search trees: time, g/r, theta, omega
    [2025-10-11 23:24 | DEBUG]: Exploring <time#0>, index=1:
    [2025-10-11 23:24 | DEBUG]: - Edge 0=<(time,time)->time>, target=<time>:
    [2025-10-11 23:24 | DEBUG]: (Disposed of 1 nodes in (time,time)->time)
    [2025-10-11 23:24 | DEBUG]:    - Combo 0: time_step#0 (1), time#0 (1)-> <time=0.03, index=2, cost=1>
    [2025-10-11 23:24 | DEBUG]: Search trees: g/r, theta, omega, time
    [2025-10-11 23:24 | DEBUG]: Exploring <g/r#1>, index=1:
    [2025-10-11 23:24 | DEBUG]: - Edge 0=<(sine, b1)->F>, target=<gravitational force>:
    [2025-10-11 23:24 | DEBUG]: Search trees: theta, omega, time
    [2025-10-11 23:24 | DEBUG]: Exploring <theta#2>, index=1:
    [2025-10-11 23:24 | INFO]: Finished search for theta with value of 0.5235983333333333
    [2025-10-11 23:24 | Level 11]: 
    Debugging Report for theta:
        Final search counter: 4
        Explored edges (# explored | # processed | # valid solution):
            <(g,r)->b1>: 2 | 1 | 1
            <(time,time)->time>: 2 | 1 | 1
            <theta0->theta>: 1 | 1 | 1
            <omega0->omega>: 1 | 1 | 1
            <(omega, c)->b2>: 1 | 0 | 0
            <(alpha, omega, t)->omega>: 1 | 0 | 0
            <(omega, theta, t)->theta>: 1 | 0 | 0
            <(sine, b1)->F>: 1 | 0 | 0

The DEBUG log has the following structure:

1. Search trees: print a list of all nodes with known values. These are the ends of all paths currently known to the solver.
2. Explore a node: select a node from the possible search trees and explore it.
3. List edges: list all edges rooted in the node, including their target.
4. List found combinations: For every edge, list every combination of source nodes known to the solver. If the combination results in a valid mapping (passing the ``via`` statements), then print the calculated output. Also list if any nodes were disposed.
5. Debugging report: The end of simulation includes a debugging report that lists all the edges encountered by the solver, and three metrics for them:  

   1. # explored: The first metric is how many times the edge was encountered. Solved edges will be encountered at least as many times as source nodes that that they have (unless the source nodes were given as inputs).
   2. # processed: The amount of times a combination was found for the edge. A combination is when every source node for the edge has a known value.
   3. # valid solution: The amount of times a combination resulted in setting the value of the target node. Combinations that don't pass all the ``via`` statements will result in this number being smaller than the # processed metric.

Fine-tuned Debugging
____________________

You can also get more precise information on how an edge or node is being handled by the solver by passing their labels as arguments to the ``Hypergraph.solve`` method. Passing a node label to the ``debug_nodes`` parameter will result in the solver outputting the simulation path every time that node is encountered, while passing an edge label to the ``debug_edges`` parameter will result in the values and indices of all source nodes being shown for each combination in the edge. Both are helpful when debugging particularly involved models.

For example, we might have trouble with our integration. We can debug the system by passing the edge lable (``(alpha, omega, t)->omega``) to ``debug_edges``:

.. code-block:: python

    alpha_tnode = hg.solve(theta, min_index=2, logging_level=12, debug_edges=['(alpha, omega, t)->omega'])

Note that set the logging_level to 12 (DEBUG + 2). This keeps the log from printing every edge. Instead, it will only log debugging information for our passed edge. The resulting log is::

    [2025-10-11 23:37 | INFO]: Begin search for theta
    [2025-10-11 23:37 | Level 12]: - Edge 0=<(alpha, omega, t)->omega>, target=<omega>:
    [2025-10-11 23:37 | Level 12]:  - alpha: 
    [2025-10-11 23:37 | Level 12]:  - omega: 
    [2025-10-11 23:37 | Level 12]:  - time_step: 0.03(1)
    [2025-10-11 23:37 | Level 12]: - Edge 0=<(alpha, omega, t)->omega>, target=<omega>:
    [2025-10-11 23:37 | Level 12]:  - alpha: 
    [2025-10-11 23:37 | Level 12]:  - omega: 0.0(1)
    [2025-10-11 23:37 | Level 12]:  - time_step: 0.03(1)
    [2025-10-11 23:37 | Level 12]: - Edge 0=<(alpha, omega, t)->omega>, target=<omega>:
    [2025-10-11 23:37 | Level 12]:  - alpha: -9.9(2)
    [2025-10-11 23:37 | Level 12]:  - omega: 0.0(1)
    [2025-10-11 23:37 | Level 12]:  - time_step: 0.03(1)
    [2025-10-11 23:37 | Level 12]: - Edge 0=<(alpha, omega, t)->omega>, target=<omega>:
    [2025-10-11 23:37 | Level 12]:  - alpha: 
    [2025-10-11 23:37 | Level 12]:  - omega: -0.2(2)
    [2025-10-11 23:37 | Level 12]:  - time_step: 0.03(1)
    [2025-10-11 23:37 | INFO]: Finished search for theta with value of 0.5145983402275627

The log shows that our edge was encountered four times. It also shows the values for the source nodes at each encounter: first the solver found ``time_step``, then ``omega``, then ``alpha``, which resulted in solving the edge.

We could also debug a certain node, say ``alpha``:

.. code-block:: python

    alpha_tnode = hg.solve(theta, min_index=2, logging_level=12, debug_nodes=['alpha'])

This prints the following log::

    [2025-10-11 23:41 | INFO]: Begin search for theta
    [2025-10-11 23:41 | Level 12]: Exploring alpha, index: 2, leading edges: (alpha, omega, t)->omega
    └──alpha=-10, index=2, cost=7
        ├──beta2=0, index=1, cost=2
        │  ├──omega=0, index=1, cost=1
        │  │  └──omega0=0, index=1
        │  └──damping coeff=1.5, index=1
        └──gravitational force=-10, index=1, cost=4
            ├──sine theta=0.5, index=1, cost=2
            │  └──theta=0.5236, index=1, cost=1
            │     └──theta0=0.5236, index=1
            └──g/r=-20, index=1, cost=1
                ├──radius=0.5, index=1
                └──gravity=-10, index=1

    [2025-10-11 23:41 | INFO]: Finished search for theta with value of 0.5145983402275627

Here we see that the node ``alpha`` was encountere once, and the simulation path at that time had 7 edges in it.

.. attention:: Printing simulation paths like this is slow. Furthermore, they can get long and confusing as your model grows. Debugging nodes is generally only good for smaller models or short paths.

As a best practice to debugging: use the debugging report, tracing the lines, before moving to the individual entries in the log. Another trick is to simulate small. If you can't solve, for instance, ``alpha`` at index 170, then try simulating ``alpha`` at index 2. Or ``omega``, or ``F``. Make sure the base paths are working before launching into the convoluted cycles. Finally, if your simulation times out, check to see if you remembered to dispose of all dynamic nodes in a cycle.

What Next?
----------

This tutorial covers all the basics of using ConstraintHg. To see more complex examples, check out the :doc:`demonstrations </demos>`. You can also leave comments, ask questions, or show how you're using the software on our :doc:`discussion board </about/contact>`.