Advanced Topics
===============

Logging
-------

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

Because we added the disposable tag, our solver can handle the complexity of the diverging branches. Let's try running a simulation over 3 seconds


If you solve this graph, the solver will have to iterate through the cycle hundreds of times before it finds a solution, but it can do that fairly easily now that we've turned off the competing model. If you plot the found :math:`\theta` values against time, you should get a plot similar to the following:

.. figure:: https://github.com/user-attachments/assets/217ed55a-7ed3-41d2-a8ae-77f039f4c540
    :alt: Simulation results of damped pendulum
    :width: 693
    :align: center
    :name: chg_simulation_advanced

    *Results of simulation solving for settling time of damped pendulum.*

