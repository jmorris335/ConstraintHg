"""
File: hypergraph.py
Author: John Morris, jhmrrs@clemson.edu, https://orcid.org/0009-0005-6571-1959
Purpose: A list of classes for storing and traversing a constraint hypergraph.
License: All rights reserved.
Versions:
- 0.0, 7 Oct. 2024: initialized
- 0.1, 4 Nov. 2024: basic searching demonstrated
"""

from typing import Callable, List
from inspect import signature
import logging
logger = logging.getLogger(__name__)
import itertools
from enum import Enum

## Helper functions
def appendToDictList(d: dict, key, val):
    """Appends the value to a dictionary where the dict.values are lists."""
    if key not in d:
        d[key] = list()
    d[key].append(val)

def makeList(val)-> list:
    """Ensures that the value is a list, or else a list containing the value."""
    if isinstance(val, list):
        return val
    elif isinstance(val, str):
        return [val]
    try: 
        return list(val)
    except TypeError:
        return [val]
    
def makeSet(val)-> list:
    """Ensures that the value is a set, or else a set containing the value."""
    if isinstance(val, set):
        return val
    elif isinstance(val, str):
        return {val}
    try: 
        return set(val)
    except TypeError:
        return {val}
    
class tNode:
    """A basic tree node for printing tree structures."""
    class conn:
        """A class of connectors used for indicating child nodes."""
        elbow = "└──"
        pipe = "│  "
        tee = "├──"
        blank = "   "
        elbow_join = "└◯─"
        tee_join = "├◯─"
        elbow_stop = "└●─"
        tee_stop = "├●─"
    
    def __init__(self, label, value=None, children: list=None, cost: float=None, 
                 indices: dict=None, trace: list=None, 
                 gen_edge_label: str=None, gen_edge_cost: float=0.0, 
                 index_offset: int=1.0, join_status: str='None' ):
        """
        Creates a node in a search tree.

        Parameters
        ----------
        label : str
            A string identifying the node represented by the tNode.
        value : Any, optional
            The value of the tree solved to the tNode.
        children : list, optional
            tNodes that form the source nodes of an edge leading to the tNode.
        cost : float, optional
            Value indicating the solving the tree rooted at the tNode.
        indices: dict, optional
            Counts of how many times each node was uniquely solved for in the 
            path (label : int).
        trace : list, optional
            Top down trace of how the tNode could be resolved, used for path exploration.
        gen_edge_label : str, optional
            A unique label for the edge generating the tNode (of which `children` are source nodes).
        gen_edge_cost : float, default=0.
            Value for weight (cost) of the generating edge, default is 0.0.
        index_offset : int, default=0
            Offset for calculating the index (allowing for iterative presetting).
        join_status : str, optional
            Indicates if the tNode is the last of a set of children, used for printing.
        """
        self.label = label
        self.value = value
        self.children = list() if children is None else children
        self.cost = cost
        self.trace = list() if trace is None else trace
        self.indices = {label : 1} if indices is None else indices
        self.gen_edge_label = gen_edge_label
        self.gen_edge_cost = gen_edge_cost
        self.values = {label : [value,]}
        self.join_status = join_status
        self.index_offset = index_offset
 
    def printConn(self, last=True)-> str:
        """Selecter function for the connector string on the tree print."""
        if last:
            if self.join_status == 'join':
                return self.conn.elbow_join
            elif self.join_status == 'join_stop':
                return self.conn.elbow_stop
            else:
                return self.conn.elbow
        if self.join_status == 'join':
            return self.conn.tee_join
        elif self.join_status == 'join_stop':
            return self.conn.tee_stop
        return self.conn.tee

    def printTree(self, last=True, header='', checked_edges:list=None)-> str:
        """Prints the tree centered at the tNode
        
        Adapted from https://stackoverflow.com/a/76691030/15496939, PierreGtch, 
        under CC BY-SA 4.0.
        """
        out = str()
        out += header + self.printConn(last) + self.__str__()
        if checked_edges is None:
            checked_edges = list()
        if self.gen_edge_label in checked_edges:
            out += ' (derivative)\n' if len(self.children) != 0 else '\n'
            return out
        out += '\n'
        if self.gen_edge_label is not None:
            checked_edges.append(self.gen_edge_label)
        for i, child in enumerate(self.children):
            c_header = header + (self.conn.blank if last else self.conn.pipe)
            c_last = i == len(self.children) - 1
            out += child.printTree(header=c_header, last=c_last, checked_edges=checked_edges)
        return out
    
    def getDescendents(self)-> list:
        """Returns a list of child nodes on all depths (includes self)."""
        out = [self]
        for c in self.children:
            out += c.getDescendents()
        return out
    
    def mergeIndices(self, other: dict):
        """Updates the indices with those of another tNode."""
        for label in other:
            if label in self.indices:
                self.indices[label] = max((self.indices[label], other[label]))
            else:
                self.indices[label] = other[label]

    @property
    def index(self)-> int:
        """The current number of states cycled through along the tNode"""
        return max(self.indices.values()) + self.index_offset
        # if self.label not in self.indices:
        #     return 1
        # return self.indices[self.label] + self.index_offset
    
    def getTreeCost(self, root=None, checked_edges: set=None):
        """Returns the cost of solving to the leaves of the tree."""
        #FF0000
        #DEBUG MODE
        return 1.0
        #DEBUG MODE
        #FF0000
        if root is None:
            root = self
        if checked_edges is None:
            checked_edges = set()
        total_cost = 0
        if root.gen_edge_label not in checked_edges:
            total_cost += root.gen_edge_cost
            checked_edges.add(root.gen_edge_label)
            for st in root.children:
                total_cost += self.getTreeCost(st, checked_edges)
        return total_cost

    def __str__(self)-> str:
        out = self.label
        if self.value is not None:
            if isinstance(self.value, float):
                out += f'={self.value:.4g}'
            else:
                out += f'={self.value}'
        if self.cost is not None:
            out += f', cost={self.cost:.4g}'
        return out
    
class Node:
    """A value in the hypergraph, equivalent to a wired connection."""
    def __init__(self, label: str, static_value=None, generating_edges: set=None, 
                 leading_edges: set=None, super_nodes: set=None, 
                 description: str=None, index_offset: int=0):
        """Creates a new `Node` object.
        
        Parameters
        ----------
        label : str
            A unique identifier for the node.
        static_value : Any, Optional
            The constant value of the node, set as an input.
        generating_edges : set, Optional
            A set of edges that have the node as their target.
        leading_edges : set, Optional
            A set of edges that have the node as one their sources.
        super_nodes : Set[Node], Optional
            A set of nodes that have this node as a subset, see note [1] below.
        description : str, Optional
            A description of the node useful for debugging.
        is_constant : bool, default=False
            Describes whether the node should be reset in between simulations.
        starting_index : int, default=1
            The starting index of the node

        Properties
        ----------
        is_constant : bool, default = False
            Boolean indicating if the value of the node should change.

        Notes
        -----
        1. The subsetting accomplished by `super_nodes` is best conducted using `via` functions
        on the edge, as these will be executed for every node value. One case where 
        this is impossible is when the node has leading edges when generated by a 
        certain generating edge. In this case the `via` function cannot be used as the
        viability is *edge* dependent, not *value* dependent. Super nodes are provided 
        for this purpose, though do not provide full functionality. When searching,
        the leading edges of each super node are added to the search queue as a valid
        path away from the node.
        """
        self.label = label
        self.static_value = static_value
        self.generating_edges = set() if generating_edges is None else generating_edges
        self.leading_edges = set() if leading_edges is None else leading_edges
        self.description = description
        self.is_constant = static_value is not None
        self.index_offset = index_offset
        self.super_nodes = set() if super_nodes is None else makeSet(super_nodes)

    def __str__(self)-> str:
        out = self.label
        if self.description is not None:
            out += ': ' + self.description
        return out
    
    def __iadd__(self, o):
        return self.union(self, o)
    
    @staticmethod
    def union(a, *args):
        """Performs a deep union of the two nodes, replacing values of `a` with those 
        of `b` where necessary."""
        for b in args:
            if not isinstance(a, Node) or not isinstance(b, Node):
                raise TypeError("Inputs must be of type Node.")
            if b.label is not None:
                a.label = b.label
            if b.static_value is not None:
                a.static_value = b.static_value
                a.is_constant = b.is_constant
            if b.description is not None:
                a.description = b.description
            if b.index_offset != 0:
                a.index_offset = b.index_offset
            a.generating_edges = a.generating_edges.union(b.generating_edges)
            a.leading_edges = a.leading_edges.union(b.leading_edges)
            a.super_nodes = a.super_nodes.union(b.super_nodes)
        return a

class EdgeProperty(Enum):
    """Enumerated object describing various configurations of an Edge that can be 
    passed during setup. Used as shorthand for common configurations."""
    LEVEL = 1
    """Every source node in the edge must have the same index for the edge to be viable."""

class Edge:
    """A relationship along a set of nodes (the source) that produces a single value."""
    def __init__(self, label: str, source_nodes: dict, target: Node, rel: Callable, 
                 via: Callable=None, weight: float=1.0, edge_props: EdgeProperty=None):
        """Creates a new `Edge` object.
        
        Parameters
        ----------
        label : str
            A unique string identifier for the edge.
        source_nodes : dict{str : Node | Tuple(str, str)} | list[Node | 
                       Tuple(str, str)] |  Tuple(str, str) | Node 
            A dictionary of `Node` objects forming the source nodes of the edge, 
            where the key is the identifiable label for each source used in rel processing.
            The Node object may be a Node, or a length-2 Tuple (identifier : attribute) 
            with the first element an identifier in the edge and the second element a 
            string referencing an attribute of the identified Node to use as the value 
            (a pseudo node).
        rel : Callable
            A function taking the values of the source nodes and returning a single 
            value (the target).
        via : Callable, optional
            A function that must be true for the edge to be traversable (viable). 
            Default to uncondtionally
            true if not set.
        weight : float > 0.0, default=1.0
            The quanitified cost of traversing the edge. Must be positive, akin to a 
            distance measurement.
        edge_props : List(EdgeProperty) | EdgeProperty | str | int, optional
            A list of enumerated types that are used to configure the edge.
        """
        self.rel = rel
        self.via = self.via_true if via is None else via
        self.source_nodes = self.identifySouceNodes(source_nodes, self.rel, self.via)
        self.found_tNodes = {sn.label : list() for sn in self.source_nodes.values() if not isinstance(sn, tuple)}
        """A dict of lists of source_tNodes that are viable trees to a source node.
        Format: {sn_label : [tNode, tNode, ...]}"""
        self.target = target
        self.weight = abs(weight)
        self.label = label
        self.edge_props = self.setupEdgeProperties(edge_props)

    def addSourceNode(self, sn):
        """Adds a source node to an initialized edge.
        
        Parameters
        ----------
        sn : dict | Node | Tuple(str, str)
            The source node to be added to the edge.
        """
        if isinstance(sn, dict):
            key, sn = list(sn.items())[0]
        else:
            key = self.getSourceNodeIdentifier()
        if not isinstance(sn, tuple):
            sn.leading_edges.add(self)
            self.found_tNodes[sn.label] = list()

        source_nodes = self.source_nodes | {key: sn}
        if hasattr(self, 'og_source_nodes'):
            self.og_source_nodes[key] = sn
        self.source_nodes = self.identifySouceNodes(source_nodes)
        self.edge_props = self.setupEdgeProperties(self.edge_props)
        
    def setupEdgeProperties(self, inputs: None)-> list:
        """Parses the edge properties."""
        eps = list()
        if inputs is None:
            return eps
        inputs = makeList(inputs)
        for ep in inputs:
            if isinstance(ep, EdgeProperty):
                eps.append(ep)
            elif ep in EdgeProperty.__members__:
                eps.append(EdgeProperty[ep])
            elif ep in [item.value for item in EdgeProperty]:
                eps.append(EdgeProperty(ep))
            else:
                logger.warning(f"Unrecognized edge property: {ep}")
        for ep in eps:
            self.handleEdgeProperty(ep)
        return eps
    
    def getSourceNodeIdentifier(self, offset: int=0):
        """Returns a generic label for a source node."""
        return f's{len(self.source_nodes) + offset + 1}'
    
    def handleEdgeProperty(self, edge_prop: EdgeProperty):
        if edge_prop is EdgeProperty.LEVEL:
            if not hasattr(self, 'og_source_nodes'):
                self.og_source_nodes = {key: val for key, val in self.source_nodes.items()}
                self.og_rel = self.rel
                self.og_via = self.via
            tuple_idxs = {id:el[0] for id, el in self.source_nodes.items() if isinstance(el, tuple)}
            sns = {key: val for key, val in self.source_nodes.items()}
            for id, sn in sns.items():
                if isinstance(sn, tuple) or id in tuple_idxs.values():
                    continue
                next_id = self.getSourceNodeIdentifier()
                self.source_nodes[next_id] = (id, 'index')
                tuple_idxs[next_id] = id

            og_kwargs = lambda **kwargs : {key: val for key,val in kwargs.items() if key in self.og_source_nodes}
            def levelCheck(*args, **kwargs):
                """Returns true if all passed indices are equivalent."""
                if not self.og_via(*args, **kwargs):
                    return False
                idxs = {val for key, val in kwargs.items() if key in tuple_idxs}
                return len(idxs) == 1
            
            self.via = levelCheck
            self.rel = lambda *args, **kwargs : self.og_rel(*args, **og_kwargs(**kwargs))
            return


    # def handleEdgeProperty1(self, edge_prop: EdgeProperty):
    #     """Configures the edge based on the passed property."""
    #     if not hasattr(self, 'og_source_nodes'):
    #         self.og_source_nodes = {key: val for key, val in self.source_nodes.items()}
    #         self.og_rel = self.rel
    #         self.og_via = self.via
    #     if edge_prop is EdgeProperty.LEVEL:
    #         idx_entries  = dict()
    #         provided_idxs = {id:el[0] for id, el in self.og_source_nodes.items() if isinstance(el, tuple)}
    #         for key, sn in self.og_source_nodes.items():
    #             if isinstance(sn, tuple):
    #                 continue
    #             if key not in provided_idxs.values():
    #                 next_key = self.getSourceNodeIdentifier(len(idx_entries))
    #                 idx_entries[next_key] = (key, 'index')
    #         self.source_nodes = self.og_source_nodes | idx_entries

    #         og_kwargs = lambda **kwargs : {key: val for key,val in kwargs.items() if key in self.og_source_nodes}
    #         def levelCheck(*args, **kwargs):
    #             """Returns true if all passed indices are equivalent."""
    #             if not self.og_via(*args, **og_kwargs(**kwargs)):
    #                 return False
    #             idxs = {val for key, val in kwargs.items() if key in idx_entries or key in provided_idxs}
    #             return len(idxs) == 1

    #         self.rel = lambda *args, **kwargs : self.og_rel(*args, **og_kwargs(**kwargs))
    #         self.via = levelCheck

    @staticmethod
    def getNamedArguments(methods: List[Callable])-> set:
        """Returns keywords for any keyed, required arguments (non-default)."""
        out = set()
        for method in methods:
            for p in signature(method).parameters.values():
                if p.kind == p.POSITIONAL_OR_KEYWORD and p.default is p.empty:
                    out.add(p.name)
        return out 

    def identifySouceNodes(self, source_nodes, rel: Callable=None, via: Callable=None):
        """Returns a {str: node} dictionary where each string is the keyword label used
        in the rel and via methods."""
        if rel is None:
            rel = self.rel
        if via is None:
            via = self.via
        if isinstance(source_nodes, dict):
            return self.identifyLabeledSourceNodes(source_nodes, rel, via)
        else:
            source_nodes = makeList(source_nodes)
        return self.identifyUnlabeledSourceNodes(source_nodes, rel, via)
    
    def identifyUnlabeledSourceNodes(self, source_nodes: list, rel: Callable, via: Callable):
        """Returns a {str: node} dictionary where each string is the keyword label used
        in the rel and via methods."""
        arg_keys = self.getNamedArguments([via, rel])
        arg_keys = arg_keys.union({f's{i+1}' for i in range(len(source_nodes) - len(arg_keys))})

        out = {key : sn for key, sn in zip(arg_keys, source_nodes)}
        return out
    
    def identifyLabeledSourceNodes(self, source_nodes: dict, rel: Callable, via: Callable):
        """Returns a {str: node} dictionary where each string is the keyword label used
        in the rel and via methods."""
        out = dict()
        arg_keys = self.getNamedArguments([rel, via])
        arg_keys = arg_keys.union({str(key) for key in source_nodes})

        for arg_key in arg_keys:
            if len(source_nodes) == 0:
                return out
            if arg_key in source_nodes:
                sn_key = arg_key
            else:
                sn_key = list(source_nodes.keys())[0]
            out[arg_key] = source_nodes[sn_key]
            del(source_nodes[sn_key])

        return out   
    
    def process(self, source_tNodes: list):
        """Processes the tNodes to get the value of the target."""
        labeled_values = self.getSourceValues(source_tNodes)
        target_val = self.processValues(labeled_values)
        return target_val

    def getSourceValues(self, source_tNodes: list):
        """Returns a dictionary of source values with their relevant keys."""
        source_values = dict()

        tuple_keys = filter(lambda key : isinstance(self.source_nodes[key], tuple), self.source_nodes)
        psuedo_nodes = {key : self.source_nodes[key] for key in tuple_keys}
        for key in psuedo_nodes:
            pseudo_identifier, pseduo_attribute = psuedo_nodes[key]
            if pseudo_identifier in self.source_nodes:
                sn_label = self.source_nodes[pseudo_identifier].label
                for st in source_tNodes:
                    if st.label == sn_label:
                        source_values[key] = getattr(st, pseduo_attribute)
                        break

        for st in source_tNodes:
            for key, sn in self.source_nodes.items():
                if not isinstance(sn, tuple) and st.label == sn.label:
                    source_values[key] = st.value
                    break
        return source_values

    def processValues(self, source_vals: dict)-> float:
        """Finds the target value based on the source values."""
        if None in source_vals:
            return None
        if self.via(**source_vals):
            return self.rel(**source_vals)
        return None
    
    def getSourceTNodeCombinations(self, t: tNode, DEBUG: bool=False):
        """Returns all viable combinations of source nodes using the tNode `t`."""
        appendToDictList(self.found_tNodes, t.label, t)
        st_candidates = list()

        if DEBUG:
            for st_label, sts in self.found_tNodes.items():
                msg = f' - {st_label}: ' + ', '.join(f'{str(st.value)[:4]}({st.index})' for st in sts)
                logger.log(logging.DEBUG + 1, msg)

        for st_label, sts in self.found_tNodes.items():
            if st_label == t.label:
                st_candidates.append([t])
            elif len(sts) == 0:
                return []
            else:
                st_candidates.append(sts)

        st_combos = itertools.product(*st_candidates)
        return st_combos
            
    @staticmethod
    def via_true(*args, **kwargs):
        """Returns true for all inputs (unconditional edge)."""
        return True
    
    def __str__(self):
        return self.label

class Pathfinder:
    """Object for searching a path through the hypergraph from a collection of source
    nodes to a single target node. If the hypergraph is fully constrained and viable,
    then the result of the search is a singular value of the target node."""
    def __init__(self, target: Node, sources: list, nodes: dict):
        """Creates a new Pathfinder object.
        
        Parameters
        ----------
        target : Node
            The Node that the Pathfinder will attempt to solve for.
        source_nodes : list
            A list of Node objects that have static values for the simulation.
        nodes : dict
            A dictionary of nodes taken from the hypergraph as {label : Node}.
        """
        self.nodes = nodes
        self.source_nodes = sources
        self.target_node = target
        self.search_roots = list()
        self.search_counter = 0
        """Number of nodes explored"""

    def search(self, debug_nodes: list=None, debug_edges: list=None, search_depth: int=10000):
        """Searches the hypergraph for a path from the source nodes to the target 
        node. Returns the solved tNode for the target and a dictionary of found values
        {label : [Any,]}. """
        debug_nodes = list() if debug_nodes is None else debug_nodes
        debug_edges = list() if debug_edges is None else debug_edges
        logger.info(f'Begin search for {self.target_node.label}')

        for sn in self.source_nodes:
            st = tNode(sn.label, sn.static_value, cost=0., index_offset=sn.index_offset)
            self.search_roots.append(st)

        while len(self.search_roots) > 0:
            if self.search_counter > search_depth:
                raise(Exception("Maximum search limit exceeded.")) 
            logger.debug('Search trees: ' + ', '.join(f'{s.label}' for s in self.search_roots))

            root = self.selectRoot()
            if root.label is self.target_node.label:
                logger.info(f'Finished search for {self.target_node.label} with value of {root.value}')
                logger.info(f'Final search counter: {self.search_counter}')
                return root, root.values
            
            self.explore(root, debug_nodes, debug_edges)
            
        logger.info(f'Finished search, no solutions found')
        logger.info(f'Final search counter: {self.search_counter}')
        return None, None
    
    def explore(self, t: tNode, debug_nodes: list=None, debug_edges: list=None):
        """Discovers all possible routes from the tNode."""
        n = self.nodes[t.label]
        super_node_leading_edges = (sup_n.leading_edges for sup_n in n.super_nodes)
        leading_edges = n.leading_edges.union(*super_node_leading_edges)
        if n.label in debug_nodes:
            logger.log(logging.DEBUG + 1, f'Exploring {n.label}, leading edges: ' + 
                         ', '.join(str(le) for le in leading_edges) + f'\n{t.printTree()}')
            
        for i, edge in enumerate(leading_edges):
            DEBUG = edge.label in debug_edges
            level = logging.DEBUG + (1 if DEBUG else 0)
            logger.log(level, f"Edge {i}, <{edge.label}>:")

            combos = edge.getSourceTNodeCombinations(t, DEBUG)
            for j, combo in enumerate(combos):
                logger.debug(f' - Combo {j}: ' + ', '.join(f'{n.label} ({n.index})' for n in combo))
                self.makeParentTNode(combo, edge.target, edge)

    def makeParentTNode(self, source_tNodes: list, node: Node, edge: Edge):
        """Creates a tNode for the next step along the edge."""
        parent_val = edge.process(source_tNodes)
        if parent_val is None:
            return None
        label = node.label
        children = source_tNodes
        gen_edge_label = edge.label + '#' + str(self.search_counter)
        parent_t = tNode(label, parent_val, children, gen_edge_label=gen_edge_label, 
                         gen_edge_cost=edge.weight, index_offset=node.index_offset)
        for st in source_tNodes:
            parent_t.mergeIndices(st.indices)
        parent_t.indices[node.label] += 1
        parent_t.values = self.mergeFoundValues(parent_val, node.label, source_tNodes)
        parent_t.cost = parent_t.getTreeCost()
        self.search_roots.append(parent_t)
        self.search_counter += 1
        return parent_t
                
    def selectRoot(self)-> tNode:
        """Determines the most optimal path to explore."""
        #TODO: Check all leading edges to find the node with the lowest cost path
        if len(self.search_roots) == 0:
            return None
        # root = None
        # for st in self.search_roots:
        #     if st.label == self.target_node.label:
        #         root = st
        #         break
        #     if root is None or root.cost > st.cost:
        #         root = st
        # self.search_roots.remove(root)
        # return root
        root = min(self.search_roots, key=lambda t : t.cost)
        self.search_roots.remove(root)
        return root
    
    def mergeFoundValues(self, parent_val, parent_label, source_tNodes: list)-> dict:
        """Merges the values found in the source nodes with the parent node."""
        if parent_label == 'theta':
            z = 2 +2 
        values = {parent_label: list()}
        for st in source_tNodes:
            for label, st_values in st.values.items():
                if label not in values or len(st_values) > len(values[label]):
                    if label == 'theta' and parent_label == 'theta':
                        a = [float(v) for v in st_values]
                        z = 1+1
                    values[label] = st_values
        values[parent_label].append(parent_val)
        return values
        
class Hypergraph:
    """Builder class for a hypergraph. See demos for examples on how to use."""
    def __init__(self):
        """Initialize a Hypergraph."""
        self.nodes = dict()
        self.edges = dict()

    def getNode(self, node_key)-> Node:
        """Caller function for finding a node in the hypergraph."""
        if isinstance(node_key, Node):
            node_key = node_key.label
        try:
            return self.nodes[node_key]
        except KeyError:
            return None
        
    def getEdge(self, edge_key)-> Node:
        """Caller function for finding a node in the hypergraph."""
        if isinstance(edge_key, Edge):
            edge_key = edge_key.label
        try:
            return self.edges[edge_key]
        except KeyError:
            return None
        
    def reset(self):
        """Clears all values in the hypergraph."""
        for node in self.nodes.values():
            if not node.is_constant:
                node.static_value = None

    def requestNodeLabel(self, requested_label=None)-> str:
        """Generates a unique label for a node in the hypergraph"""
        label = 'n'
        if requested_label is not None:
            label = requested_label
        i = 0
        check_label = label
        while check_label in self.nodes:
            check_label = label + str(i := i + 1)
        return check_label
    
    def requestEdgeLabel(self, requested_label: str=None, source_nodes: list=None)-> str:
        """Generates a unique label for an edge in the hypergraph."""
        label = 'e'
        if requested_label is not None:
            label = requested_label
        elif source_nodes is not None:
            label = ''.join(s.label[0].lower() for s in source_nodes[:4])
        i = 0
        check_label = label
        while check_label in self.edges:
            check_label = label + str(i := i + 1)
        return check_label
    
    def addNode(self, *args, **kwargs)-> Node:
        """Wraps Node.__init__() and also inserts the Node into the hypergraph."""
        node = Node(*args, **kwargs)
        self.insertNode(node)

    def insertNode(self, node: Node, value=None)-> Node:
        """Adds a node to the hypergraph via a union operation."""
        if isinstance(node, tuple):
            return None
        if isinstance(node, Node):
            if node.label in self.nodes:
                label = node.label
                self.nodes[label] += node
            else:
                label = self.requestNodeLabel(node.label)
                self.nodes[label] = node
        else:
            if node in self.nodes: 
                label = node
                self.nodes[label].static_value = value
            else:
                label = self.requestNodeLabel(node)
                self.nodes[label] = Node(label, value) 
        return self.nodes[label]

    def addEdge(self, sources: dict, target, rel, via=None, weight: float=1.0, 
                label: str=None, edge_props=None):
        """Adds an edge to the hypergraph.
        
        Parameters
        ----------
        sources : dict{str : Node | Tuple(Node, str)} | list[Node | 
                       Tuple(Node, str)] |  Tuple(Node, str) | Node 
            A dictionary of `Node` objects forming the source nodes of the edge, 
            where the key is the identifiable label for each source used in rel processing.
            The Node object may be a Node, or a length-2 Tuple with the second element
            a string referencing an attribute of the Node to use as the value (a pseudo
            node).
        targets : list | str | Node
            A list of nodes that are the target of the given edge, with the same type
            as sources. Since each edge can only have one target, this makes a unique
            edge for each target.
        rel : Callable
            A function taking in a value for each source node that returns a single 
            value for the target.
        weight : float, default=1.0
            The cost of traversing the edge. Must be positive.
        label : str, optional
            A unique identifier for the edge.
        edge_props : List(EdgeProperty) | EdgeProperty | str | int, optional
            A list of enumerated types that are used to configure the edge.
        """
        source_nodes, source_inputs = self.getNodesAndIdentifiers(sources)
        target_nodes, target_inputs = self.getNodesAndIdentifiers([target])
        label = self.requestEdgeLabel(label, source_nodes + target_nodes)
        edge = Edge(label, source_inputs, target_nodes[0], rel, via, weight, edge_props=edge_props)
        self.edges[label] = edge
        for sn in source_nodes:
            sn.leading_edges.add(edge)
        for tn in target_nodes:
            tn.generating_edges.add(edge)
        return edge
    
    def insertEdge(self, edge: Edge):
        """Inserts a fully formed edge into the hypergraph."""
        if not isinstance(edge, Edge):
            raise TypeError('edge must be of type `Edge`')
        self.edges[edge.label] = edge
        tn = self.insertNode(edge.target)
        tn.generating_edges.add(edge)
        
    def getNodesAndIdentifiers(self, nodes):
        """Helper function for getting a list of nodes and their identified argument 
        format for various input types."""
        if isinstance(nodes, dict):
            node_list, inputs = list(), dict()
            for key, node in nodes.items():
                if isinstance(node, tuple):
                    if node[0] not in nodes:
                        raise(Exception(f"Pseudo node identifier '{node[0]}' not included in Edge."))
                else:
                    node = self.insertNode(node)
                    node_list.append(node)
                inputs[key] = node
            return node_list, inputs
        
        nodes = makeList(nodes)
        node_list = [self.insertNode(n) for n in nodes]
        inputs = [self.getNode(node) for node in nodes if not isinstance(node, tuple)]
        return node_list, inputs
    
    def setNodeValues(self, node_values: dict):
        """Sets the values of the given nodes."""
        for key, value in node_values.items():
            node = self.getNode(key)
            node.static_value = value
    
    def solve(self, target, node_values: dict=None, toPrint: bool=False, 
              debug_nodes: list=None, debug_edges: list=None, search_depth: int=100000):
        """Runs a DFS search to identify the first valid solution for `target`.
        
        Parameters
        ----------
        target : Node | str
            The node or label of the node to solve for.
        node_values : dict, optional
            A dictionary {label : value} of input values.
        toPrint : bool, default=False
            Prints the search tree if set to true.
        debug_nodes : List[label,], optional
            A list of node labels to log debugging information for
        debug_edges : List[label,], optional
            A list of edge labels to log debugging information for
        search_depth : int, default=100000
            Number of nodes to explore before concluding no valid path.

        Returns
        -------
        tNode | None
            the tNode for the minimum-cost path found
        dict | None
            a dictionary of values found for each node in the search path, as {label : List[value,]}
        """
        self.reset()
        if node_values is not None:
            self.setNodeValues(node_values)
            source_nodes = [self.getNode(label) for label in node_values]
            source_nodes += [node for node in self.nodes.values() if node.is_constant and node.label not in node_values]
        else:
            source_nodes = [node for node in self.nodes.values() if node.is_constant]
        target_node = self.getNode(target)
        pf = Pathfinder(target_node, source_nodes, self.nodes)
        try:
            t, found_values = pf.search(debug_nodes, debug_edges, search_depth)
        except Exception as e:
            logger.error(str(e))
            raise(e)     
        if toPrint:
            if t is not None:
                print(t.printTree())
            else:
                print("No solutions found")
        return t, found_values
    
    def printPaths(self, target, toPrint: bool=False)-> str:
        """Prints the hypertree of all paths to the target node."""
        target_node = self.getNode(target)
        target_tNode = self.printPathsHelper(target_node)
        out = target_tNode.printTree()
        if toPrint:
            print(out)
        return out

    def printPathsHelper(self, node: Node, join_status='none', trace: list=None)-> tNode:
        """Recursive helper to print all paths to the target node."""
        if isinstance(node, tuple):
            return None
        t = tNode(node.label, node.static_value, join_status=join_status, trace=trace)
        branch_costs = list()
        for edge in node.generating_edges:
            if self.edgeInCycle(edge, t):
                t.label += '[CYCLE]'
                return t

            child_cost = 0
            for i, child in enumerate(edge.source_nodes.values()):
                c_join_status = self.getJoinStatus(i, len(edge.source_nodes))
                c_trace = t.trace + [(t, edge)]
                c_tNode = self.printPathsHelper(child, c_join_status, c_trace)
                if c_tNode is None:
                    continue
                child_cost += c_tNode.cost if c_tNode.cost is not None else 0.0
                t.children.append(c_tNode)
            branch_costs.append(child_cost + edge.weight)

        t.cost = min(branch_costs) if len(branch_costs) > 0 else 0.
        return t
    
    def edgeInCycle(self, edge: Edge, t: tNode):
        """Returns true if the edge is part of a cycle in the tree rooted at the tNode."""
        return edge.label in [e.label for tt, e in t.trace]
    
    def getJoinStatus(self, index, num_children):
        """Returns whether or not the node at the given index is part of a hyperedge (`join`) or specifically the last node 
        in a hyperedge (`join_stop`) or a singular edge (`none`)"""
        if num_children > 1:
            return 'join_stop' if index == num_children - 1 else 'join'
        return 'none'
    
    def __str__(self)-> str:
        return