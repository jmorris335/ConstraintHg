from typing import Callable
import logging as log

import src.constrainthg.CONTROL as CONTROL

class tNode:
    """A basic tree node for printing tree structures."""
    class conn:
        elbow = "└──"
        pipe = "│  "
        tee = "├──"
        blank = "   "
        elbow_join = "└◯─"
        tee_join = "├◯─"
        elbow_stop = "└●─"
        tee_stop = "├●─"
    
    def __init__(self, label, value=None, children: list=None, join_status: str='None', 
                 cost: float=None, trace: list=None, indices: dict=None):
        self.label = label
        self.value = value
        self.children = list() if children is None else children
        self.join_status = join_status
        self.cost = cost
        self.trace = list() if trace is None else trace
        """List of connected (tNode, Edge) pairings, the last of which the tNode is a 
        leaf for."""
        self.indices = dict() if indices is None else indices
        """Counts of how many times each node has been visited in the tNode (label : int)."""
 
    def printConn(self, last=True)-> str:
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

    def printTree(self, last=True, header='')-> str:
        """Prints the tree centered at the tNode
        
        Adapted from https://stackoverflow.com/a/76691030/15496939, PierreGtch, 
        under CC BY-SA 4.0.
        """
        out = str()
        out += header + self.printConn(last) + self.__str__() + '\n'
        for i, child in enumerate(self.children):
            c_header = header + (self.conn.blank if last else self.conn.pipe)
            c_last = i == len(self.children) - 1
            out += child.printTree(header=c_header, last=c_last)
        return out
    
    def getDescendents(self)-> list:
        """Returns a list of child nodes on all depths (includes self)."""
        out = [self]
        for c in self.children:
            out += c.getDescendents()
        return out
    
    def mergeIndices(self, other: dict):
        """Updates the indices with those of another tNode."""
        #TODO: Each tNode holds the previous indices, and they're all adding up (not just the target tNode)

        # print(self.printTree())
        # a = 1 + 1
        for label in other:
            if label in self.indices:
                self.indices[label] = sum((self.indices[label], other[label]))
            else:
                self.indices[label] = other[label]

    @property
    def index(self)-> int:
        """The current number of states cycled through along the tNode"""
        if len(self.indices) == 0:
            return 0
        return max(self.indices.values())


    def __str__(self)-> str:
        out = self.label
        if self.value is not None:
            if isinstance(self.value, float):
                out += f'= {self.value:.4g}'
            else:
                out += f'= {self.value}'
        if self.cost is not None:
            out += f', cost={self.cost:.4g}'
        return out
    
class Node:
    """A value in the hypergraph, equivalent to a wired connection."""
    def __init__(self, label: str, value=None, generating_edges: list=None, description: str=None):
        """Creates a new `Node` object.
        
        Parameters
        ----------
        label : str
            A unique identifier for the node.
        value : Any, Optional
            The value of the node. 
        generating_edges : list, Optional
            A list of edges that have the node as their target.
        description : str, Optional
            A description of the node useful for debugging.

        Properties
        ----------
        is_simulated : bool, default = False
            Marker saying that the value was artificially generated from an edge 
            (used for resetting the Node after a simulation).
        """
        self.label = label
        self.value = value
        self.generating_edges = list() if generating_edges is None else generating_edges
        self.description = description
        self.values = list()
        """List of tNodes with potential values."""
        self.is_simulated = False
        """Marker saying that the value was artificially generated (used for resetting the Node after a simulation)."""
        
    def setValue(self, value, is_simulated: bool=True):
        """Sets the value for the node"""
        self.value = value
        self.is_simulated = is_simulated

    def __str__(self)-> str:
        out = self.label
        if self.description is not None:
            out += ': ' + self.description
        return out

class Edge:
    """A relationship along a set of nodes (the source) that produces a single value."""
    def __init__(self, label: str, source_nodes: dict, rel: Callable, 
                 via: Callable=None, weight: float=1.0, pseudo: str=None):
        """Creates a new `Edge` object.
        
        Parameters
        ----------
        label : str
            A unique string identifier for the edge.
        source_nodes : dict
            A dictionary of `Node` objects forming the source nodes of the edge, 
            where the key is the identifiable label for each source used in rel processing.
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
        pseudo : str, optional
            A enumerated string to call a nodal property at runtime rather than a source
            value. Recognized values are properties of `Node`.
        """
        self.source_nodes = source_nodes
        self.rel = rel
        self.via = self.via_true if via is None else via
        self.weight = abs(weight)
        self.label = label
        self.pseudo = pseudo

        self.source_tNodes = {sn.label : list() for sn in self.source_nodes.values()}
    
    def edgeInCycle(self, t: tNode):
        """Returns true if the edge is part of the cycle manifest by the `target_tNode`."""
        return self.label in [e.label for tt, e in t.trace]
    
    def process(self, source_tNodes: list):
        """Processes the tNodes to get the value of the target."""
        labeled_values = self.getSourceValues(source_tNodes)
        target_val = self.processValues(labeled_values)
        return target_val

    def getSourceValues(self, source_tNodes: list):
        """Returns a dictionary of source values with their relevant keys."""
        labeled_values = dict()
        for st in source_tNodes:
            for key, sn in self.source_nodes.items():
                if st.label == sn.label:
                    if self.pseudo is not None:
                        labeled_values[key] = getattr(st, self.pseudo)
                    else:
                        labeled_values[key] = st.value
                    break
        return labeled_values

    def processValues(self, source_vals: dict)-> float:
        """Finds the target value based on the source values."""
        if None in source_vals:
            return None
        if self.via(**source_vals):
            return self.rel(**source_vals)
        return None
            
    @staticmethod
    def via_true(*args, **kwargs):
        """Returns true for all inputs (unconditional edge)."""
        return True

class Pathfinder:
    """Class for recursively searching a hypergraph using a best-first search approach."""
    class tEdge:
        """Container for duplicating edges in a tree."""
        __slots__ = ('label', 'source_tNodes', 'edge')
        def __init__(self, label: str, edge: Edge):
            self.label = label
            self.edge = edge
            self.source_tNodes = list()

        def getTNode(self, label: str):
            """Returns the source tNode with the given label."""
            tNode_labels = [st.label for st in self.source_tNodes]
            return self.source_tNodes[tNode_labels.index(label)]
             
    def __init__(self, target: Node, nodes: dict):
        """Creates the initial search structure for a best-first search strategy.
        
        Parameters
        ----------
        target : Node
            The node for which the search is trying to evaluate.
        nodes : dict
            A dictionary of nodes as {node_label : Node}
        """
        self.target = target
        self.nodes = nodes
        self.paths = list()
        """List of tNodes, each the leaf of a potential tree path to the target."""
        self.tEdges = dict()
        """Dictionary of found sources for an edge, with 'tEdge_label' : tEdge format"""
        self.label_index = 0
        """Int used to identify tEdges in a path (many of which are duplicated)."""
        self.best_path = None
        """The tNode root of the best path found by the solver."""

    def search(self):
        """Find the lowest-cost simulated value for the target node."""
        target_tNode = tNode(self.target.label, cost=0.)
        self.exploreNode(target_tNode)

        while len(self.paths) > 0:
            if self.label_index > CONTROL.CYCLE_SEARCH_DEPTH:
                if self.best_path is not None:
                    print("Best found path:")
                    print(self.best_path.printTree())
                raise(Exception("Maximum search depth exceeded."))
            t = self.selectPath()

            self.exploreNode(t)
            if t.value is not None:
                t.cost = 0
                found_root = self.solveLeaf(t)
                if self.best_path is None or found_root.cost > self.best_path.cost:
                    self.best_path = found_root
                if self.best_path.label == target_tNode.label:
                    return target_tNode
                log.debug('Current path:\n' + t.printTree())

            self.paths.remove(t)

        return None
    
    def exploreNode(self, t: tNode):
        """Appends all possible paths leading from the tNode to the `paths` member."""
        if t.label in self.nodes:
            n = self.nodes[t.label]
        else:
            return #Node not in hypergraph
        
        for e in n.generating_edges:
            e_t = self.makeTEdge(e)
            self.tEdges[e_t.label] = e_t
            cost = t.cost + e.weight
            trace = t.trace + [(e_t.label, t)]

            for sn in e.source_nodes.values():
                st = tNode(sn.label, sn.value, cost=cost, trace=trace, indices={})
                e_t.source_tNodes.append(st)
                self.paths.append(st)

    def selectPath(self)-> tNode:
        """Determines the most optimal path to explore."""
        if len(self.paths) == 0:
            return None
        return min(self.paths, key=lambda t : t.cost)

    def makeTEdge(self, edge: Edge)-> tEdge:
        """Returns a unique tEdge for the edge (including duplicate cycle edges)."""
        self.label_index += 1
        tEdge_label = edge.label + str(self.label_index)
        return self.tEdge(tEdge_label, edge)

    def solveLeaf(self, t: tNode)-> tNode:
        """Procedurally solves  the system as far as possible given the leaf node."""
        if t.label == self.target.label:
            return t
        
        tEdge_label, parent_t = t.trace[-1]
        et = self.tEdges[tEdge_label]

        if all(st.value is not None for st in et.source_tNodes):
            parent_val = et.edge.process(et.source_tNodes)
            if parent_val is None:
                return t
            
            parent_t.indices = {parent_t.label : 1}
            parent_t.value = parent_val
            parent_t.children = et.source_tNodes
            parent_t.cost = sum([a.cost for a in et.source_tNodes]) + et.edge.weight
            for st in et.source_tNodes:
                parent_t.mergeIndices(st.indices)
            return self.solveLeaf(parent_t)

        return t

class Hypergraph:
    """Builder class for a hypergraph. See demos for information on how to use."""
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
        for key in self.nodes:
            node = self.nodes[key]
            if node.is_simulated:
                node.value = None
            node.is_simulated = False

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

    def addNode(self, node: Node, value=None)-> Node:
        """Adds a node to the hypergraph via a union operation."""
        label = node.label if isinstance(node, Node) else node
        if label in self.nodes: 
            self.nodes[label].value = node.value if isinstance(node, Node) else value
            return self.nodes[label]

        label = self.requestNodeLabel(label)
        if isinstance(node, Node):
            node.label = label
        else:
            node = Node(label, value) 
        self.nodes[label] = node
        return node

    def addEdge(self, sources: list, targets: list, rel, via=None, weight: float=1.0, 
                label: str=None, identify: dict=None, pseudo: str=None):
        """Adds an edge to the hypergraph.
        
        Parameters
        ----------
        sources : list | str | Node
            A list of nodes that are sources to the edge. Nodes may be references to 
            actual `Node` objects or the labels of `Node` objects (passed as strings).
            Sources may be passed as a list or a single object.
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
        identify : dict, optional
            A dictionary of `str : str` items where the keys are labels of the source
            nodes and the values are keywords for the arguments of `rel`, used to 
            identify the values of the source nodes when called by `rel`.
        pseudo : str, optional
            A enumerated string to call a nodal property at runtime rather than a source
            value. Recognized values are properties of `Node`.
        """
        if not isinstance(sources, list):
            sources = [sources]
        if not isinstance(targets, list):
            targets = [targets]
        source_nodes = [self.addNode(source) for source in sources]
        target_nodes = [self.addNode(target) for target in targets]
        label = self.requestEdgeLabel(label, source_nodes + target_nodes)
        source_node_dict = self.assignSourceIdentities(source_nodes, identify)
        edge = Edge(label, source_node_dict, rel, via, weight, pseudo)
        self.edges[label] = edge
        for target in target_nodes:
            target.generating_edges.append(edge)
        return edge
    
    def assignSourceIdentities(self, source_nodes: list, identify: dict):
        """Assigns an identifier to each source node."""
        if identify is None:
            identify = dict()
        else:
            identify = {self.getNode(key) : identify[key] for key in identify}
        identified = dict()
        reserved = identify.values()
        for sn in source_nodes:
            if sn in identify:
                identifier = identify[sn]
            else:
                for i in range(len(source_nodes) + len(reserved)):
                    identifier = f's{len(identified) + i + 1}'
                    if identifier not in reserved:
                        break
            identified[identifier] = sn
        return identified
    
    def setNodeValues(self, node_values: dict):
        """Sets the values of the given nodes."""
        for key in node_values:
            node = self.getNode(key)
            node.setValue(node_values[key], is_simulated=False)
    
    def solve(self, target, node_values: dict=None, toPrint: bool=False):
        """Runs a DFS search to identify the first valid solution for `target`."""
        self.reset()
        if node_values is not None:
            self.setNodeValues(node_values)
        target_node = self.getNode(target)
        t = Pathfinder(target_node, self.nodes).search()
        if t is None:
            return None
        elif toPrint:
            print(t.printTree())
        return t.value
    
    def printPaths(self, target, toPrint: bool=True)-> str:
        """Prints the hypertree of all paths to the target node."""
        target_node = self.getNode(target)
        target_tNode = self.printPathsHelper(target_node)
        out = target_tNode.printTree()
        if toPrint:
            print(out)
        return out

    def printPathsHelper(self, node: Node, join_status='none', trace: list=None)-> tNode:
        """Recursive helper to print all paths to the target node."""
        t = tNode(node.label, node.value, join_status=join_status, trace=trace)
        branch_costs = list()
        for edge in node.generating_edges:
            if edge.edgeInCycle(t):
                t.label += '[CYCLE]'
                return t

            child_cost = 0
            for i, child in enumerate(edge.source_nodes.values()):
                c_join_status = self.getJoinStatus(i, len(edge.source_nodes))
                c_trace = t.trace + [(t, edge)]
                c_tNode = self.printPathsHelper(child, c_join_status, c_trace)
                child_cost += c_tNode.cost if c_tNode.cost is not None else 0.0
                t.children.append(c_tNode)
            branch_costs.append(child_cost + edge.weight)

        t.cost = min(branch_costs) if len(branch_costs) > 0 else 0.
        return t
    
    def getJoinStatus(self, index, num_children):
        """Returns whether or not the node at the given index is part of a hyperedge (`join`) or specifically the last node 
        in a hyperedge (`join_stop`) or a singular edge (`none`)"""
        if num_children > 1:
            return 'join_stop' if index == num_children - 1 else 'join'
        return 'none'
    
    def __str__(self)-> str:
        return