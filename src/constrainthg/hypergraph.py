from src.constrainthg.CONTROL import CYCLE_SEARCH_DEPTH
from typing import Callable, Tuple, Any

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
    
    def __init__(self, label, value=None, children: list=None, join_status: str='None', cost: float=None, trace: list=None):
        self.label = label
        self.value = value
        self.children = list() if children is None else children
        self.join_status = join_status
        self.cost = cost
        self.trace = list() if trace is None else trace
        """List of edges for which the node is a leaf for."""

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
        under CC BY-SA 4.0
        """
        out = str()
        out += header + self.printConn(last) + self.__str__() + '\n'
        for i, child in enumerate(self.children):
            c_header = header + (self.conn.blank if last else self.conn.pipe)
            c_last = i == len(self.children) - 1
            out += child.printTree(header=c_header, last=c_last)
        return out
    
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
    
class Cycle:
    def __init__(self):
        pass

    def solveCycle(self, t: tNode, last_edge_label: str)-> tNode:
        """Returns the maximally preferential n-cycle path in a loop."""
        start_index = [e.label for e in t.trace].index(last_edge_label)
        cycle_edges = t.trace[start_index:-1]
        cycle_nodes = self.findCycleNodes(cycle_edges)
        exit_edge, exit_node = t.trace[start_index-1], cycle_nodes[-1] #TODO: Check that exit_node is a source for exit_edge
        enter_points = self.findCycleEnterPoints(cycle_nodes)
        cycle_node_labels = [c.label for c in cycle_nodes]

        exit_tNodes = list()
        for enter_node, enter_edge in enter_points:
            enter_tNode = tNode(enter_node.label, join_status='none')
            enter_tNode = enter_edge.solveValue(enter_tNode)
            cycle_tNodes= [enter_tNode]
            
            # Find n-cycle
            num_iter = 1
            i = -1
            while num_iter < CYCLE_SEARCH_DEPTH:
                # Solve the source values for the cycle node
                edge = cycle_edges[i % len(cycle_edges)]
                target_tNode = tNode(label=cycle_nodes[(i-1) % len(cycle_nodes)].label, join_status='none')

                source_tNodes = list()
                for s in edge.source_nodes: #Make sure all source nodes are solved for.
                    if s in cycle_nodes: #Find latest t-node for the source
                        for ct in cycle_tNodes[::-1]:
                            if ct.label == s.label:
                                source_tNodes.append(ct)
                                break
                    else: #Solve any non-cyclical nodes recursively
                        source_tNodes.append(s.solveValue())

                source_values = [st.value for st in source_tNodes]

                # Check if the cycle can be exited
                if target_tNode.label == exit_node.label:
                    if exit_edge.via(*source_values):
                        target_tNode.value = exit_edge.process(source_values)
                        if target_tNode.value is None:
                            return None
                        target_tNode = edge.prepareTNode(target_tNode, target_tNode.value, source_tNodes)
                        exit_tNodes.append(target_tNode)
                        break

                # Save the progress through the cycle
                target_tNode.value = edge.process(source_values)
                if target_tNode.value is None:
                    return None
                target_tNode = edge.prepareTNode(target_tNode, target_tNode.value, source_tNodes)
                cycle_tNodes.append(target_tNode)
                num_iter += 1
                i -= 1
        
        # Find the tNode corresponding to the best n-cycle path
        best_exit_t = None
        for exit_t in exit_tNodes:
            if best_exit_t is None or (exit_t.cost is not None and exit_t.cost < best_exit_t.cost):
                best_exit_t = exit_t

        # Retreat down 1 iteration to where the cycle was entered
        def searchChildren(cycle_tNode: tNode, search_label: str, isFirst: bool=True):
            for child in cycle_tNode.children:
                if child.label == search_label:
                    if isFirst:
                        return searchChildren(child, search_label, isFirst=False)
                    return child
                if child.label in cycle_node_labels:
                    return searchChildren(child, search_label, isFirst)
            return None
        
        t = searchChildren(best_exit_t, t.label)
            
        return t
    
    def findCycleNodes(self, cycle_edges: list)-> list:
        """Returns a list of nodes comprising the given cycle."""
        cycle_nodes = list()
        edges = cycle_edges + [cycle_edges[0]]
        for i in range(len(cycle_edges)):
            e1, e2 = edges[i:i+2]
            for s in e1.source_nodes:
                if e2 in s.generating_edges:
                    cycle_nodes.append(s)
                    break
        return cycle_nodes

    def findCycleEnterPoints(self, cycle_nodes: list)-> list:
        """Returns a list of (node, edge) tuples that each serve as entry points for a cycle."""
        num_shared_nodes = lambda edge : len(set(s.label for s in edge.source_nodes).intersection(c.label for c in cycle_nodes))
        enter_points = list()
        for n in cycle_nodes:
            for e in n.generating_edges:
                if num_shared_nodes(e) == 0:
                    enter_points.append((n, e))
        return enter_points
    
    def findBestNpath(self, cycle_nodes: list, cycle_edges: list):
        """Finds the best n-cycle path between the enter and exit point by cost."""
        n = 0
        while n < CYCLE_SEARCH_DEPTH:
            for edge in cycle_edges:
                target_node = Node()
                source_vals = self.solveSourceNodes()
                target_val = self.process(source_vals)
                if target_val is None:
                    return None
                target_node.setValue(target_val)
            if cycle_edges[-1].via():
                return n
        return None

class Node:
    def __init__(self, label: str, value=None, generating_edges: list=None, description: str=None):
        self.label = label
        self.value = value
        self.generating_edges = list() if generating_edges is None else generating_edges
        self.description = description
        self.is_simulated = False
        """Marker saying that the value was artificially generated (used for resetting the Node after a simulation)."""

    def setValue(self, value, is_simulated: bool=True):
        """Sets the value for the node"""
        self.value = value
        self.is_simulated = is_simulated

    def solveValue(self, t: tNode)-> tNode:
        """Recursively solve for the value of the node."""
        if self.value is not None:
            t.value = self.value
            return t
        t = self.findOptimalEdge(t)
        self.value = t.value
        return t
    
    def findOptimalEdge(self, t: tNode):
        """Returns the best possible edge found from an exhuastive search."""
        candidate_edges = dict()
        for edge in self.generating_edges:
            t = edge.solveValue(t)
            self.is_simulated = True
            if t.value is None:
                continue
            if t.cost is None:
                return t
            candidate_edges[t.cost] = t
        if len(candidate_edges) == 0:
            return None, t
        return candidate_edges[min(candidate_edges.keys())]
        
    def __str__(self)-> str:
        out = self.label
        if self.description is not None:
            out += ': ' + self.description
        return out

class Edge:
    """A relationship along a set of nodes (the source) that produces a single value (the target)."""
    def __init__(self, label: str, source_nodes: list, rel: Callable, via: Callable=None, weight: float=0.0):
        self.source_nodes = source_nodes
        """List of Node objects."""
        self.rel = rel
        """Method for calculating the target value from the `source_nodes`"""
        self.via = self.via_true if via is None else via
        """Method for determining if the edge is viable."""
        self.weight = abs(weight)
        """Cost of traversing the edge."""
        self.label = label

    def solveValue(self, t: tNode)-> tNode:
        """Recursively solves for the value of target node."""
        source_tNodes = self.solveSourceNodes(t)
        if source_tNodes is None:
            return None, t
        
        source_values = [st.value for st in source_tNodes]
        target_val = self.process(source_values)
        t = self.prepareTNode(t, target_val, source_tNodes)
        return t
    
    def solveSourceNodes(self, t: tNode)-> list:
        """Returns the solved tNodes for each source node in the edge."""
        source_tNodes = list()

        for source_node in self.source_nodes:
            source_tNode = tNode(source_node.label, join_status='none')
            source_tNode.trace = t.trace + [self]
            if self.label in [e.label for e in t.trace[:-1]]:
                cycle = Cycle()
                source_tNode = cycle.solveCycle(source_tNode, self.label)
            else:
                source_tNode = source_node.solveValue(source_tNode)
            if source_tNode.value is None:
                return None
            source_tNodes.append(source_tNode)

        return source_tNodes
    
    def prepareTNode(self, t: tNode, value, source_tNodes: list)-> tNode:
        """Preps the tree node recording the edge traversal."""
        if value is not None and t is not None:
            t.cost = self.calculateCost(source_tNodes)
            t.value = value
            t.children = source_tNodes
        return t
    
    def calculateCost(self, source_tNodes: list)-> float:
        """Calculates the cost of traversing the edge including solving for the costs of each source node"""
        child_costs = [c.cost if c.cost is not None else 0.0 for c in source_tNodes]
        cost = sum(child_costs) + self.weight
        return cost

    def process(self, source_vals: list)-> float:
        """Finds the target value based on the source values."""
        if None in source_vals:
            return None
        if self.via(*source_vals):
            return self.rel(*source_vals)
        else:
            return None
            
    @staticmethod
    def via_true(*source):
        """Returns true for all inputs (unconditional edge)."""
        return True
    
class Hypergraph:
    """Builder class for a hypergraph."""
    def __init__(self):
        """Initialize a Hypergraph."""
        self.nodes = dict()
        self.edges = dict()

    def getNode(self, node_key):
        """Caller function for finding a node in the hypergraph."""
        if isinstance(node_key, Node):
            node_key = node_key.label
        try:
            return self.nodes[node_key]
        except:
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
        if label in self.nodes: #Return node if node in hypergraph
            self.nodes[label].value = node.value if isinstance(node, Node) else value
            return self.nodes[label]

        label = self.requestNodeLabel(label) #Get unique label
        if isinstance(node, Node):
            node.label = label
        else:
            node = Node(label, value) 
        self.nodes[label] = node
        return node

    def addEdge(self, sources: list, targets: list, rel, via=None, weight: float=1.0, label: str=None):
        """Adds an edge to the hypergraph."""
        if not isinstance(sources, list):
            sources = [sources]
        if not isinstance(targets, list):
            targets = [targets]
        source_nodes = [self.addNode(source) for source in sources]
        target_nodes = [self.addNode(target) for target in targets]
        label = self.requestEdgeLabel(label, source_nodes + target_nodes)
        edge = Edge(label, source_nodes, rel, via, weight)
        self.edges[label] = edge
        for target in target_nodes:
            target.generating_edges.append(edge)
        return edge
    
    def setNodeValues(self, node_values: dict):
        """Sets the values of the given nodes."""
        for key in node_values:
            node = self.getNode(key)
            node.value = node_values[key]
    
    def solve(self, target, node_values: dict=None, toPrint: bool=False):
        """Runs a DFS search to identify the first valid solution for `target`."""
        self.reset()
        if node_values is not None:
            self.setNodeValues(node_values)
        target_node = self.getNode(target)
        t = tNode(target_node.label)
        t = target_node.solveValue(t)
        if toPrint:
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

    def printPathsHelper(self, node: Node, join_status='none')-> tNode:
        """Recursive helper to print all paths to the target node."""
        t = tNode(node.label, node.value, join_status=join_status)
        branch_costs = list()
        for edge in node.generating_edges:
            child_cost = 0
            for i, child in enumerate(edge.source_nodes):
                c_join_status = self.getJoinStatus(i, len(edge.source_nodes))
                c_tNode = self.printPathsHelper(child, c_join_status)
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