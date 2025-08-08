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
ConstraintHg is a systems modeling kernel used for parsing constraint hypergraphs. Constraint hypergraphs are a mathematical formalism embodying the constraint-based approach to representing behavior [@willemsBehavioralApproachOpen2007]. Any executable model--whether database schema, plant controller, or ecological forecaster--can be represented as a constraint hypergraph [@morrisUnifiedSystemModeling2025]. Once combined, the unified structure shows how all elements in the system are related to each other. In addition to representing constraint hypergraphs, ConstraintHg provides methods for traversing them, equivalent to simulating the system. While most system simulations are imperatively defined, ConstraintHg enables simulations to be declaratively constructed. The result is the effective glass-boxing of any system, allowing modelers to observe interactions and complex behaviors simply by identifying elements of interest.

# Statement of Need
Every thing in the world is a system and science is the work of characterizing their behavior [@cellierContinuousSystemModeling1991]. The description of a system is given by a model, which tells how different elements in a system interact. Models are ubiquitous: they are used to describe phenomena including weather patterns [@hoffmannDestinationEarthDigital2023], economic policies [@garicanoWhyOrganizationsFail2016], ecological events [@wangHowVastDigital2025] and immunological responses [@sahalPersonalDigitalTwin2022]. To be comprehendable, models must adhere to an established formalism such as a bond graph [@borutzkyBondGraphModelling2011] or stock and flow diagram [@baezCompositionalModelingStock2023]. The limitations of these often incompatible frameworks makes integrating models difficult, leaving scientists, engineers, and decision makers unable to represent the interactions between disparate elements.

## Approaches to Generalized System Modeling
The problem with general systems modeling[^1] is often addressed under the auspices of category theory [@leinsterBasicCategoryTheory2014], which provides the mathematical tools for understanding intersystem relationships[@hedgesCompositionalGameTheory2018]. In this context tools such as [Psymple](https://casasglobal-org.github.io/psymple/latest/) [@simmonsPsymplePythonPackage2025] and [Decapodes](https://algebraicjulia.github.io/Decapodes.jl/dev/) [@morrisDecapodesDiagrammaticTool2024] have been created. Both employ macros to discover mathematical relationships between system entities, allowing for the simulation of dynamic systems.

[^1]: Examples of categorical approaches to general systems modeling include [@mabrokCategoryTheoryFormal2017; @robinsonSheafDualityMethods2017; @zardiniCompositionalSheafTheoreticFramework2021; @amesCategoricalTheoryHybrid2006; @schultzTemporalTypeTheory2017; @baezPhysicsTopologyLogic2010].

Constraint hypergraphs (CHGs), conversely, are a functional representation of a system where integration and other mathematical processes are interpreted as aspects of the modeled system. This allows all systems to be represented according to the formalism rather than imposing a rigid interface that might preclude some modeling types. A CHG is a mathematical structure that represent the state variables of a system as nodes in a graph, and the behaviors of the system as hyperedges mapping between these nodes [@morrisUnifiedSystemModeling2025]. A basic formalization allows them to represent systems universally, reconciling independently defined models into a single, cohesive structure so that system behavior can be made interpreted holistically. They have consequently been posited as a potential foundation for digital twins [@morrisConstraintHypergraphsUnifying2025] and model-based engineering [@morrisDeclarativeIntegrationCAD2025]. 

## System Simulation
A model is only as useful as it is simulatable. Simulation is the use of a model to identify unobserved information. For example, seeing someone walk into a building with a wet umbrella might prompt the estimation that it is raining outside. This is a simulation of a mental model that associates wet umbrellas with precipitation. Simulation can be understood as a function, mapping a set of known inputs (the wetness of the umbrella) to the unobserved output (the current weather). Traditional system simulation is imperative, requiring explicit procedures to be defined for every combination of inputs to outputs. The maximum number of such pairings is given by:

$$\sum_{i=0}^{n-1}(n-i)\binom{n}{i}$$

where $n$ is how many variables are in the system. This number grows exponentially, making it untenable to imperatively define all simulation processes for systems of even a moderate number of states. CHGs address this by representing a system graphically such that only local interactions between variables need to be expressed. This drastically reduces the complexity of the model by avoiding redundant redefinitions across simulations. However, such a representation requires an agent capable of parsing the graph structure and constructing simulations as they are needed--the definition of declarative simulation.

## Software Functionalities
ConstraintHg enables general, declarative multi-physics simulation by employing a breadth-first search (BFS) algorithm that can autonomously construct an optimal simulation process between arbitrarily paired input and output variables. This search algorithm is designed to unravel cycles in the hypergraph, performing parallel searches on cycle branches to ensure an optimal chain is found. Allowing cycles allows modelers to represent real world patterns--repeated behaviors--without needing to explicitly state every occurance of that pattern.

In addition to handling cycles, ConstraintHg allows modelers to declare model validity frames, defining the range of values over which a relationship is valid. This frame is expressed as a boolean function which is conditional to the parser including the edge in a simulation path. This feature allows modelers to specify the conditions in which a model can be relied on, an important aspect of collaborative modeling where users of a model are often unfamiliar with its limitations.

## Examples
General systems simulation has been demonstrated with ConstraintHg in the modeling of a [naval microgird](https://github.com/jmorris335/MicrogridHg) [@morrisMicrogridHg2025], an [elevator lift](https://github.com/jmorris335/ElevatorHypergraph) [@morrisUnifiedSystemModeling2025], and a kinematically-constrained [crankshaft](https://github.com/jmorris335/tool-interoperability-scripts) [@morrisDeclarativeIntegrationCAD2025].

# Acknowledgements
The author acknowledges valuable testing and contributions from Evan Taylor.

# References