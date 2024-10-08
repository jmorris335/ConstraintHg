class pNode:
    """A basic tree node for printing tree structures."""
    elbow = "└──"
    pipe = "│  "
    tee = "├──"
    blank = "   "

    def __init__(self, label, children: list=None):
        self.label = label
        self.children = list() if children is None else children

    def __str__(self, last=True, header=''):
        """Prints the tree centered at the pNode
        
        Adapted from https://stackoverflow.com/a/76691030/15496939, PierreGtch, 
        under CC BY-SA 4.0
        """
        out = str()
        out += header + (self.elbow if last else self.tee) + self.label + '\n'
        for i, child in enumerate(self.children):
            c_header = header + (self.blank if last else self.pipe)
            c_last = i == len(self.children) - 1
            out += child.__str__(header=c_header, last=c_last)
        return out

class Node:
    def __init__(self, label=str, value=None, generating_edges: list=None):
        self.label = label
        self.value = value
        self.generating_edges = list() if generating_edges is None else generating_edges 

    def solveValue(self, p: pNode=None):
        """Recursively solve for the value of the node."""
        if self.value is not None:
            return self.value, p
        for edge in self.generating_edges:
            self.value, p = edge.solveValue(p)
            if self.value is not None:
                return self.value, p
        return None, p
        
    def __str__(self):
        return self.label

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
            sub_node_p = pNode(node.label)
            node_value, sub_node_p = node.solveValue(sub_node_p)
            if node_value is None:
                return None, p
            child_values.append(node_value)
            sub_p_list.append(sub_node_p)
        target_val = self.process(child_values)
        if target_val is not None and p is not None:
            p.children = sub_p_list
        return target_val, p

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

    def addNode(self, node: Node=None, value=None)-> Node:
        """Adds a node to the hypergraph via a union operation."""
        label = node.label if isinstance(node, Node) else node
        if label in self.nodes: #Return node if node in hypergraph
            self.nodes[label].value = value
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
            self.nodes[key].value = node_values[key]
    
    def DFS(self, node_values: dict, target, toPrint: bool=False):
        """Runs a DFS search to identify the first valid solution for `target`."""
        if toPrint:
            p = pNode(target)
        else:
            p = None
        self.setNodeValues(node_values)
        target_val, p = self.nodes[target].solveValue(p)
        if toPrint:
            print(p)
        return target_val
    

if __name__ == '__main__':
    def rel_sum(*source):
        return sum(source)
    
    def rel_increment(*source):
        return source[0] + 1

    Hg = Hypergraph()
    ab = Hg.addEdge('A', 'B', rel_increment)
    cb = Hg.addEdge('A', 'C', rel_increment)
    # bd = Hg.addEdge('B', 'D', rel_increment)
    bce = Hg.addEdge(['B', 'C'], 'E', rel_increment)
    cg = Hg.addEdge('C', 'G', rel_increment)
    ed = Hg.addEdge('E', 'D', rel_increment)
    di = Hg.addEdge('D', 'I', rel_increment)
    ij = Hg.addEdge('I', 'J', rel_increment)
    # jt = Hg.addEdge('J', 'T', rel_increment)
    edh = Hg.addEdge(['E', 'D'], 'H', rel_increment)
    hj = Hg.addEdge('H', 'J', rel_increment)
    hg = Hg.addEdge('H', 'G', rel_increment)
    ht = Hg.addEdge('H', 'T', rel_increment)
    gt = Hg.addEdge('G', 'T', rel_increment)

    # jt.via = lambda *source : False
    # bd.via = lambda *source : False
    # cg.via = lambda *source : False

    inputs = {'A': 1}
    Tval = Hg.DFS(inputs, 'T', toPrint=True)

    print(f'T = {Tval}')