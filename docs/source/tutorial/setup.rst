Initial Setup
=============

Package Structure
-----------------

ConstraintHg has four major components:
    - Structures for forming the major elements of constraint hypergraph (:ref:`nodes <node_class>`, :ref:`edges <edge_class>`, as well as the full :ref:`hypergraph <hypergraph_class>` itself).
    - Structures for representing simulation paths, given as a :ref:`search tree <tnode_class>`.
    - Pathfinding :ref:`algorithms <pathfinder_class>` for constructing a simulation.
    - Several predefined :doc:`methods </api/relations>` to help developers when constructing relationships.

Installation
------------

.. note::
    ConstraintHg is a Python package. The recommended way to use Python packages is to setup a `virtual environment <https://docs.python.org/3/library/venv.html>`_ by calling ``python -m venv .venv`` from your terminal.

The best way to install the package is to use `pip <https://pip.pypa.io/en/stable/getting-started/>`_. Start by opening up a terminal and activating your virtual environment. Then, enter the following command:

.. code-block::

    pip install constrainthg

This will install the ConstraintHg source code from the `Python Package Index <https://pypi.org/project/constrainthg/>`_ (PyPI) to your working directory. It will also import the `numpy <https://numpy.org>`_ package. 

Calling the Package
-------------------

After installing ConstraintHg, you can call it from a Python script. Open a new file in your directory and give it a name. We'll call ours ``demo_pendulum.py``.

Inside the blank file, import the ConstraintHg package. You typically don't need to import the whole thing, just the classes for the Hypergraph and Node, as well as the relations class. To do this, add the following lines to your file:

.. code-block:: python

    from constrainthg.hypergraph import Hypergraph, Node
    import constrainthg.relations as R

You're now ready to move onto creating your model. Click :doc:`here </tutorial/modeling>` to go to the next step, or use the navigation links below.






