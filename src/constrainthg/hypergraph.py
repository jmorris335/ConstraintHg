from src.constrainthg.CONTROL import CYCLE_SEARCH_DEPTH

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

    def printConn(self, last=True):
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

    def printTree(self, last=True, header=''):
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
    
    def __str__(self):
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

    def solveValue(self, t: tNode):
        """Recursively solve for the value of the node."""
        if self.value is not None:
            return self.value, t
        self.value, t = self.findOptimalEdge(t)
        return self.value, t
    
    def findOptimalEdge(self, t: tNode):
        """Returns the best possible edge found from an exhuastive search."""
        candidate_edges = dict()
        for edge in self.generating_edges:
            value, t = edge.solveValue(t)
            self.is_simulated = True
            if value is None:
                continue
            if t.cost is None:
                return value, t
            candidate_edges[t.cost] = (value, t)
        if len(candidate_edges) == 0:
            return None, t
        return candidate_edges[min(candidate_edges.keys())]
        
    def __str__(self)-> str:
        out = self.label
        if self.description is not None:
            out += ': ' + self.description
        return out

class Edge:
    def __init__(self, source_nodes: list, rel, via=None, weight: float=0.0):
        self.source_nodes = source_nodes
        self.rel = rel
        self.via = self.via_true if via is None else via
        self.weight = weight

    def solveValue(self, t: tNode):
        """Recursively solves for the value of target node."""
        child_values = list()
        sub_p_list = list()

        for source_node in self.source_nodes:
            source_tNode = tNode(source_node.label, join_status='none')
            if self in t.trace:
                pass
                # node_value, sub_tNode = self.solveCycle(node, t)
            else:
                node_value, source_tNode = source_node.solveValue(source_tNode)
            if node_value is None:
                return None, t
            child_values.append(node_value)
            sub_p_list.append(source_tNode)
        
        target_val = self.process(child_values)
        t = self.prepareTNode(t, target_val, sub_p_list)
        return target_val, t
    
    def prepareTNode(self, t: tNode, value, child_tNodes: list):
        """Preps the tree node recording the edge traversal."""
        if value is not None and t is not None:
            t.cost = self.calculateCost(child_tNodes)
            t.value = value
            t.children = child_tNodes
            t.trace = t.trace + [self]
        return t
    
    def calculateCost(self, source_tNodes: list):
        """Calculates the cost of traversing the edge including solving for the costs of each source node"""
        child_costs = [c.cost if c.cost is not None else 0.0 for c in source_tNodes]
        cost = sum(child_costs) + self.weight
        return cost

    def process(self, source_vals):
        """Finds the target value based on the source values."""
        if None in source_vals:
            return None
        if self.via(*source_vals):
            return self.rel(*source_vals)
        else:
            return None
        
    def solveCycle(self, t: tNode, exit: Node):
        """Returns the maximally preferential n-cycle path in a loop."""
        cycle_nodes = t.trace[t.trace.index(t.label):]
        enter_nodes = self.findCycleEnterNodes(cycle_nodes)
        for enter in enter_nodes:
            value, cost = self.findBestNpath(enter, exit, cycle_nodes)

    def findCycleEnterNodes(self, cycle_nodes)-> list:
        """Returns a list of nodes that serve as entry points for a cycle (defined as node in the cycle pointed to by an edge
        with only non-cyclical nodes as its source)."""
        num_shared_nodes = lambda edge : len(set(s.label for s in edge.source_nodes).intersection(cycle_nodes))
        enter_nodes = list()
        for c_node in cycle_nodes:
            for edge in c_node.generating_edges:
                if num_shared_nodes(edge) == 0:
                    enter_nodes.append(c_node)
        return enter_nodes
    
    def findBestNpath(self, cycle_nodes: list, cycle_edges: list):
        """Finds the best n-cycle path between the enter and exit point by cost."""
        n = 0
        while n < CYCLE_SEARCH_DEPTH:
            for edge in cycle_edges:
                target_node = Node()
                source_vals = self.getSourceValues()
                target_val = self.process(source_vals)
                if target_val is None:
                    return None
                target_node.setValue(target_val)
            if cycle_edges[-1].via():
                return n
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
        self.edges = list()

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

    def generateNodeLabel(self)-> str:
        """Generates a label for a node in the hypergraph."""
        return f'n{(len(self.nodes) + 1)}'

    def getNodeLabel(self, requested_label=None)-> str:
        """Generates a unique label for a node in the hypergraph"""
        if requested_label is None:
            return self.generateNodeLabel()
        if requested_label in self.nodes:
            return self.getNodeLabel(requested_label + self.generateNodeLabel())
        return requested_label

    def addNode(self, node: Node, value=None)-> Node:
        """Adds a node to the hypergraph via a union operation."""
        label = node.label if isinstance(node, Node) else node
        if label in self.nodes: #Return node if node in hypergraph
            self.nodes[label].value = node.value if isinstance(node, Node) else value
            return self.nodes[label]

        label = self.getNodeLabel(label) #Get unique label
        if isinstance(node, Node):
            node.label = label
        else:
            node = Node(label, value) 
        self.nodes[label] = node
        return node

    def addEdge(self, sources: list, targets: list, rel, via=None, weight: float=1.0):
        """Adds an edge to the hypergraph"""
        if not isinstance(sources, list):
            sources = [sources]
        if not isinstance(targets, list):
            targets = [targets]
        source_nodes = [self.addNode(source) for source in sources]
        target_nodes = [self.addNode(target) for target in targets]
        edge = Edge(source_nodes, rel, via, weight)
        self.edges.append(edge)
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
        t = tNode(target_node.label) if toPrint else None
        target_val, t = target_node.solveValue(t)
        if toPrint:
            print(t.printTree())
        return target_val
    
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