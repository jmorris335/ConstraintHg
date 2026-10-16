Advanced Features
=================

Beyond basic modeling and simulation, ConstraintHg provides a few advanced features that are not necessary, but may be helpful in certain cases.

Dynamic Edge Weights
--------------------
The typical way to set the weight (or cost) of an edge is to pass a number to the ``weight`` argument when creating the edge. This creates a static weight for the edge that does not change during the simulation. However, in some cases you may want to have the weight update based on the values encountered during the simulation. These weights are dynamic.

To create a dynamic weight, you pass a callable method (function) to the ``weight`` parameter rather than a number; i.e.

.. code-block:: python

    def weight_method(s1, s2):
        return s1 * s2

    hg.add_edge(
        sources={'s1': X, 's2': Y},
        target=z,
        rel=lambda s1, s2: s1 + s2,
        weight=weight_method
    )

This adds a relation that can be used to calculate the weight of the edge at runtime, allowing the system behavior to influence how the models are compared and incorporated into the found paths.

The format for the method is similar to that of the ``rel`` and ``via`` methods, in that the arguments to the method are the source nodes of the edge.

.. important:: The output of the weight method should be a positive number. ConstraintHg will automatically cast this as a float. Negative numbers and non-numeric values will raise an error during the simulation.

Whether the weight is passed as a static number or a dynamic method, the weight of the edge can be accessed at any time by calling the ``weight`` property of the edge object. Note that if the weight is dynamic, the value will only be calculated during a simulation. Therefore, accessing a dynamic weight outside of a simulation will return the default value of 1.0. 1.0 is considered the default weight for all edges if otherwise unset, which is a good way to consider a dynamically calculated weight outside a simulation. Since the weight is only valid during the simulation, at all other times it is unset, consequently the software sets it to be 1.0.

Static JSON Exports
-------------------

Constraint hypergraphs represented in ConstraintHg can be exported to JSON files for use in other applications. This is especially useful for visually representing a hypergraph in VisualCHG. To do so, call the ``to_json`` method of the hypergraph object. This returns a string containing the JSON data, which can be saved to an separate file. For example:

.. code-block:: python
    
    with open("path/to/hypergraph/file.chg", "w") as f:
        f.write(hg.to_json())

The .chg filetype is a custom file extension for ConstraintHg hypergraph files. It is simply a JSON file, but the .chg extension helps to identify it as containing a constraint hypergraph.

.. note:: You can also call the ``to_json()`` method on :ref:`Nodes <node>` and :ref:`Edges <edge>` to get a JSON representation of those objects.

Similarly, you can initalize a hypergraph from a JSON file by calling the ``from_json`` method of the hypergraph object. This takes in a string of JSON data and returns a new hypergraph object.

There are some limitations of this method. The JSON export has to capture the methods for each edge (``rel``, ``via``, etc.). These methods have to be saved as strings of Python code which can be reloaded later. This is not a safe method, as it allows for arbitrary code execution when importing the JSON-formatted hypergraph. Therefore, the ``from_json`` method is only available when the hypergraph is in ``unsafe_mode``. This is a mode that allows for arbitrary code execution, and should be used with caution. It is recommended to only use this mode when importing JSON files that you have created yourself, or that come from a source you trust. To import from a .chg (JSON) file, you can do the following:

.. code-block:: python

    with open("path/to/hypergraph/file.chg", "r") as f:
        json_data = f.read()
    hg2 = Hypergraph(unsafe_mode=True)
    hg2.from_json(json_data)

.. note:: The ``to_json`` method builds a dictionary representation of the nodes, edges, and hypergraph. You can access this Python-specific static representation by calling the ``to_dict()`` method of the hypergraph object.

Another limitation is that the methods for the edges must be defined in the global scope of the script. This is because the methods are saved as strings of Python code, and when they are reloaded, they are executed in the global scope. Therefore, if you define a method inside another method or class, it will not be accessible when reloading the hypergraph from JSON.