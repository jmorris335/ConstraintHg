Cycles
======

Explanation of Cycles
----------------------

We would usually think that constraint networks should not permit cycles, and for good reason. A cycle indicates that the value of a variable is dependent upon itself, an illogical proposition for a causal model.

However, there are many instances where variables might represent multiple values, such as a variable that varies in time. In this case each progressive value of the variable might be dependent upon previous values of itself. This kind of relationships can be modeled easily enough: just make a different node for every instance of a variable.

.. note:: The following example is modeled as a simple demo in the main package, available `here <https://github.com/jmorris335/ConstraintHg/blob/main/demos/demo_linear_motion.py>`_.

Let's say for example, that we wanted to solve for the position :math:`x` of a car moving at constant velocity :math:`v`. The first step would be to set the starting position :math:`x_0` and add it to the hypergraph. We can then add another node for the position after :math:`\Delta{}t` seconds had gone by and call it :math:`x_1`. The relationship between :math:`x_1` and :math:`x_0` is :math:`x_1 = x_0 + v\Delta{}t`, which we can easily make into a hyperedge. We could repeat this process for the position after :math:`2\Delta{}t` seconds had gone by, noting that :math:`x_2 = x_1 + v\Delta{}t`. This results in a drawn out hypergraph similar to the one shown in :ref:`Figure 1 <chg_simple>`.

.. figure:: https://github.com/user-attachments/assets/d42a03a5-9fd8-4e62-81bd-92a99c94b77e
    :alt: Simple CHG
    :width: 681px
    :align: center
    :name: chg_simple

    *A simple hypergraph explicitly mapping out the relationships between variables*

Such a modeling process is not only tedious, it lacks expressability. What we really want to model is the relationship :math:`x_{i+1} = x_i + v\Delta{}t`, rather than every incremental relation. The trick for adding the variables :math:`x_i` and :math:`x_{i+1}` to the hypergraph is to use cycles.

Cycles enable arbitrary indexing of a variable, allowing us to express these recursive type expressions without have to explicitly map out every single instance of a variable, as shown in `Figure 2 <chg_nonsimple>`.

.. figure:: https://github.com/user-attachments/assets/cb8387cc-e005-4ed9-9247-2599f76f323b
    :alt: Non-simple CHG with a cycle
    :width: 681px
    :align: center
    :name: chg_nonsimple
    
    *A non-simple hypergraph with a cycle*

If you call the ``print_paths`` method on the `above constraint hypergraph <https://github.com/jmorris335/ConstraintHg/blob/main/demos/demo_linear_motion.py>`_, you'll get the following output:

.. code-block::

    └──x_n, index=1, cost=3
        ├◯─x, index=1, cost=2
        │  ├◯─x[CYCLE], index=1
        │  └●─delta_x, index=1, cost=1
        │     ├◯─velocity, index=1
        │     └●─delta_t, index=1
        └●─n, index=1

Note that the solver found the cycle, and highlighted it in the output.

Problems with Cycles
--------------------

Representing cycles causes significant technical problems that have to be addressed. The first is that we need a way to identify which instance of a variable is being referenced in the graph, because :math:`x_1` might be related to :math:`x_0`, but :math:`x_{308}` is not! To do we introduce a **index** that allows us to note which version of a variable we're dealing with. ConstraintHg will keep track of indices for us, but whenever we have a cycle (where a variable becomes dependent upon itself) we need to manually indicate the index to employ.

This occurs in the pendulum when we integrate the values (refer to the last two equations given at the beginning). In these cases, we have to indicate that the acceleration :math:`\alpha` being solved for by the model is really :math:`alpha_{i+1}`. The way to do this is supplying the ``index_offset`` parameter to the ``add_edge`` function call. Go ahead and add ``index_offset=1`` to the last edge in your script, so that the line looks like this:

.. code-block:: python

    hg.addEdge(F, alpha, R.Rmean, label='F->alpha', index_offset=1)

This indicates that the node `alpha` is constrained to be the value of the node `F` and that whenever this constraint is applied the index of `alpha` should be increased by one.

.. important:: To use a cycle, the solver needs a condition for exiting the cycle.

To set a condition for exiting a cycle requires an edge that is only followed for *some* values of it's input source. This is called conditional viability. You can learn more about this :doc:`here <viability>` or by following the navigation below. Otherwise, jump to :doc:`simulation </tutorial/simulation>`.