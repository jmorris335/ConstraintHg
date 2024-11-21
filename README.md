![Static Badge](https://img.shields.io/badge/homepage-blue?link=https%3A%2F%2Fgithub.com%2Fjmorris335%2FConstraintHg%2Fwiki)
 ![Read the Docs](https://img.shields.io/readthedocs/constrainthg?link=https%3A%2F%2Fconstrainthg.readthedocs.io%2Fen%2Flatest%2Findex.html) ![Static Badge](https://img.shields.io/badge/tests-14/15-red) ![GitHub Release](https://img.shields.io/github/v/release/jmorris335/ConstraintHg?include_prereleases&display_name=tag) ![GitHub last commit](https://img.shields.io/github/last-commit/jmorris335/ConstraintHg)

# ConstraintHg
This repository enables usage of hypergraphs to define and execute system models. **It is not a rigorous data storage solution. Do not use this as a database.** Note that this repo is under active development (no official release yet), therefore changes may occur without warning. No functionality is guaranteed. 

**For an detailed overview of the package and introduction to constraint hypergraph theory, see the [wiki](https://github.com/jmorris335/ConstraintHg/wiki).** The latest API documentation is available on [Read the Docs](https://constrainthg.readthedocs.io/en/latest/).

## Install
ConstraintHg is listed on the Python Package Index. Just use `pip install constrainthg` to get started.

# Introduction
Hypergraphs are normal graphs but without the constraint that edges must only link between two nodes. Because of this expanded generality, hypergraphs can be used to model more complex relationships. For instance, the relationship `A + B = C` is a multinodal relationship between three nodes, A, B, and C. You can think of all three nodes being linked by a 2D hyperedge, so that to move along that hyperedge you need at least two of three nodes. 

An constraint hypergraph is a hypergraph where the relationships are constraints that can be solved for by some execution engine, generally via API calls. These constraints reveal the behavior of the system. The goal is for the hypergraph to be platform agnostic, while API calls allow for edges to be processed on any available software.

Processing a series of nodes and edges (a "route") is what constitutes a simulation, so one of the uses of an constraint hypergraph is enabling high-level simulation ability from any possible entry point in a system model.

## Getting started
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

Check out the  [demos](https://github.com/jmorris335/ConstraintHg/tree/main/demos) directory for more examples.

## Licensing and Usage
Author: [John Morris](https://www.people.clemson.edu/jhmrrs/)  
Organization: [PLM Center](https://github.com/Clemson-PLMC) at Clemson University  
Contact: Reach out to my GitHub profile ([jmorris335](https://github.com/jmorris335))  
Usage: An official release will *likely* be provided under the CC BY-NC-SA 4.0 license, but for now **all rights are reserved**. For usage, please reach out to the author directly.
