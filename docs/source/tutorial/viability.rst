Conditional Viability
=====================

Intuitive Understanding
-----------------------
A function is an algebraic relation that maps every value of one set (the domain) to a value in another set (the codomain). We usually represent our domain set as a combination of variables. However, sometimes, we don't have a relationship for every value in an input set.

For example, let's take our pendulum, which says that :math:`\alpha = -\frac{g}{l}\sin\theta`. That means we have a mapping to :math:`\alpha` for every combination of the variables :math:`g`, :math:`l`, and :math:`\theta`. But that's not *totally* true--if :math:`l` is 0, then our equation is undefined. In other words we don't know what :math:`\alpha` is when the radius of our pendulum is zero!

Via Statements
--------------
How do we represent this in our model? What we're trying to do is say that our equation is only applicable for a subset of values in the function's domain. But rather than creating a whole new set of variables to represent :math:`g`, :math:`l`, and :math:`\theta` except for when :math:`l` is 0, we can add what's called a ``via`` statement.

A :ref:`via <edge_init_method>` statement is a boolean method that takes in the values for the edge's source nodes, and returns ``True`` if the values are part of the relations valid subdomain. ``via`` statements are typically given using a ``lambda`` method. 

.. hint:: If you're not familiar with ``lambda`` methods, you can read more about them `here <https://www.w3schools.com/python/python_lambda.asp>`_.

For the example above, we might write a lambda method as the following:

.. code-block:: python

    via=lambda l : l != 0

Note that the arguments for a ``via`` statement are the dict keys of the source nodes passed to an edge.

Conditional viability is a powerful concept that allows us to create relationships between only a subset of values in a variable. For instance, say you have a variable for whether a door is open, with possible values ``['is_open', 'is_closed']``, and another variable specifying whether the door is locked, with values ``['is_locked', 'is_unlocked']``. You want to indicate that the door is always unlocked if it is open. But you don't necessarily know if the door is locked if it's closed. In order to add the edge, you'll need to add a viability method that resolves to true only if the door is open. Such an edge might look like: ``lambda door_status : door_status == 'is_open'``. Then, if the door is not open, the edge will not be solved.

Psuedo Nodes
------------

Sometimes you want to use a property of a node in a ``via`` statement (or perhaps in the main relation). This is tricky since node properties update live during a simulation run. To get around this, you can call what's called a **pseudo node**: a fake node that gets passed to a relation and whose value is a property of some source node for the edge.

To create a pseudo node, we pass a length 2 tuple to the sources of an edge. The first value of the tuple is the key for the source node we're getting the property of, and the second value is the name of the property.

.. important:: For a source node to have a key means that it was passed as a dictionary. This means to use pseudo nodes you *have* to pass the source nodes to the edge in a dict structure.

We can access any property defined for the `:ref:`Node <node_class>`` class: ``index``, ``label``, ``units``, etc. However, the most common one is index. Here's an example (taken from the `linear motion demo <https://github.com/jmorris335/ConstraintHg/blob/main/demos/demo_linear_motion.py>`_) of using a node's index in a ``via`` statement:

.. code-block:: python

    hg.add_edge(
        sources={'x': x, 'i': ('x', 'index'), 'n': n}, #This must be a dict, with the pseudo node passed as a tuple
        target=xn,
        rel=lambda x : x
        via=lambda i, n : i >= n, #Here we access the node's index
        label='x_i, i -> x_n',
    )


Index Via Statements
--------------------

Because the index of a node is called so many times, ConstraintHg has a shortcut to make it easier to reference it. These are called ``index_via`` statements, are they are syntactic sugar for the ``(<node_key, 'index'>)`` pseudo-node call.

An ``index_via`` statement works exactly the same as a ``via`` statement, except when instead of the value of a node being passed to the Boolean method, the index of the node is passed. For example, the above edge could be rewritten as:

.. code-block:: python

    hg.add_edge(
        sources={'x': x},
        target=xn,
        rel=lambda x : x
        index_via=lambda i : i >= 4,
        label='x_i-> x_n',
    )

Note that we no longer have to define a ``via`` statement, because we were only working with the node's index value in the first place.

Closing the Pendulum Cycle
--------------------------

We can use our ``index_via`` statements to fully close the loop for the pendulum using the ``integrate`` relation we defined back in :doc:`modeling </tutorial/modeling>` step. These loops indicate that :math:`\alpha` can be integrated to get :math:`\omega`, and :math:`\omega` can be integrated to get :math:`\theta`.

Add the following lines to your script:

.. code-block:: python

    hg.add_edge(
        sources={'slope': alpha, 'initial_val': omega, 'step': time_step},
        target=omega,
        rel=Rintegrate,
        index_via=lambda slope, initial_val: slope - 1 == initial_val,
        disposable=['slope', 'intial_val'],
        label='(alpha, omega, time_step)->omega',
    )

    hg.add_edge(
        sources={'slope': omega, 'initial_val': theta, 'step': time_step},
        target=theta,
        rel=Rintegrate,
        index_via=lambda slope, initial_val: slope - 1 == initial_val,
        disposable=['slope', 'intial_val'],
        label='(omega, theta, time_step)->theta',
    )

.. note:: Note that we dispose of ``slope`` and ``initial_val`` because those indices are constantly changing, as discussed in the :ref:`previous step <cycle_complexity>`. The time step, on the other hand, is a constant value, so we shouldn't dispose of it.

We also need to add a similar edge for time. Time updates on its own loop, and therefore needs its own index_offest. Add the following edge to your script:

.. code-block:: python

    hg.add_edge(
        sources={'time': time, 'step': time_step},
        target=time,
        rel=R.Rsum,
        index_offset=1,
        disposable=['time'],
        label='(time,step)->time'
    )

With the full loop, we're ready to simulate our hypergraph. To do so, click :doc:`here </tutorial/simulation>` or use the navigation below.