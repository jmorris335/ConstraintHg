==================================
Overview of Constraint Hypergraphs
==================================

This is the launchpad for information about constraint hypergraphs (CHGs), 
the mathematical framework undergirding `ConstraintHg <home_>`_.

Good Starting Points
====================

Brief Introduction with examples: :doc:`chg_intro`

`Video <https://www.youtube.com/watch?v=Ph2yhaThex0>`_ overview of using CHGs with digital twins: 

.. raw:: html
    
    <iframe width="560" height="315" src="https://www.youtube.com/embed/Ph2yhaThex0?si=cnhRVxP2oTeQ_4g6" title="CHGs used for Digital Twins" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

More In-Depth
=============

Unified Systems Modeling and Simulation: `DOI <https://doi.org/10.1115/1.4068375>`_
    First published paper covering Contraint Hypergraphs, goes into technical 
    details about how they are defined. A video overview is available `here <https://www.youtube.com/watch?v=nQaxbmd1yds>`_

Integrating Simulation Software with CHGs: `Linked here <https://www.people.clemson.edu/jhmrrs/publications/#:~:text=Declarative%20Integration%20of%20CAD%20Software%20into%20Multi%2DPhysics%20Simulation%20via%20Constraint%20Hypergraphs>`_
    Shows how CHGs enable declarative modeling between simulation software, 
    demonstrating with integration of a dynamic model with Onshape's CAD API. 
    The code for this model is available `here <https://github.com/jmorris335/tool-interoperability-scripts/tree/main>`_

Demonstrations
==============

This is a simple list showing many of the places we've seen CHGs used. If you find more,
reach out to us to include them here! 

Note that many simple examples are available in the 
`demos <https://github.com/jmorris335/ConstraintHg/tree/main/demos>`_ directory of the repository.

`Pendulum <https://github.com/jmorris335/ConstraintHg/blob/main/demos/demo_pendulum.py>`_
    Demonstrates model selection.

`Elevator <https://github.com/jmorris335/ElevatorHypergraph>`_
    Combines discrete-event simulation with a PID controller.

`Naval Microgrid <https://github.com/jmorris335/MicrogridHg>`_
    Complex system featuring data querying and dynamic simulation and linear systems.

`Crankshaft <https://github.com/jmorris335/tool-interoperability-scripts/tree/main>`_
    Integrates CAD software (Onshape) with dynamic simulation.

Questions
=========
Reach out to jhmrrs AT clemson DOT edu for questions or more information.


:doc:`Home </index>` \| :ref:`genindex` \| :ref:`Search <search>`

.. _ConstraintHg Repo: https://github.com/jmorris335/ConstraintHg
.. _home: https://constrainthg.readthedocs.io/en/latest/