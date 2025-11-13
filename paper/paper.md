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

date: 8 August 2025
bibliography: paper.bib
---

# Summary
ConstraintHg is a systems modeling kernel used for parsing constraint hypergraphs. Constraint hypergraphs are a mathematical formalism embodying the constraint-based approach to representing behavior [@willemsBehavioralApproachOpen2007]. Any executable model--whether database schema, plant controller, or ecological forecaster--can be represented as a constraint hypergraph [@morrisUnifiedSystemModeling2025]. Once combined, the unified structure shows how all elements in the system are related to each other. In addition to representing constraint hypergraphs, ConstraintHg provides methods for traversing them, equivalent to simulating the system. While most system simulations must be imperatively defined, ConstraintHg enables simulations to be constructed declaratively. As a result, knowledge about a system can be discovered autonomously, transforming a general system representation into an agentic information provider.

# Statement of Need
Every thing in the world is a system: a collection of distinguishable elements that together espouse some unique behavior [@cellierContinuousSystemModeling1991]. To determine that behavior, scientists describe systems using models, which express how different elements in a system interact. Models are ubiquitous: they are used to describe phenomena including weather patterns [@hoffmannDestinationEarthDigital2023], economic policies [@garicanoWhyOrganizationsFail2016], ecological events [@wangHowVastDigital2025] and immunological responses [@sahalPersonalDigitalTwin2022]. To be comprehendable, models must adhere to an established formalism such as a bond graph [@borutzkyBondGraphModelling2011] or stock and flow diagram [@baezCompositionalModelingStock2023]. The limitations of these often incompatible frameworks makes integrating models difficult, leaving scientists, engineers, and decision makers unable to represent the interactions between disparate elements.

## Approaches to Generalized System Modeling
The problem with general systems modeling is often addressed under the auspices of category theory[^1] [@leinsterBasicCategoryTheory2014], which provides the mathematical tools for understanding intersystem relationships [@hedgesCompositionalGameTheory2018]. In this context, tools such as [Psymple](https://casasglobal-org.github.io/psymple/latest/) [@simmonsPsymplePythonPackage2025], [Decapodes](https://algebraicjulia.github.io/Decapodes.jl/dev/) [@morrisDecapodesDiagrammaticTool2024], and [ModelingToolkit.jl](https://docs.sciml.ai/ModelingToolkit/stable/) [@maModelingToolkitComposableGraph2022] have been created. All of these employ macros to discover mathematical relationships between system entities, allowing for the simulation of dynamic systems.

[^1]: Examples of categorical approaches to general systems modeling include [@mabrokCategoryTheoryFormal2017; @robinsonSheafDualityMethods2017; @zardiniCompositionalSheafTheoreticFramework2021; @amesCategoricalTheoryHybrid2006; @schultzTemporalTypeTheory2017; @baezPhysicsTopologyLogic2010].

Constraint hypergraphs (CHGs), conversely, are a functional representation of a system where integration and other mathematical processes are interpreted as aspects of the modeled system. This allows all systems to be represented according to the formalism rather than imposing a rigid interface that might preclude some modeling types. A CHG is a mathematical structure that represent the state variables of a system as nodes in a graph, and the behaviors of the system as hyperedges mapping between these nodes [@morrisUnifiedSystemModeling2025]. This basic formalization allows them to represent systems universally, reconciling independently defined models into a single, cohesive structure from which system behavior can be interpreted holistically. They have consequently been posited as a potential foundation for digital twins [@morrisConstraintHypergraphsUnifying2025] and model-based engineering [@morrisDeclarativeIntegrationCAD2025].

## System Simulation
A model is only as useful as it is simulatable. Simulation is the use of a model to identify unobserved information. For example, seeing someone walk into a building with a wet umbrella might prompt the estimation that it is raining outside. This is a simulation of a mental model that associates wet umbrellas with precipitation. Simulation can be understood as a function, mapping a set of known inputs (the wetness of the umbrella) to the unobserved output (the current weather). Traditional system simulation is imperative, where the modeler specifies how the simulation should be conducted. Imperative simulations are difficult to adapt; for instance, a modeler might define simluations mapping umbrella wetness to precipitation, cloud cover, transit delay, temperature, etc. Describing these simulations imperatively requires a unique transformation sequence to be explicitly defined, regardless of the cross-over between the procedures. For a system with $n$ variables, the maximum number of simulation functions that could be defined is given by 

$$n \left( 2^{n-1}-1 \right)$$

This number grows exponentially, making it untenable to imperatively define all simulation processes for systems of even a moderate number of states. CHGs address this by representing a system graphically such that only local interactions between variables need to be expressed. This drastically reduces the complexity of the model by avoiding redundant redefinitions across simulations. Agents that can reason on the graph structure are able to construct these local relationships into global simulations--the definition of declarative simulation.

While many packages are provided for representing hypergraphs, such as XGI [@landryXGIPythonPackage2023] or HyperNetX [@praggastisHyperNetXPythonPackage2024], ConstraintHg is the first agent used for traversing and declaratively simulating CHGs. It does this by employing a breadth-first search (BFS) algorithm that can autonomously construct an optimal simulation process between arbitrarily paired input and output variables. In addition to finding simple paths, the search algorithm is able to unravel cycles in the hypergraph by performing parallel searches on cycle branches to ensure an optimal chain is found. This allows ConstraintHg to simlulate dynamic systems, where the states of a system go through some type of repeated change.

In addition to dealing with dynamic systems, ConstraintHg also provides mechanisms for dealing with partial models, such as when a modeler can provide relations for only a subset of a state's values. For example, while an umbrella being wet might imply that it is raining, but if the umbrella is not wet, no prediction can be made as to current weather. These partial relations become model validity frames which, while essential to systems modeling, can be difficult to capture in a modeling framework [@malakCharacterizingAssessingValidity2004]. ConstraintHg captures a validity frame as a boolean function which is conditional to the parser including the edge in a simulation path. This feature allows modelers to specify the conditions in which a model can be relied on, an important aspect of collaborative modeling where users of a model are often unfamiliar with its limitations.

# Related Research
ConstraintHg is actively being employed in work deriving the mathematical foundations of digital twins [@morrisConstraintHypergraphsUnifying2025], as well as establishing executable digital threads for model-based enterprises [@morrisDeclarativeIntegrationCAD2025]. It has been employed to modeling a [naval microgird](https://github.com/jmorris335/MicrogridHg) [@morrisMicrogridHg2025], an [elevator lift](https://github.com/jmorris335/ElevatorHypergraph) [@morrisUnifiedSystemModeling2025], a kinematically-constrained [crankshaft](https://github.com/jmorris335/tool-interoperability-scripts) [@morrisDeclarativeIntegrationCAD2025], and an [additive manufaacturing machine](https://github.com/jmorris335/Powder-Based-Fusion-Digital-Twin).

# Acknowledgements
The author acknowledges valuable testing and contributions from Evan Taylor.

# References