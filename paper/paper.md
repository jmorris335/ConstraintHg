---
title: 'ConstraintHg: A Kernel for Systems Modeling and Simulation'
tags:
  - simulation
  - modeling
  - systems
  - Python
  - constraint hypergraphs

authors:
  - name: John Morris
    corresponding: true
    orcid: 0009-0005-6571-1959
    affiliation: 1

affiliations:
  - index: 1
    name: Deptartment of Mechanical Engineering, Clemson University, Clemson, South Carolina, United States

date: 13 November 2025
bibliography: paper.bib
---

# Summary
ConstraintHg is a systems modeling kernel used for parsing constraint hypergraphs. Constraint hypergraphs are a mathematical formalism embodying the constraint-based approach to representing behavior [@willemsBehavioralApproachOpen2007]. Any executable model, whether database schema, plant controller, or ecological forecaster, can be represented as a constraint hypergraph [@morrisUnifiedSystemModeling2025]. Once combined, the unified structure shows how all elements in the system are related to each other. In addition to representing constraint hypergraphs, ConstraintHg provides methods for traversing them, equivalent to simulating the system. While most system simulations must be imperatively defined, ConstraintHg enables simulations to be constructed declaratively. As a result, knowledge about a system can be discovered autonomously, transforming a general system representation into an agentic information provider.

# Statement of Need
Every thing in the world is a system: a collection of distinguishable elements that together espouse some unique behavior [@cellierContinuousSystemModeling1991]. To determine that behavior, scientists describe systems using models, which express how different elements in a system interact. Models are ubiquitous: they are used to describe phenomena including weather patterns [@hoffmannDestinationEarthDigital2023], economic policies [@garicanoWhyOrganizationsFail2016], ecological events [@wangHowVastDigital2025] and immunological responses [@sahalPersonalDigitalTwin2022]. For the behavior of a system to be understandable, models must adhere to an established framework such as a bond graph [@borutzkyBondGraphModelling2011] or stock and flow diagram [@baezCompositionalModelingStock2023]. Information in such frameworks can be difficult to connect, such as comparing energy in a bond graph to population dynamics in a stock and flow diagram. These domain-specificities makes integrating models difficult, leaving scientists, engineers, and decision-makers often unable to discern the complex, multi-physics interactions.

## Approaches to Generalized System Modeling
The problem with general systems modeling is often addressed under the auspices of category theory[^1] [@leinsterBasicCategoryTheory2014], which provides the mathematical tools for understanding intersystem relationships [@hedgesCompositionalGameTheory2018]. In this context, tools such as [Psymple](https://casasglobal-org.github.io/psymple/latest/) [@simmonsPsymplePythonPackage2025], [Decapodes](https://algebraicjulia.github.io/Decapodes.jl/dev/) [@morrisDecapodesDiagrammaticTool2024], [ModelingToolkit.jl](https://docs.sciml.ai/ModelingToolkit/stable/) [@maModelingToolkitComposableGraph2022], and [Modelica](https://modelica.org) [@mattssonModelicaInternationalEffort1997] have been created. All of these employ macros to discover mathematical relationships between system entities, allowing for the simulation of dynamic systems.

[^1]: Examples of categorical approaches to general systems modeling include [@mabrokCategoryTheoryFormal2017; @robinsonSheafDualityMethods2017; @zardiniCompositionalSheafTheoreticFramework2021; @amesCategoricalTheoryHybrid2006; @schultzTemporalTypeTheory2017; @baezPhysicsTopologyLogic2010].

Constraint hypergraphs (CHGs), conversely, are a functional representation of a system where the system solution is composed from elements in the model rather than applied by external solvers. This allows systems to be represented without requiring a proscriptive interface. A CHG is a mathematical structure that represent the state variables of a system as nodes in a graph and the behaviors of the system as directed hyperedges mapping between these nodes [@morrisUnifiedSystemModeling2025]. Eeach hyperedge representing a function constraining the value of the target node. The generality of this formalism is able to flexibly capture the intracacies of any system. Consequently, independent models defined across domains, scales, or even different software platforms can all be reconciled into a cohesive structure from which behavior can be interpreted holistically.

## System Simulation
A model is only as useful as it is simulatable. Simulation is the use of a model to identify unobserved information. For example, a person observing someone walk into a building with a wet umbrella might infer that it is raining outside. This inference is the simulation of a mental model associating wet umbrellas with precipitation. Simulation can be understood as a function, mapping a set of known inputs (the wetness of the umbrella) to the unobserved output (the current weather). Traditional system simulation is imperative, where the modeler specifies how the explicit processes by which the transformation should be conducted. Imperative simulations are difficult to adapt; for instance, a model might define relationships mapping wetness to precipitation, cloud cover, transit delay, temperature, etc. Describing these imperatively requires a unique sequence to be explicitly defined for each pairing of inputs to outputs. For a system with $n$ variables, the maximum limit of simulation functions that could be defined is $n \left( 2^{n-1}-1 \right)$. This exponential cap makes it untenable to fully describe all imperative simulations for models with even a moderate number of states. CHGs address this by representing a system graphically such that global simulations can be created by combining local interactions. This drastically reduces the complexity of the model by avoiding redundant redefinitions.

While many packages are provided for representing hypergraphs, such as XGI [@landryXGIPythonPackage2023] or HyperNetX [@praggastisHyperNetXPythonPackage2024], ConstraintHg is the first library for performing declarative simulation using a CHG. It does this by employing a breadth-first search (BFS) algorithm that can autonomously construct an optimal simulation process between arbitrarily paired input and output variables. In addition to finding simple paths, the search algorithm is able to unravel cycles in the hypergraph by performing parallel searches on cycle branches to ensure an optimal chain is found. This allows ConstraintHg to simlulate dynamic systems, where the states of a system go through some type of repeated change.

In addition to dealing with dynamic systems, ConstraintHg also provides mechanisms for dealing with partial models, such as when a modeler can provide relations for only a subset of a state's values. For example, while an umbrella being wet might imply that it is raining, if the umbrella is not wet, no prediction can be made as to current weather. These partial relations become model validity frames which, while essential to systems modeling, can be difficult to capture in a modeling framework [@malakCharacterizingAssessingValidity2004]. ConstraintHg captures a validity frame as a boolean function which is conditional to the parser including the edge in a simulation path. This feature allows modelers to specify the conditions in which a model can be relied on, an important aspect of collaborative modeling where users of a model are often unfamiliar with its limitations.

# Related Research
ConstraintHg is actively being employed in work deriving the mathematical foundations of digital twins [@morrisConstraintHypergraphsUnifying2025], as well as establishing executable digital threads for model-based enterprises [@morrisDeclarativeIntegrationCAD2025]. It has been employed to modeling a [naval microgird](https://github.com/jmorris335/MicrogridHg) [@morrisMicrogridHg2025], an [elevator lift](https://github.com/jmorris335/ElevatorHypergraph) [@morrisUnifiedSystemModeling2025], a kinematically-constrained [crankshaft](https://github.com/jmorris335/tool-interoperability-scripts) [@morrisDeclarativeIntegrationCAD2025], and an [additive manufacturing machine](https://github.com/jmorris335/Powder-Based-Fusion-Digital-Twin).

# Acknowledgements
The author acknowledges valuable testing and contributions from Evan Taylor.

# References
