from typing import Callable, List
from inspect import signature, Parameter
import logging as log
import itertools

import constrainthg.CONTROL as CONTROL

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
    
    def __init__(self, label, value=None, children: list=None, cost: float=None, 
                 indices: dict=None, trace: list=None, join_status: str='None' ):
        self.label = label
        self.value = value
        self.children = list() if children is None else children
        self.join_status = join_status
        self.cost = cost
        self.trace = list() if trace is None else trace
        self.indices = {label : 0} if indices is None else indices
        """Counts of how many times each node was uniquely solved for in the path (label : int)."""
 
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
        for label in other:
            if label in self.indices:
                self.indices[label] = max((self.indices[label], other[label]))
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
    def __init__(self, label: str, static_value=None, generating_edges: list=None, 
                 leading_edges: list=None, description: str=None):
        """Creates a new `Node` object.
        
        Parameters
        ----------
        label : str
            A unique identifier for the node.
        static_value : Any, Optional
            The constant value of the node, set as an input.
        generating_edges : list, Optional
            A list of edges that have the node as their target.
        leading_edges : list, Optional
            A list of edges that have the node as one their sources.
        description : str, Optional
            A description of the node useful for debugging.
        is_constant : bool, default=False
            Describes whether the node should be reset in between simulations.

        Properties
        ----------
        is_simulated : bool, default = False
            Marker saying that the value was artificially generated from an edge 
            (used for resetting the Node after a simulation).
        """
        self.label = label
        self.static_value = static_value
        self.generating_edges = list() if generating_edges is None else generating_edges
        self.leading_edges = list() if leading_edges is None else leading_edges
        self.description = description
        self.is_constant = static_value is not None

    def __str__(self)-> str:
        out = self.label
        if self.description is not None:
            out += ': ' + self.description
        return out

class Edge:
    """A relationship along a set of nodes (the source) that produces a single value."""
    def __init__(self, label: str, source_nodes: dict, target: Node, rel: Callable, 
                 via: Callable=None, weight: float=1.0):
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

    @staticmethod
    def getNamedArguments(methods: List[Callable])-> set:
        """Returns keywords for any keyed, required arguments (non-default)."""
        out = set()
        for method in methods:
            for p in signature(method).parameters.values():
                if p.kind == p.POSITIONAL_OR_KEYWORD and p.default is p.empty:
                    out.add(p.name)
        return out 

    def identifySouceNodes(self, source_nodes, rel: Callable, via: Callable):
        """Returns a {str: node} dictionary where each string is the keyword label used
        in the rel and via methods."""
        if isinstance(source_nodes, dict):
            return self.identifyLabeledSourceNodes(source_nodes, rel, via)
        elif not isinstance(source_nodes, list):
            source_nodes = [source_nodes]
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
    
    def getSourceTNodeCombinations(self, t: tNode):
        """Returns all viable combinations of source nodes using the tNode `t`."""
        self.found_tNodes[t.label].append(t)
        st_candidates = list()

        for st_label, sts in self.found_tNodes.items():
            if st_label == t.label:
                st_candidates.append([t])
            elif len(sts) == 0:
                return []
            else:
                # same_index = [st for st in sts if st.index == t.index]
                # st_candidates.append(same_index)
                st_candidates.append(sts)

        st_combos = itertools.product(*st_candidates)
        return st_combos
            
    @staticmethod
    def via_true(*args, **kwargs):
        """Returns true for all inputs (unconditional edge)."""
        return True

class Pathfinder:
    def __init__(self, target: Node, sources: list, nodes: dict):
        self.nodes = nodes
        self.source_nodes = sources
        self.target_node = target
        self.search_roots = list()
        self.found_tNodes = {label : list() for label in nodes}
        self.search_counter = 0
        """Number of nodes explored"""

    def search(self, toPrint: bool=False):
        for sn in self.source_nodes:
            st = tNode(sn.label, sn.static_value, cost=0.)
            self.search_roots.append(st)
            self.found_tNodes[st.label].append(st)
        
        while len(self.search_roots) > 0:
            if self.search_counter > CONTROL.CYCLE_SEARCH_DEPTH:
                raise(Exception("Maximum search depth exceeded."))
            root = self.selectRoot()
            if root.label is self.target_node.label:
                found_values = self.getFoundValues(root)
                return root, found_values
            
            self.explore(root)
            # print(f'############### {root.label} ###############\n')
            # for i, s in enumerate(self.search_roots):
            #     print(f'{i}: {s.printTree()}')
            # a = 1 + 1

        # best_found = max(itertools.chain(*self.found_tNodes.values()), key=lambda fTn : fTn.cost)
        # return None, self.getFoundValues(best_found)
        if toPrint:
            print("No solutions found")
        return None, None
    
    def explore(self, t: tNode):
        """Discovers all possible routes from the tNode."""
        n = self.nodes[t.label]
        for edge in n.leading_edges:
            parent = edge.target
            source_tNode_combos = edge.getSourceTNodeCombinations(t)
            for combo in source_tNode_combos:
                self.makeParentTNode(combo, parent, edge)
        self.search_roots.remove(t)

    def makeParentTNode(self, source_tNodes: list, node: Node, edge: Edge):
        """Creates a tNode for the next step along the edge."""
        self.search_counter += 1
        parent_val = edge.process(source_tNodes)
        if parent_val is None:
            return None
        children = source_tNodes
        cost = sum([st.cost for st in source_tNodes]) + edge.weight
        parent_t = tNode(node.label, parent_val, children, cost=cost)
        for st in source_tNodes:
            parent_t.mergeIndices(st.indices)
        parent_t.indices[node.label] += 1
        self.search_roots.append(parent_t)
        self.found_tNodes[parent_t.label].append(parent_t)
        return parent_t
                
    def selectRoot(self)-> tNode:
        """Determines the most optimal path to explore."""
        if len(self.search_roots) == 0:
            return None
        return min(self.search_roots, key=lambda t : t.cost)
    
    def getFoundValues(self, root: tNode)-> dict:
        """Returns the found values for the full search path."""
        children_tNodes = root.getDescendents()
        found = {child_t.label : list() for child_t in children_tNodes}
        for child_t in children_tNodes:
            if any((st.index == child_t.index for st in found[child_t.label])):
                continue
            found[child_t.label].append(child_t)
            found[child_t.label].sort(key=lambda st : st.index)
        values = {label : [st.value for st in sts] for label, sts in found.items()}
        return values
        
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

    def addNode(self, node: Node, value=None)-> Node:
        """Adds a node to the hypergraph via a union operation."""
        if isinstance(node, tuple):
            return None
        label = node.label if isinstance(node, Node) else node
        if label in self.nodes: 
            self.nodes[label].value = node.static_value if isinstance(node, Node) else value
            return self.nodes[label]

        label = self.requestNodeLabel(label)
        if isinstance(node, Node):
            node.label = label
        else:
            node = Node(label, value) 
            node.is_constant == value is not None
        self.nodes[label] = node
        return node

    def addEdge(self, sources: dict, target, rel, via=None, weight: float=1.0, 
                label: str=None):
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
        """
        source_nodes, source_inputs = self.getNodesAndIdentifiers(sources)
        target_nodes, target_inputs = self.getNodesAndIdentifiers([target])
        label = self.requestEdgeLabel(label, source_nodes + target_nodes)
        edge = Edge(label, source_inputs, target_nodes[0], rel, via, weight)
        self.edges[label] = edge
        for sn in source_nodes:
            sn.leading_edges.append(edge)
        for tn in target_nodes:
            tn.generating_edges.append(edge)
        return edge
    
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
                    node = self.addNode(node)
                    node_list.append(node)
                inputs[key] = node
            return node_list, inputs
        
        if not isinstance(nodes, list):
            nodes = [nodes]
        node_list = [self.addNode(n) for n in nodes]
        inputs = [self.getNode(node) for node in nodes if not isinstance(node, tuple)]
        return node_list, inputs
    
    def setNodeValues(self, node_values: dict):
        """Sets the values of the given nodes."""
        for key, value in node_values.items():
            node = self.getNode(key)
            node.static_value = value
    
    def solve(self, target, node_values: dict=None, toPrint: bool=False):
        """Runs a DFS search to identify the first valid solution for `target`."""
        self.reset()
        if node_values is not None:
            self.setNodeValues(node_values)
            source_nodes = [self.getNode(label) for label in node_values]
            source_nodes += [node for node in self.nodes.values() if node.is_constant and node.label not in node_values]
        else:
            source_nodes = [node for node in self.nodes.values() if node.is_constant]
        target_node = self.getNode(target)
        t, found_values = Pathfinder(target_node, source_nodes, self.nodes).search(toPrint)
        if toPrint and t is not None:
            print(t.printTree())
        return t, found_values
    
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
        if isinstance(node, tuple):
            return None
        t = tNode(node.label, node.static_value, join_status=join_status, trace=trace)
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
                if c_tNode is None:
                    continue
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