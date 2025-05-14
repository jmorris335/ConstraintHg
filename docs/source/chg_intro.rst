======================================
Introduction to Constraint Hypergraphs
======================================

.. contents::
   :local:
   :depth: 2
   :caption: Contents:

A constraint hypergraph is a modeling framework for capturing and synthesizing information at a fundamental level. They can be used to describe different domains such as workplace personnel, project structures, aircraft carriers, and ecological systems. Their primary use is to represent a real system by a sequence of executable actions which can be read by a computer, allowing the computer to reason and predict about information anywhere in the system. In short, if something can be known, then it can be captured in a constraint hypergraph; if something is represented in a constraint hypergraph, then it can be understood by a computer.

What are they made of
========================

Constraint hypergraphs are composed of nodes and edges. Each node represents a set of values—a variable in other words. Each edge represents a constraint placed between variables, along the lines of "if :math:`X` is this value, then :math:`Y` will be this value." Mathematically, these are functions mapping each value of :math:`X` to a value in :math:`Y`. 

Constraint hypergraphs are *hyper*-graphs, meaning that these relationships can involve multiple variables. The framework allows that edges may have many variables in their source set (or domain), which together constrain a single variable as a target (or codomain). For instance, given three variables :math:`A`, :math:`B`, and :math:`C`, we could define an edge stipulating that :math:`A + B = C`. This edge declares that every value in :math:`C` is constrained to be the sum of the values of :math:`A` and :math:`B`. This is a hyperedge with :math:`\lbrace A, B \rbrace` as its source set and :math:`C` as its target.

First example
================

It helps to have a basic example to demonstrate the functionality of a constraint hypergraph. Let's consider a pendulum with a mass :math:`m`, a radius :math:`r`, and an angular position of :math:`\theta`, as shown in  :ref:`Figure 1 <pend_fbd>`.

.. figure:: https://github.com/user-attachments/assets/c5a77507-bdca-432a-8d3d-b881bec5f26e
    :alt: Pendulum free body diagram
    :width: 200px
    :align: center
    :name: pend_fbd

    Pendulum free body diagram

The angular acceleration (:math:`\alpha`) of the pendulum is given as :math:`\alpha = -\frac{g}{m}\sin\theta`. This is a relationship, or in other words a constraint–the values of :math:`\alpha` are determined by the combined values of :math:`g`, :math:`m`, and :math:`\theta`. We could put these all into a single edge, though it's better practice to break them up into many edges where each edge represents a single operation. This results with more edges, but this allows us to make connections with intermediate variables that we might otherwise hide. The hypergraph is shown in :ref:`Figure 2 <pend_simple>`, with these intermediate nodes in grey. A constraint hypergraph represents all the knowledge known about a system. In this case, the only thing we know about our pendulum is the original equation, though as seen in :ref:`Figure 2 <pend_simple>` we've broken that algebraic expression into 4 different relationships. 

.. figure:: https://github.com/user-attachments/assets/86367294-e0cf-4de3-bfa2-6952529ae693
    :alt: Constraint hypergraph for a simple pendulum
    :height: 250px
    :align: center
    :name: pend_simple

    Constraint hypergraph for a simple pendulum

However, we can describe more relationships in the system. For instance, if we know the damping coefficient :math:`c` and the angular velocity :math:`\omega` for the pendulum, then we can expand the initial equation to say that :math:`\alpha = -\frac{g}{m}\sin\theta - c\omega`. But before we add this new relationship to the graph, we should note that many of the variables used in the second equation are already in the graph (as shown in :ref:`Figure 2 <pend_simple>`). The solution is to add new edges to the preexisting variables, so that we don't have duplicate nodes in the final hypergraph. The expanded hypergraph is shown in :ref:`Figure 3 <pend_damping>`.

.. figure:: https://github.com/user-attachments/assets/07e06962-9e8e-41b4-bda0-a5705f8a58d6
    :alt: Expanded constraint hypergraph for a pendulum with damping
    :height: 250px
    :align: center
    :name: pend_damping

    Expanded constraint hypergraph for a pendulum with damping

Take note that the :math:`\alpha` node in :ref:`Figure 3 <pend_damping>` has two edges leading to it, showing that there are two possible ways to constrain its values. This is a quirk of constraint hypergraphs that permits competing constraints–a normal constraint network would not allow a variable to be related by two different, overlapping constraints. But in this case by allowing the dual relationships we have indicated that there are at least two possible models that can be used to solve for :math:`\alpha` (in this case one with and one without damping). During simulation, if we have a damping coefficient, the solver has to select which model will be active at any given time. 

The takeaway is that the constraint hypergraph shows not just a single way to simulate the system, it shows *every* way to simulate the system—every possible model we can construct [#]_. We could add more edges and nodes to the graph if we knew relationships between :math:`\alpha` and :math:`\omega`, or :math:`\omega` and :math:`\theta`, or any other variable we want to virtually observe. The constraint hypergraph captures them all and provides the solver the ability to distinguish between them, chain edges together (path finding), and select preferred models. For a full implementation see the `Pendulum demo <https://github.com/jmorris335/ConstraintHg/blob/main/demos/demo_pendulum.py>` in the package.

What are they used for
======================
A constraint hypergraph is a base-level representation of information, fully able to capture the way we understand the real world in a way that enables computer simulation. Here are some examples of what they can be used for:

System unification
------------------
Models are often composed in formats that don't talk to each other, but a constraint hypergraph is fundamental enough to capture the complexities of any system model in a single framework. This allows for a single, universal model to be created for a system that contains information about every sub-domain, unifying multi-domain projects. For instance, when developing a product models might be made for the geometry, materials, requirements, assembly instructions, supply chain, economic forecasts, cost estimates, project status, involved personnel, revisions, and more. Each of these models can be unified into a single constraint hypergraph, allowing a systems engineer to understand how (for example) changing the power requirements might impact shipping time.

Simulation
----------
A simulation is the artificial generation of data. A simulation requires inputs and outputs, which are connected to each other via the relationships of the model. The underlying idea is: "given I know :math:`a`, :math:`b`, and :math:`c`, what do I know about :math:`x`, :math:`y`, and :math:`z`?" Simulation is not just an engineering term, we use it everyday to understand reality. When the weather reporter says it's *5 degrees* outside, we infer that the feeling of the outside air is *cold*. This wasn't said to us, but was rather simulated along our mental model of temperature. Similarly when your boss says they want a report due *ASAP*, we simulate that the priority of the report is *important*. This value was not explicitly stated, but rather implied by our model.

Simulation in a constraint hypergraph is automatic and powerful. Because of how the edges are constructed, simulation is enabled at every level of the system. Choosing values for nodes in the hypergraph allows a solver to imply the other variables in the system (if there are relationships that constrain them). You can also call this a reasoner, that given knowledge about a system, a constraint hypergraph enables an agent to reason over the system and come to new conclusions based on the existing models.

Digital twins
-------------
A digital twin is a set of models being fed data from a real world system. In practice, digital twins are typically scattered throughout a digital ecosystem, with data and models stored in many different places. These are tied together into a volatile system managed by the digital thread. Constraint hypergraphs simplify this setup by bringing each variable and each model together into a single place. Constraint hypergraphs can then provide information about the real system from their ability to simulate across the model/data combination.

Model selection
---------------
A hypergraph represents all possible models of a system. By providing a cost associated with calculating each graph edge, a solver can choose a preferred model to use in a specific circumstance, such as one that minimizes uncertainty, disruption, computation time, or achieves a certain output. This can even happen mid-simulation, such as jumping between a linear and non-linear model as variables change throughout a simulation run.

Applications
============
To provide context for constraint hypergraphs, here are a few practical cases where hypergraphs can be of use:

Inter-team organization
-----------------------
If a company has many teams working in parallel on a project, it can be difficult to share knowledge gained about the system as a whole. But any team member who learns something about the project can add it to a project-wide constraint hypergraph. Although the person might not understand the whole system, each individual contribution is still curated by the constraint hypergraph, growing the body of knowledge for the entire company. In this case, structure of the hypergraph (mostly) keeps edges from causing inconsistencies, providing a quick, painless, and powerful way to preserve and combine individual contributions.

Change disruption propagation
-----------------------------
It can be difficult to tell what impact changing a product, specification, or organization might have. Constraint hypergraphs keep track of large, complex systems without losing the ability to reason across the system as a whole. A product manager could simulate making multiple changes by tweaking values in the constraint hypergraph and observing the response across many different domains, quickly estimating cost, time, and safety risks.

_____

Footnotes
=========
.. [#] The definition of a model employed here is of a set of relationships between a set of variables. That means that every algebraic equation you have used is a model and every system of equations. CAD models fit this context as well, as they constrain the positions of geometric features relative to each other. This definition also covers flow charts, Markov processes, block diagrams, Petri nets, and really most modeling frameworks! We call the combination of known relationships and variables the *model space*.

:doc:`Home </index>`
:ref:`genindex`
:ref:`modindex`
:ref:`search`