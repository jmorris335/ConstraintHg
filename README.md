<h1 align="center">
<img src="https://github.com/jmorris335/ConstraintHg/blob/14d9ea2db0e73d440dd4de1491ba0ffee0233d87/media/logo.svg?raw=true" width="300">
</h1><br>

[![DOI](https://zenodo.org/badge/869248124.svg)](https://doi.org/10.5281/zenodo.15278018) [![Read the Docs](https://img.shields.io/readthedocs/constrainthg?link=https%3A%2F%2Fconstrainthg.readthedocs.io%2Fen%2Flatest%2Findex.html)](https://constrainthg.readthedocs.io/en/latest/) ![Static Badge](https://img.shields.io/badge/tests-26/26-brightgreen) ![GitHub Release](https://img.shields.io/github/v/release/jmorris335/ConstraintHg?include_prereleases&display_name=tag) ![GitHub last commit](https://img.shields.io/github/last-commit/jmorris335/ConstraintHg)


ConstraintHg is a systems modeling kernel written in Python that enables general definition and universal simulation of any system. The kernel breaks a system down into the informational values (nodes) and functional relationships (hyperedges), providing robust simulation through pathfinding operations. This repository is under active development (no official release yet), and is therefore subject to change without warning. **It is not a rigorous data storage solution. Do not use this as a database.**

## Uses
ConstraintHg enables the following functionalities:
- **Universal systems modeling:** any model can be represented as a Constraint Hypergraph, meaning that models of different types and sources can be combined inside a single hypergraph.
- **Universal simulation:** any simulation that could be conducted on a systems model can be discovered by ConstraintHg, or in other words, a program for calculating any piece of information (given a set of inputs) can be compiled for any system--given that such a program exists!
- **System interrogation:** any system can be turned into a black box where information is autonomously returned by ConstraintHg--whether that information was recorded or simulated. This is especially useful for automatons trying to interface with a system.
- **Digital twin representation:** modeling a real systsem with ConstraintHg is equivalent to creating a digital twin of that system, providing universal observation of the properties and biconnectiviy with the modeled system.

## Links and More Information
- Homepage: [Link](https://constrainthg.readthedocs.io/en/latest/index.html)
- Learn to use: [Get Started](https://constrainthg.readthedocs.io/en/latest/constrainthg_intro.html)
- Learn about Constraint Hypergraphs: [Resources](https://constrainthg.readthedocs.io/en/latest/chg_overview.html)
- API Documentation: [Read the Docs](https://constrainthg.readthedocs.io/en/latest/constrainthg.html)
- Video overview: [YouTube](https://www.youtube.com/watch?v=Ph2yhaThex0)
- Papers:
  - [Introduction of Constraint Hypergraphs](https://doi.org/10.1115/1.4068375)

### Licensing and Usage
Author: [John Morris](https://www.people.clemson.edu/jhmrrs/)  
Contact: Reach out to my GitHub profile ([jmorris335](https://github.com/jmorris335))  
Usage: Released under the Apache 2.0 license. This permissive license allows you can use, modify, and distribute this source code as desired (official terms are in the LICENSE file). The main limitations are that you'll need to include a copy of this license as well as the NOTICE file, and you'll have to state your changes. **We'd appreciate hearing if you used this for something helpful. Let us know by contacting us via our [profiles](https://github.com/jmorris335)!**

### Install
ConstraintHg is listed on the Python Package Index. To install, paste the following to your command terminal: 
```
   pip install constrainthg
```

## Introduction
Hypergraphs are normal graphs but without the constraint that edges must only link between two nodes. Because of this expanded generality, hypergraphs can be used to model more complex relationships. For instance, the relationship `A + B = C` is a multinodal relationship between three nodes, A, B, and C. You can think of all three nodes being linked by a 2D hyperedge, so that to move along that hyperedge you need at least two of three nodes. 

A constraint hypergraph is a hypergraph where the relationships are constraints that can be solved for by some execution engine, generally via API calls. These constraints reveal the behavior of the system. The goal is for the hypergraph to be platform agnostic, while API calls allow for edges to be processed on any available software.

Processing a series of nodes and edges (a "route") is what constitutes a simulation, so one of the uses of an constraint hypergraph is enabling high-level simulation ability from any possible entry point in a system model.

### Getting started
*Note that this demo is found in [`demos/demo_basic.py`](https://github.com/jmorris335/ConstraintHg/blob/main/demos/demo_basic.py)*
Let's build a basic constraint hypergraph of the following equations:
- $A + B = C$
- $A = -D$
- $B = -E$
- $D + E = F$  
- $F = -C$

First, import the classes. 
```[python]
from constrainthg.hypergraph import Hypergraph
import constrainthg.relations as R
```

A hypergraph consists of edges that map between a set of nodes to a single node. We provide the mapping by defining a constraint function (many of which are already defined in the `relationships` module). The two relationships defined in the governing equations are addition and negation. Using the typical syntax, we refer to the functions defined in `relationships` with `R.<name>`, in this case `R.Rsum` and `R.Rnegate`. To make the hypergraph we'll need to compose the 5 edges (equations) given above. 
```[python]
hg = Hypergraph()
hg.add_edge(['A', 'B'], 'C', R.Rsum)
hg.add_edge('A', 'D', R.Rnegate)
hg.add_edge('B', 'E', R.Rnegate)
hg.add_edge(['D', 'E'], 'F', R.Rsum)
hg.add_edge('F', 'C', R.Rnegate)
```

We can verify that the hypergraph was made correctly by tracing all possible paths for generating C using the `printPaths` function.
```[python]
print(hg.print_paths('C'))
```

This should give us the following output. Hyperedges are indicated with a `◯`, with the last source separated from other edges with a `●`.
```
└──C, cost=1
   ├◯─A, cost=0
   ├●─B, cost=0
   └──F, cost=3
      ├◯─D, cost=1
      │  └──A, cost=0
      └●─E, cost=1
         └──B, cost=0
```

Compute the value of $C$ by picking a set of source nodes (inputs), such as $A$ and $B$ or $A$ and $E$. Set values for the inputs and the solver will automatically calulate an optimized route to simulate $C$. 
```[python]
print("**Inputs A and E**")
hg.solve('C', {'A':3, 'E':-7}, to_print=True)
print("**Inputs A and B**")
hg.solve('C', {'A':3, 'B':7}, to_print=True)
```

The output of the above should be:
```
**Inputs A and E**
└──C= 10, cost=3
   └──F= -10, cost=2
      ├──D= -3, cost=1
      │  └──A= 3, cost=0
      └──E= -7, cost=0

**Inputs A and B**
└──C= 10, cost=1
   ├──A= 3, cost=0
   └──B= 7, cost=0
```

### Examples
Many examples are available in the [demos](https://github.com/jmorris335/ConstraintHg/tree/main/demos) directory. These, and other external examples include:
- [Pendulum](https://github.com/jmorris335/ConstraintHg/blob/main/demos/demo_pendulum.py): demonstrating model selection
- [Elevator](https://github.com/jmorris335/ElevatorHypergraph): combining discrete-event simulation with a PID controller
- [Naval Microgrid](https://github.com/jmorris335/MicrogridHg): complex system featuring data querying and dynamic simulation and linear systems
- [Crankshaft](https://github.com/jmorris335/tool-interoperability-scripts/tree/main): integrates CAD software (Onshape) with dynamic simulation
