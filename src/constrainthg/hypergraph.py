class pNode:
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
    
    def __init__(self, label, value=None, children: list=None, join_status: str='None', cost: float=None):
        self.label = label
        self.value = value
        self.children = list() if children is None else children
        self.join_status = join_status
        self.cost = cost

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
        """Prints the tree centered at the pNode
        
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

    def solveValue(self, p: pNode=None):
        """Recursively solve for the value of the node."""
        if self.value is not None:
            return self.value, p
        for edge in self.generating_edges:
            self.value, p = edge.solveValue(p)
            self.is_simulated = True
            if self.value is not None:
                return self.value, p
        return None, p
        
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

    def solveValue(self, p: pNode=None):
        """Recursively solves for the value of target node."""
        child_values = list()
        sub_p_list = list()

        for node in self.source_nodes:
            node_value, sub_pNode = self.getSourceValues(node)
            if node_value is None:
                return None, p
            child_values.append(node_value)
            sub_p_list.append(sub_pNode)
        
        target_val = self.process(child_values)
        p = self.preparePNode(p, target_val, sub_p_list)
        return target_val, p
    
    def getSourceValues(self, node):
        """Calculates the value of the node (recursive helper)."""
        sub_pNode = pNode(node.label, join_status='none')
        node_value, sub_pNode = node.solveValue(sub_pNode)
        if node_value is None:
            return None, None
        sub_pNode.value = node_value
        return node_value, sub_pNode
    
    def preparePNode(self, p: pNode, value, child_pNodes: list):
        if value is not None and p is not None:
            child_costs = [c.cost if c.cost is not None else 0.0 for c in child_pNodes]
            p.cost = sum(child_costs) + self.weight
            p.value = value
            p.children = child_pNodes
        return p

    def process(self, source_vals):
        '''Finds the target value based on the source values.'''
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
    
    def solve(self, node_values: dict, target, toPrint: bool=False):
        """Runs a DFS search to identify the first valid solution for `target`."""
        self.reset()
        self.setNodeValues(node_values)
        target_node = self.getNode(target)
        p = pNode(target_node.label) if toPrint else None
        target_val, p = target_node.solveValue(p)
        if toPrint:
            print(p.printTree())
        return target_val
    
    def printPaths(self, target, toPrint: bool=True)-> str:
        """Prints the hypertree of all paths to the target node."""
        target_node = self.getNode(target)
        target_pNode = self.printPathsHelper(target_node)
        out = target_pNode.printTree()
        if toPrint:
            print(out)
        return out

    def printPathsHelper(self, node: Node, join_status='none')-> pNode:
        """Recursive helper to print all paths to the target node."""
        p = pNode(node.label, node.value, join_status=join_status)
        for edge in node.generating_edges:
            for i, child in enumerate(edge.source_nodes):
                if len(edge.source_nodes) > 1:
                    c_join_status = 'join_stop' if i == len(edge.source_nodes) - 1 else 'join'
                else:
                    c_join_status = 'none'
                p.children.append(self.printPathsHelper(child, c_join_status))
            child_costs = [c.cost if c.cost is not None else 0.0 for c in p.children]
            p.cost = sum(child_costs) + edge.weight
        return p
    
    def __str__(self)-> str:
        return