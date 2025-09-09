"""
Copyright 2025 John Morris

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

| File: hypergraph.py
| Author: John Morris
|   - jhmrrs@clemson.edu
|   - https://orcid.org/0009-0005-6571-1959
| Purpose: Classes for storing and traversing a constraint hypergraph.
"""

from typing import Callable, List
from inspect import signature
import logging
import itertools
from enum import Enum

logger = logging.getLogger('constrainthg')


# Helper functions
def append_to_dict_list(d: dict, key, val):
    """Appends the value to a dictionary where the dict.values are
    lists."""
    if key not in d:
        d[key] = []
    d[key].append(val)
    return d


def make_list(val) -> list:
    """Ensures that the value is a list, or else a list containing the
    value."""
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        return [val]
    try:
        return list(val)
    except TypeError:
        return [val]


def make_set(val) -> list:
    """Ensures that the value is a set, or else a set containing the
    value."""
    if isinstance(val, set):
        return val
    if isinstance(val, str):
        return {val}
    try:
        return set(val)
    except TypeError:
        return {val}


class TNode:
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

    def __init__(self, label: str, node_label: str, value=None,
                 children: list=None, cost: float=None, trace: list=None,
                 gen_edge_label: str=None, gen_edge_cost: float=0.0,
                 join_status: str='None', max_display_length: int=12):
        """
        Creates the root of a search tree.

        Parameters
        ----------
        label : str
            A unique identifier for the TNode, necessary for
            pathfinding.
        node_label : str
            A string identifying the node represented by the TNode.
        value : Any, optional
            The value of the tree solved to the TNode.
        children : list, optional
            TNodes that form the source nodes of an edge leading to the
            TNode.
        cost : float, optional
            Value indicating the cost of solving the tree rooted at the
            TNode.
        trace : list, optional
            Top down trace of how the TNode could be resolved, used for
            path exploration.
        gen_edge_label : str, optional
            A unique label for the edge generating the TNode (of which
            `children` are source nodes).
        gen_edge_cost : float, default=0.
            Value for weight (cost) of the generating edge, default is
            0.0.
        join_status : str, optional
            Indicates if the TNode is the last of a set of children,
            used for printing.
        max_display_length : int, default=12
            The maximum characters to display for the value of the node.


        Properties
        ----------
        index : int
            The maximum times the TNode or any child TNodes are repeated
            in the tree.
        values : dict
            The values of all the child TNodes of the form
            {label : [Any,]}.
        """
        self.node_label = node_label
        self.label = label
        self.value = value
        self.children = [] if children is None else children
        self.trace = [] if trace is None else trace
        self.gen_edge_label = gen_edge_label
        self.gen_edge_cost = gen_edge_cost
        self.values = {node_label: [value,]}
        self.join_status = join_status
        self.index = max([1] + [c.index for c in self.children])
        self.max_display_length = max_display_length
        self.cost = cost

    def print_conn(self, last=True) -> str:
        """Selecter function for the connector string on the tree
        print."""
        if last:
            if self.join_status == 'join':
                return self.conn.elbow_join
            if self.join_status == 'join_stop':
                return self.conn.elbow_stop
            return self.conn.elbow
        if self.join_status == 'join':
            return self.conn.tee_join
        if self.join_status == 'join_stop':
            return self.conn.tee_stop
        return self.conn.tee

    def print_tree(self, last=True, header='',
                   checked_edges: list=None) -> str:
        """Prints the tree centered at the TNode

        Adapted from https://stackoverflow.com/a/76691030/15496939,
        PierreGtch, under CC BY-SA 4.0.
        """
        out = str()
        out += header + self.print_conn(last) + str(self)
        if checked_edges is None:
            checked_edges = []
        if self.gen_edge_label in checked_edges:
            out += ' (derivative)\n' if len(self.children) != 0 else '\n'
            return out
        out += '\n'
        if self.gen_edge_label is not None:
            checked_edges.append(self.gen_edge_label)
        for i, child in enumerate(self.children):
            c_header = header + (self.conn.blank if last else self.conn.pipe)
            c_last = i == len(self.children) - 1
            out += child.print_tree(header=c_header,
                                    last=c_last,
                                    checked_edges=checked_edges)
        return out

    def get_descendents(self) -> list:
        """Returns a list of child nodes on all depths (includes
        self)."""
        out = [self]
        for c in self.children:
            out += c.get_descendents()
        return out

    @property
    def cost(self) -> float:
        """The total sum of the weights of each edge in the tree."""
        if self.calc_cost is None:
            self.calc_cost = self.get_tree_cost()
        return self.calc_cost

    @cost.setter
    def cost(self, val: float):
        """Sets the cost property of the TNode."""
        if val is None:
            self.calc_cost = self.get_tree_cost()
        elif not (isinstance(val, float) or isinstance(val, int)):
            raise TypeError("Input to cost must be float type.")
        else:
            self.calc_cost = float(val)

    @cost.deleter
    def cost(self):
        """Deletes the cost property of the TNode."""
        self.calc_cost = None

    def get_tree_cost(self, root=None, checked_edges: set=None) -> float:
        """Returns the cost of solving to the leaves of the tree."""
        if root is None:
            root = self
        if checked_edges is None:
            checked_edges = set()
        total_cost = 0
        if root.gen_edge_label not in checked_edges:
            total_cost += root.gen_edge_cost
            checked_edges.add(root.gen_edge_label)
            for st in root.children:
                total_cost += self.get_tree_cost(st, checked_edges)
        return total_cost

    def __str__(self) -> str:
        out = self.node_label
        if self.value is not None:
            if isinstance(self.value, float):
                out += f'={self.value:.4g}'[:self.max_display_length]
            else:
                out += f'={self.value}'[:self.max_display_length]
        out += f', index={self.index}'
        if self.cost is not None:
            out += f', cost={self.cost:.4g}'
        return out


class Node:
    """A value in the hypergraph, equivalent to a wired connection."""
    def __init__(self, label: str, static_value=None,
                 generating_edges: set=None,
                 leading_edges: set=None, super_nodes: set=None,
                 sub_nodes: set=None,
                 description: str=None, units: str=None):
        """Creates a new `Node` object.

        Parameters
        ----------
        label : str
            A unique identifier for the node.
        static_value : Any, optional
            The constant value of the node, set as an input.
        generating_edges : set, optional
            A set of edges that have the node as their target.
        leading_edges : set, optional
            A set of edges that have the node as one their sources.
        super_nodes : Set[Node], optional
            A set of nodes that have this node as a subset, see
            note [1].
        sub_nodes : Set[Node], optional
            A set of nodes that that have this node as a super node, see
            note [1].
        description : str, optional
            A description of the node useful for debugging.
        units : str, optional
            Units of value.
        starting_index : int, default=1
            The starting index of the node.


        Properties
        ----------
        is_constant : bool
            Describes whether the node should be reset in between
            simulations.


        Notes
        -----
        1. The subsetting accomplished by `super_nodes` is best
        conducted using `via` functions on the edge, as these will be
        executed for every node value. One case where this is impossible
        is when the node has leading edges when generated by a certain
        generating edge. In this case the `via` function cannot be used
        as the viability is *edge* dependent, not *value* dependent.
        Super nodes are provided for this purpose, though do not provide
        full functionality. When searching, the leading edges of each
        super node are added to the search queue as a valid path away
        from the node.
        """
        self.label = label
        self.static_value = static_value
        self.generating_edges = set() if generating_edges is None else generating_edges
        self.leading_edges = set() if leading_edges is None else leading_edges
        self.description = description
        self.units = units
        self.is_constant = static_value is not None
        self.super_nodes = set() if super_nodes is None else make_set(super_nodes)
        self.sub_nodes = set() if sub_nodes is None else make_set(sub_nodes)
        for sup_node in self.super_nodes:
            if not isinstance(sup_node, tuple):
                sup_node.sub_nodes.add(self)
        for sub_node in self.sub_nodes:
            if not isinstance(sub_node, tuple):
                sub_node.super_nodes.add(self)

    def __str__(self) -> str:
        out = self.label
        if self.description is not None:
            out += ': ' + self.description
        return out

    def __iadd__(self, o):
        return self.union(self, o)

    @staticmethod
    def union(a, *args):
        """Performs a deep union of the two nodes, replacing values of
        `a` with those of `b` where necessary."""
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
            a.generating_edges = a.generating_edges.union(b.generating_edges)
            a.leading_edges = a.leading_edges.union(b.leading_edges)
            a.super_nodes = a.super_nodes.union(b.super_nodes)
            a.sub_nodes = a.sub_nodes.union(b.sub_nodes)
        return a


class EdgeProperty(Enum):
    """Enumerated object describing various configurations of an Edge
    that can be passed during setup. Used as shorthand for common
    configurations.

    Members
    -------
    LEVEL : 1
        Every source node in the edge must have the same index for the
        edge to be viable.
    DISPOSE_ALL : 2
        Every source node can only be used once per execution.
    """
    LEVEL = 1
    DISPOSE_ALL = 2


class Edge:
    """A relationship along a set of nodes (the source) that produces a
    single value."""
    def __init__(self, label: str, source_nodes: dict, target: Node,
                 rel: Callable, via: Callable=None, index_via: Callable=None,
                 weight: float=1.0, index_offset: int=0, disposable: list=None,
                 edge_props: EdgeProperty=None):
        """Creates a new `Edge` object. This should generally be called
        from a Hypergraph object using the Hypergraph.addEdge method.

        Parameters
        ----------
        label : str
            A unique string identifier for the edge.
        source_nodes : dict{str : Node | Tuple(str, str)} | list[Node |
                       Tuple(str, str)] |  Tuple(str, str) | Node
            A dictionary of `Node` objects forming the source nodes of
            the edge, where the key is the identifiable label for each
            source used in rel processing. The Node object may be a Node,
            or a length-2 Tuple (identifier : attribute) with the first
            element an identifier in the edge and the second element a
            string referencing an attribute of the identified Node to
            use as the value (a pseudo node).
        target : Node
            Node that the edge maps to.
        rel : Callable
            A function taking the values of the source nodes and
            returning a single value (the target).
        via : Callable, optional
            A function that must be true for the edge to be traversable
            (viable). Defaults to unconditionally true if not set.
        index_via : Callable, optional
            A function that takes in handles of source nodes as inputs
            in reference to the *index* of each referenced source node,
            returns a boolean condition relating the indices of each.
            Defaults to unconditionally true if not set, meaning any
            index of source node is valid.
        weight : float > 0.0, default=1.0
            The quanitified cost of traversing the edge. Must be
            positive, akin to a distance measurement.
        index_offset : int, default=0
            Offset to apply to the target once solved for. Akin to
            iterating to the next level of a cycle.
        disposable : list, optional
            A list of source node handles that should not be evaluated
            for future cyclic executions of the edge. That is, each
            TNode that corresponds to a handle in `disposable` is
            removed from `found_tnodes` after a successful edge calculation.
        edge_props : List(EdgeProperty) | EdgeProperty | str | int, optional
            A list of enumerated types that are used to configure the
            edge.


        Properties
        ----------
        found_tnodes : dict
            A dict of lists of source_tnodes that are viable trees to a
            source node, with each sub_dict referenced by index. format:
            {node_label : list[TNode,]}
        subset_alt_labels : dict
            A dictionary of alternate node labels if a source node is a
            super set, format: {node_label : List[alt_node_label,]}
        """
        self.rel = rel
        self.via = self.via_true if via is None else via
        self.index_via = self.via_true if index_via is None else index_via
        self.source_nodes = self.identify_source_nodes(source_nodes, self.rel, self.via)
        self.create_found_tnodes_dict()
        self.target = target
        self.weight = abs(weight)
        self.label = label
        self.index_offset = index_offset
        self.disposable = disposable
        self.edge_props = self.setup_edge_properties(edge_props)

    def create_found_tnodes_dict(self):
        """Creates the found_tnodes dictionary, accounting for super
        nodes."""
        self.subset_alt_labels = {}
        self.found_tnodes = {}
        for sn in self.source_nodes.values():
            if not isinstance(sn, tuple):
                self.subset_alt_labels[sn.label] = []
                self.found_tnodes[sn.label] = []
                for sub_sn in sn.sub_nodes:
                    self.subset_alt_labels[sn.label].append(sub_sn.label)

    def add_source_node(self, sn):
        """Adds a source node to an initialized edge.

        Parameters
        ----------
        sn : dict | Node | Tuple(str, str)
            The source node to be added to the edge.
        """
        if isinstance(sn, dict):
            key, sn = list(sn.items())[0]
        else:
            key = self.get_source_node_identifier()
        if not isinstance(sn, tuple):
            sn.leading_edges.add(self)
            self.found_tnodes[sn.label] = []

        source_nodes = self.source_nodes | {key: sn}
        if hasattr(self, 'og_source_nodes'):
            self.og_source_nodes[key] = sn
        self.source_nodes = self.identify_source_nodes(source_nodes)
        self.edge_props = self.setup_edge_properties(self.edge_props)

    def setup_edge_properties(self, inputs: None) -> list:
        """Parses the edge properties."""
        eps = []
        if inputs is None:
            return eps
        inputs = make_list(inputs)
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
            self.handle_edge_property(ep)
        return eps

    def get_source_node_identifier(self, offset: int=0):
        """Returns a generic label for a source node."""
        return f's{len(self.source_nodes) + offset + 1}'

    def handle_edge_property(self, edge_prop: EdgeProperty):
        """Perform macro functions defined by the EdgeProperty."""
        if edge_prop is EdgeProperty.LEVEL:
            self.make_edge_level()
        elif edge_prop is EdgeProperty.DISPOSE_ALL:
            self.disposable = [key for key in self.source_nodes]

    def make_edge_level(self):
        """Adds a condition to the via function forcing all node indices
        to be equivalent."""
        if not hasattr(self, 'og_source_nodes'):
            self.og_source_nodes = dict(self.source_nodes.items())
            self.og_rel = self.rel
            self.og_via = self.via
        sns = dict(self.source_nodes.items())
        tuple_idxs = {label: el[0] for label, el in sns.items()
                      if isinstance(el, tuple)}
        for label, sn in sns.items():
            if isinstance(sn, tuple) or label in tuple_idxs.values():
                continue
            next_id = self.get_source_node_identifier()
            self.source_nodes[next_id] = (label, 'index')
            tuple_idxs[next_id] = label

        def og_kwargs(**kwargs):
            """Returns the original keywords specified when the edge was
            created."""
            return {key: kwargs[key] for key in kwargs
                    if key in self.og_source_nodes}

        def level_check(*args, **kwargs):
            """Returns true if all passed indices are equivalent."""
            if not self.og_via(*args, **kwargs):
                return False
            idxs = {val for key, val in kwargs.items() if key in tuple_idxs}
            return len(idxs) == 1

        self.via = level_check
        self.rel = lambda *args, **kwargs: self.og_rel(*args, **og_kwargs(**kwargs))

    @staticmethod
    def get_named_arguments(methods: List[Callable]) -> set:
        """Returns keywords for any keyed, required arguments
        (non-default)."""
        out = set()
        for method in methods:
            for p in signature(method).parameters.values():
                if p.kind == p.POSITIONAL_OR_KEYWORD and p.default is p.empty:
                    out.add(p.name)
        return out

    def identify_source_nodes(self, source_nodes, rel: Callable=None,
                              via: Callable=None) -> dict:
        """Returns a {str: node} dictionary where each string is the
        keyword label used in the rel and via methods."""
        if rel is None:
            rel = self.rel
        if via is None:
            via = self.via
        if isinstance(source_nodes, dict):
            return self.identify_labeled_source_nodes(source_nodes, rel, via)
        source_nodes = make_list(source_nodes)
        return self.identify_unlabeled_source_nodes(source_nodes, rel, via)

    def identify_unlabeled_source_nodes(self, source_nodes: list,
                                        rel: Callable, via: Callable) -> dict:
        """Returns a {str: node} dictionary where each string is the
        keyword label used in the rel and via methods."""
        arg_keys = self.get_named_arguments([via, rel])
        arg_keys = arg_keys.union({f's{i+1}' for i in range(len(source_nodes)
                                                            - len(arg_keys))})

        out = dict(zip(arg_keys, source_nodes))
        return out

    def identify_labeled_source_nodes(self, source_nodes: dict, rel: Callable,
                                      via: Callable) -> dict:
        """Returns a {str: node} dictionary where each string is the
        keyword label used in the rel and via methods."""
        out = {}
        arg_keys = self.get_named_arguments([rel, via])
        arg_keys = arg_keys.union({str(key) for key in source_nodes})

        for arg_key in arg_keys:
            if len(source_nodes) == 0:
                return out
            if arg_key in source_nodes:
                sn_key = arg_key
            else:
                sn_key = list(source_nodes.keys())[0]
            out[arg_key] = source_nodes[sn_key]
            del source_nodes[sn_key]

        return out

    def process(self, source_tnodes: list):
        """Processes the tnodes to get the value of the target."""
        source_vals, sourcs_idxs = self.get_source_vals_and_idxs(source_tnodes)
        target_val = self.process_values(source_vals, sourcs_idxs)
        if target_val is not None:
            self.dispose_solved_tnodes(source_tnodes)
        return target_val

    def get_source_vals_and_idxs(self, source_tnodes: list) -> tuple:
        """Returns two dictionaries mapping a source identifier with a
        value (1) or its index (2).
        """
        source_values, source_indices = {}, {}

        tuple_keys = filter(lambda key: isinstance(self.source_nodes[key], tuple),
                            self.source_nodes)
        for key in tuple_keys:
            value = self.get_psuedo_node_value(source_tnodes,
                                               *self.source_nodes[key])
            source_values[key] = value

        for st in source_tnodes:
            for key, sn in self.source_nodes.items():
                if not isinstance(sn, tuple) and st.node_label == sn.label:
                    source_values[key] = st.value
                    source_indices[key] = st.index
                    break

        return source_values, source_indices

    def get_psuedo_node_value(self, source_tnodes: list,
                              pseudo_identifier: str,
                              pseudo_attribute: str):
        """Identifies the source node and returns its attribute given by
        the pseudo-node notation.
        """
        sn_label = self.source_nodes.get(pseudo_identifier, None)
        if sn_label is None:
            return None
        sn_label = self.source_nodes[pseudo_identifier].label
        for st in source_tnodes:
            if st.node_label == sn_label:
                value = getattr(st, pseudo_attribute)
                return value
        return None

    def process_values(self, source_vals: dict,
                       source_indices: dict=None):
        """Finds the target value based on the source values and
        indices."""
        if None in source_vals:
            return None
        if source_indices is not None and not self.index_via(**source_indices):
            return None
        if self.via(**source_vals):
            return self.rel(**source_vals)
        return None

    def dispose_solved_tnodes(self, source_tnodes: list):
        """Once a TNode has been processed, it is removed from the
        `found_tnodes` list *only* if it has been marked for removal via
        inclusion in the `disposable` list.

        This ensures that nodes from previous cycles don't get
        revetted for future edges, greatly simplifying simulation.

        Process
        -------
        1. Get an identifier from the disposal list
        2. Get the label for the source node corresponding to the
        identifier
        3. Find the tnode used in the solution (from source_tnodes) with
        the matching node_label
        4. Find the set of found_tnodes from the edge corresponding to
        the node label
        5. Remove the tnode in found_tnodes with the same index as the
        solved tnode
        """
        if self.disposable is not None:
            count = 0
            for identifier in self.disposable:
                sn = self.source_nodes.get(identifier, None)
                if sn is None or isinstance(sn, tuple):
                    continue
                node_label = sn.label

                for st in source_tnodes:
                    if st.node_label == node_label:
                        index = st.index
                        break
                else:
                    continue

                count += self.dispose_of_tnodes_with_index(node_label, index)
            logger.debug(f'(Disposed of {count} nodes in {self.label})')

    def dispose_of_tnodes_with_index(self, node_label: str,
                                     index: int) -> int:
        """Removes each TNode from the edge property `found_tnodes` with
        a matching node_label and index. Returns the number of TNodes
        succesfully removed.
        """
        matching_tnodes = self.found_tnodes.get(node_label, None)
        if matching_tnodes is None:
            return 0
        matching_tnodes = [mt for mt in matching_tnodes]
        self.found_tnodes[node_label] = [t for t in matching_tnodes
                                         if t.index != index]
        return len(matching_tnodes) - len(self.found_tnodes[node_label])

    def get_source_tnode_combinations(self, t: TNode, DEBUG: bool=False):
        """Returns all viable combinations of source nodes using the
        TNode `t`."""
        if not self.add_found_tnode(t):
            return []

        st_candidates = []
        if DEBUG:
            for st_label, sts in self.found_tnodes.items():
                val_idxs = [f'{str(st.value)[:4]}({st.index})' for st in sts]
                var_info = ', '.join(val_idxs)
                msg = f' - {st_label}: ' + var_info
                logger.log(logging.DEBUG + 2, msg)

        for st_label, sts in self.found_tnodes.items():
            if st_label == t.node_label:
                st_candidates.append([t])
            elif len(sts) == 0:
                return []
            else:
                st_candidates.append(sts)

        st_combos = itertools.product(*st_candidates)
        return st_combos

    def add_found_tnode(self, t: TNode) -> bool:
        """Returns true if `t` successfully added as a viable path to a
        source node."""
        node_label = self.get_relevant_node_label(t)
        if self.check_tnode_already_found(t, node_label):
            return False
        append_to_dict_list(self.found_tnodes, node_label, t)
        return True

    def get_relevant_node_label(self, t: TNode) -> str:
        """Returns the node label of `t` or of the super set of `t`, if
        present."""
        if t.node_label not in self.found_tnodes:
            for label, sub_labels in self.subset_alt_labels.items():
                if t.node_label in sub_labels:
                    return label
        return t.node_label

    def check_tnode_already_found(self, t: TNode,
                                  source_node_label: str) -> bool:
        """Returns True if `t` has already been found as a path to the
        source node."""
        ft_labels = [ft.label for ft in self.found_tnodes[source_node_label]]
        return t.label in ft_labels

    @staticmethod
    def via_true(*args, **kwargs):
        """Returns true for all inputs (unconditional edge)."""
        return True

    def __str__(self):
        return self.label


class Pathfinder:
    """Object for searching a path through the hypergraph from a
    collection of source nodes to a single target node. If the
    hypergraph is fully constrained and viable, then the result of the
    search is a singular value of the target node."""
    def __init__(self, target: Node, sources: list, nodes: dict,
                 no_weights: bool=False, memory_mode: bool=False):
        """Creates a new Pathfinder object.

        Parameters
        ----------
        target : Node
            The Node that the Pathfinder will attempt to solve for.
        sources : list
            A list of Node objects that have static values for the
            simulation.
        nodes : dict
            A dictionary of nodes taken from the hypergraph as
            {label : Node}.
        no_weights : bool, default=False
            Optional run mode where weights aren't considered. This
            speeds up the simulation but prevents model switching.
        memory_mode : bool, default=False
            Optional run mode where all encountered TNodes are stored to
            a list property. Increases memory usage.


        Properties
        ----------
        search_counter : int
            Number of nodes explored.
        explored_edges : dict
            Dict counting the number of times edges were processed
            {label : int}.
        explored_tnodes : list
            Dict containing the all TNodes explored during searching,
            if not running in memory mode.
        """
        self.nodes = nodes
        self.source_nodes = sources
        self.target_node = target
        self.no_weights = no_weights
        self.memory_mode = memory_mode
        self.search_roots = []
        self.search_counter = 0
        self.explored_edges = {}
        self.explored_nodes = []

    def search(self, min_index: int=0, debug_nodes: list=None,
               debug_edges: list=None, search_depth: int=10000):
        """Searches the hypergraph for a path from the source nodes to the
        target node. Returns the solved TNode for the target, with a dictionary
        of found values {label : [Any,]} given by the `target.values`.

        Parameters
        ----------
        min_index : int, default=0
            Minimum index of the target node.
        debug_nodes: list, optional
            List of nodes to log additional information for.
        debug_edges : list, optional
            List of edges to log additional information for.
        search_depth : int, default=10000
            Number of TNodes to explore before search is failed.
        """
        debug_nodes = [] if debug_nodes is None else debug_nodes
        debug_edges = [] if debug_edges is None else debug_edges
        self.explored_nodes, self.explored_edges = [], {}
        logger.info(f'Begin search for {self.target_node.label}')

        for sn in self.source_nodes:
            st = TNode(f'{sn.label}#0', sn.label, sn.static_value, cost=0.)
            self.search_roots.append(st)

        while len(self.search_roots) > 0:
            if self.search_counter > search_depth:
                self.log_debugging_report()
                raise Exception("Maximum search limit exceeded.")

            labels = [f'{s.node_label}' for s in self.search_roots]
            logger.debug('Search trees: ' + ', '.join(labels))

            root = self.select_root()

            logger.debug(f'Exploring <{root.label}>, index={root.index}:')
            if self.memory_mode:
                self.explored_nodes.append(root)

            if root.node_label is self.target_node.label and root.index >= min_index:
                logger.info(f'Finished search for {self.target_node.label} with value of {root.value}')
                self.log_debugging_report()
                return root

            self.explore(root, debug_nodes, debug_edges)

        logger.info('Finished search, no solutions found')
        self.log_debugging_report()
        return None

    def explore(self, t: TNode, debug_nodes: list=None, debug_edges: list=None):
        """Discovers all possible routes from the TNode."""
        leading_edges = self.get_edges_to_explore(t, debug_nodes)
        if t.node_label in debug_nodes:
            logger.log(logging.DEBUG + 2,
                       f'Exploring {t.node_label}, index: {t.index}, '
                       + 'leading edges: '
                       + ', '.join(str(le) for le in leading_edges)
                       + f'\n{t.print_tree()}')

        for i, edge in enumerate(leading_edges):
            if edge.label not in self.explored_edges:
                self.explored_edges[edge.label] = [0, 0, 0]

            self.explored_edges[edge.label][0] += 1

            DEBUG = edge.label in debug_edges
            level = logging.DEBUG + (2 if DEBUG else 0)
            logger.log(level, f"- Edge {i}=<{edge.label}>, target=<{edge.target.label}>:")

            combos = edge.get_source_tnode_combinations(t, DEBUG)
            for j, combo in enumerate(combos):
                pt = self.make_parent_tnode(combo, edge.target, edge)
                self.explored_edges[edge.label][1] += 1
                if pt is not None:
                    self.explored_edges[edge.label][2] += 1

                node_indices = ', '.join(f'{n.label} ({n.index})' for n in combo)
                logger.debug(f'   - Combo {j}: ' + node_indices + f'-> <{str(pt)}>')

    def get_edges_to_explore(self, t: TNode, debug_nodes: list=None) -> list:
        """Finds and orders all edges leading from the node by label."""
        n = self.nodes[t.node_label]
        super_node_leading_edges = (sup_n.leading_edges for sup_n in n.super_nodes)
        leading_edges = list(n.leading_edges.union(*super_node_leading_edges))
        leading_edges.sort(key=lambda le: le.label)
        return leading_edges

    def make_parent_tnode(self, source_tnodes: list, node: Node, edge: Edge):
        """Creates a TNode for the next step along the edge."""
        parent_val = edge.process(source_tnodes)
        if parent_val is None:
            return None
        node_label = node.label
        children = source_tnodes
        gen_edge_label = edge.label + '#' + str(self.search_counter)
        label = f'{node_label}#{self.search_counter + 1}'
        cost = 0.0 if self.no_weights else None

        parent_t = TNode(label,
                         node_label,
                         parent_val,
                         children,
                         cost=cost,
                         gen_edge_label=gen_edge_label,
                         gen_edge_cost=edge.weight)
        parent_t.values = self.merge_found_values(parent_val,
                                                  node.label,
                                                  source_tnodes)
        parent_t.index += edge.index_offset

        if self.edge_resolves_input(parent_t):
            return None
        self.search_roots.append(parent_t)
        self.search_counter += 1
        return parent_t

    def edge_resolves_input(self, parent_t: TNode):
        """Returns True if the edge attempts to resolve the first index
        of an input.

        Note that inputs can be resolved as part of cycles, but only for
        later indices (2 or greater).
        """
        source_node_labels = [sn.label for sn in self.source_nodes]
        target_is_input = parent_t.node_label in source_node_labels
        resolves_input = parent_t.index == 1 and target_is_input
        return resolves_input

    def select_root(self) -> TNode:
        """Determines the most optimal path to explore."""
        if len(self.search_roots) == 0:
            return None

        min_idx = min(self.search_roots, key=lambda t: t.index).index
        lowest_idx_roots = filter(lambda t: t.index == min_idx, self.search_roots)
        root = min(lowest_idx_roots, key=lambda t: t.cost)

        self.search_roots.remove(root)
        return root

    def merge_found_values(self, parent_val, parent_label,
                           source_tnodes: list) -> dict:
        """Merges the values found in the source nodes with the parent node."""
        values = {parent_label: []}
        for st in source_tnodes:
            for label, st_values in st.values.items():
                if label not in values or len(st_values) > len(values[label]):
                    values[label] = st_values
        values[parent_label].append(parent_val)
        return values

    def log_debugging_report(self):
        """Prints a debugging report of the search."""
        out = f'\nDebugging Report for {self.target_node.label}:\n'
        out += f'\tFinal search counter: {self.search_counter}\n'
        out += '\tExplored edges (# explored | # processed | # valid solution):\n'
        sorted_edges = list(self.explored_edges.items())
        sorted_edges.sort(key=lambda a: max(a[1]), reverse=True)
        for e, vals in sorted_edges:
            out += f'\t\t<{e}>: ' + ' | '.join([str(v) for v in vals]) + '\n'
        logger.log(logging.DEBUG + 1, out)


class Hypergraph:
    """Builder class for a hypergraph. See demos for examples on how to
    use.


    Properties
    ----------
    nodes : dict
        Nodes in the hypergraph, {label : Node}
    edges : dict
        Edges in the hypergraph, {label : Edge}
    solved_tnodes : list
        List of solved TNodes from a simulation. Only set if run in
        `memory_mode`.
    no_weights : bool
        Indicates no weights have been given to the edges in the
        Hypergraph, speeding up processing (but preventing model
        switching).
    memory_mode : bool
        Indicates whether the TNodes in the Hypergraph should be saved
        between calls.
    """
    def __init__(self, no_weights: bool=False, setup_logger: bool=False,
                 logging_level=None, memory_mode: bool=False):
        """Initialize a Hypergraph.

        Parameters
        ----------
        no_weights : bool, default=False
            Optional run mode where weights aren't considered. This
            speeds up the simulation but prevents model switching.
        setup_logger : bool, default=False
            Sets up logging in the library (off by default). The logging
            level can be set by calling `Hypergraph.set_logging_level`.
        logging_level : int | str, optional
            Sets the logging level for the library. Setting the logging
            level requires an additional logging handler to be passed to
            `logger.getLogger('constrainthg')`. This can be done at the
            application level (in the calling script) or automatically
            by passing `setup_logger` as True.
        memory_mode : bool, default=False
            Store every solved for TNode to the Hypergraph.
        """
        self.nodes = {}
        self.edges = {}
        self.no_weights = no_weights
        self.logging_is_setup = self.check_if_logger_setup()
        if setup_logger:
            self.setup_logger()
        if logging_level is not None:
            self.set_logging_level(logging_level)
        self.memory_mode = memory_mode
        self.solved_tnodes = []

    def __iadd__(self, o):
        """Merges the passed Hypergraph to self via a union operation."""
        return self.union(self, o)

    def __add__(self, o):
        """Creates a shallow copy of self and joins that to ``o`` via a
        union operation."""
        if not isinstance(o, Hypergraph):
            raise Exception("Input must be of type Hypergraph.")
        new_hg = self.__copy__()
        new_hg = self.union(new_hg, o)
        return new_hg

    def __copy__(self):
        """Returns a shallow copy of the Hypergraph."""
        new_hg = Hypergraph(
            no_weights=self.no_weights,
            memory_mode=self.memory_mode,
        )
        self.union(new_hg, self)
        return new_hg
    
    def __str__(self) -> str:
        """Prints a short list of the Hypergraph."""
        out = 'Hypergraph with'
        out += f' {len(self.nodes)} nodes'
        out += f'and {len(self.edges)} edges'
        return out

    def check_if_logger_setup(self) -> bool:
        """Checks if a Handler beyond the NullHandler was created for
        the logger."""
        if not logger.hasHandlers():
            return False
        non_null = [h for h in logger.handlers
                    if not isinstance(h, logging.NullHandler)]
        return len(non_null) > 0

    def setup_logger(self) -> logging.Logger:
        """An optional call to setup logging."""
        fh = logging.FileHandler("constrainthg.log")
        log_formatter = logging.Formatter(
            fmt="[{asctime} | {levelname}]: {message}",
            style="{",
            datefmt="%Y-%m-%d %H:%M",
        )
        fh.setFormatter(log_formatter)
        logger.addHandler(fh)
        self.logging_is_setup = True
        return logger

    def set_logging_level(self, logging_level=logging.INFO):
        """Sets the logging level.

        Parameters
        ----------
        logging_level : int | str, default=logging.INFO (20)
            The level to set logging to, based on the Python logging
            library. More information is available at
            https://docs.python.org/3/howto/logging.html#logging-levels

        Notes
        -----
        The logging approach is the following, with higher levels
        include all items logged on lower ones:
        - logging.DEBUG (10): all edges and found combinations are
        listed, as well as search trees at each explored node.
        - logging.DEBUG+1 (11): debugging report is logged after a
        search is complete.
        - logging.DEBUG+2 (12): edges passed to `debug_edges` and nodes
        passed to `debug_nodes` as arguments to `Hypergraph.solve` are
        logged, as well as search trees at each explored node.
        - logging.INFO (20): start and end of a search are logged.
        - Warnings and errors are handled by the logging package
        (logging.WARNING and logging.ERROR). Note that these will *not*
        print to `sys.stderr`, though they will normally get raised and
        returned by the library.
        """
        if not self.logging_is_setup:
            self.setup_logger()
        logger.setLevel(logging_level)

    def get_node(self, node_key) -> Node:
        """Caller function for finding a node in the hypergraph."""
        if isinstance(node_key, Node):
            node_key = node_key.label
        try:
            return self.nodes[node_key]
        except KeyError:
            msg = f'No node with label <{node_key}> found in Hypergraph.'
            raise KeyError(msg)

    def get_edge(self, edge_key) -> Node:
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
        for edge in self.edges.values():
            edge.create_found_tnodes_dict()
        self.solved_tnodes = []

    def request_node_label(self, requested_label=None) -> str:
        """Generates a unique label for a node in the hypergraph"""
        label = 'n'
        if requested_label is not None:
            label = requested_label
        i = 0
        check_label = label
        while check_label in self.nodes:
            check_label = label + str(i := i + 1)
        return check_label

    def request_edge_label(self, requested_label: str=None,
                           source_nodes: list=None) -> str:
        """Generates a unique label for an edge in the hypergraph."""
        label = 'e'
        if requested_label is not None:
            label = requested_label
        elif source_nodes is not None:
            label_names = [s.label[:4] for s in source_nodes[:-1]]
            label = '(' + ','.join(label_names) + ')'
            label += '->' + source_nodes[-1].label[:8]
        i = 0
        check_label = label
        while check_label in self.edges:
            check_label = label + '#' + str(i := i + 1)
        return check_label

    def add_node(self, node=None, *args, **kwargs) -> Node:
        """Creates (if necessary) a Node and inserts into the hypergraph.

        Wraps ``Hypergraph.insert_node`` and ``Node.__init__``.

        Parameters
        ----------
        node : Node | str, optional
            The node (or node label) to add to the hypergraph. If not
            provided, then args and kwargs are passed to Node.__init__.
        """
        if node is None:
            try:
                node = Node(*args, **kwargs)
            except Exception:
                return None
        return self.insert_node(node)

    def insert_node(self, node: Node, value=None) -> Node:
        """Adds a node to the hypergraph via a union operation."""
        if isinstance(node, tuple):
            return None
        if isinstance(node, Node):
            if node.label in self.nodes:
                label = node.label
                self.nodes[label] += node
            else:
                label = self.request_node_label(node.label)
                self.nodes[label] = node
        else:
            if node in self.nodes:
                label = node
            else:
                label = self.request_node_label(node)
                self.nodes[label] = Node(label, value)
        return self.nodes[label]

    def add_edge(self, sources: dict, target, rel, via=None, index_via=None,
                 weight: float=1.0, label: str=None, index_offset: int=0,
                 disposable=None, edge_props=None):
        """Adds an edge to the hypergraph.

        Parameters
        ----------
        sources : dict{str : Node | Tuple(Node, str)} | list[Node |
                       Tuple(Node, str)] |  Tuple(Node, str) | Node
            A dictionary of `Node` objects forming the source nodes of
            the edge, where the key is the identifiable label for each
            source used in rel processing. The Node object may be a Node,
            or a length-2 Tuple with the second element a string
            referencing an attribute of the Node to use as the value (a
            pseudo node).
        targets : list | str | Node
            A list of nodes that are the target of the given edge, with
            the same type as sources. Since each edge can only have one
            target, this makes a unique edge for each target.
        rel : Callable
            A function taking in a value for each source node that
            returns a single value for the target.
        via : Callable, optional
            A function that must be true for the edge to be traversable
            (viable). Defaults to unconditionally true if not set.
        index_via : Callable, optional
            A function that takes in handles of source nodes as inputs
            in reference to the *index* of each referenced source node,
            returns a boolean condition  relating the indices of each.
            Defaults to unconditionally true if not set, meaning any
            index of source node is valid.
        weight : float, default=1.0
            The cost of traversing the edge. Must be positive.
        label : str, optional
            A unique identifier for the edge.
        index_offset : int, default=0
            Offset to apply to the target once solved for. Akin to
            iterating to the next level of a cycle.
        disposable : list, optional
            A list of source node handles that should not be evaluated
            for future cyclic executions of the edge. That is, each
            tnode that corresponds to a handle in `disposable` is
            removed from `found_tnodes` after a successful edge
            calculation.
        edge_props : List(EdgeProperty) | EdgeProperty | str | int, optional
            A list of enumerated types that are used to configure the
            edge.
        """
        source_nodes, source_inputs = self.get_nodes_and_identifiers(sources)
        target_nodes, target_inputs = self.get_nodes_and_identifiers([target])
        label = self.request_edge_label(label, source_nodes + target_nodes)
        edge = Edge(label, source_inputs, target_nodes[0],
                    rel, via, index_via, weight,
                    index_offset=index_offset, disposable=disposable,
                    edge_props=edge_props)
        self.edges[label] = edge
        for sn in source_nodes:
            sn.leading_edges.add(edge)
        for tn in target_nodes:
            tn.generating_edges.add(edge)
        return edge

    def insert_edge(self, edge: Edge):
        """Inserts a fully formed edge into the hypergraph."""
        if not isinstance(edge, Edge):
            raise TypeError('edge must be of type `Edge`')
        self.edges[edge.label] = edge
        tn = self.insert_node(edge.target)
        tn.generating_edges.add(edge)

    @staticmethod
    def union(a, *args):
        """Merges with another Hypergraph via a union operation,
        preserving all nodes and edges in the two graphs.
        """
        if not isinstance(a, Hypergraph):
            raise Exception('Input must by of type Hypergraph.')
        for b in args:
            if not isinstance(b, Hypergraph):
                raise Exception('Parameters are not of type Hypergraph.')
            for node in b.nodes.values():
                a.insert_node(node)
            for edge in b.edges.values():
                a.insert_edge(edge)
            a_tns = set(a.solved_tnodes).union(set(b.solved_tnodes))
            a.solved_tnodes = list(a_tns)
        return a

    def get_nodes_and_identifiers(self, nodes):
        """Helper function for getting a list of nodes and their
        identified argument format for various input types."""
        if isinstance(nodes, dict):
            node_list, inputs = [], {}
            for key, node in nodes.items():
                if isinstance(node, tuple):
                    if node[0] not in nodes:
                        raise Exception(f"Pseudo node identifier for '{node[0]}' not included in Edge.")
                else:
                    node = self.insert_node(node)
                    node_list.append(node)
                inputs[key] = node
            return node_list, inputs

        nodes = make_list(nodes)
        node_list = [self.insert_node(n) for n in nodes]
        inputs = [self.get_node(node) for node in nodes
                  if not isinstance(node, tuple)]
        return node_list, inputs

    def set_node_values(self, node_values: dict):
        """Sets the values of the given nodes.

        Creates a new node in the hypergraph if the given label is not
        found.
        """
        for key, value in node_values.items():
            try:
                node = self.get_node(key)
            except KeyError:
                node = self.insert_node(key, value)
            node.static_value = value

    def solve(self, target, inputs: dict=None, to_print: bool=False,
              min_index: int=0, debug_nodes: list=None, debug_edges: list=None,
              search_depth: int=100000, memory_mode: bool=False,
              logging_level=None, to_reset: bool=True):
        """Runs a BFS search to identify the first valid solution for
        `target`.

        Parameters
        ----------
        target : Node | str
            The node or label of the node to solve for.
        inputs : dict, optional
            A dictionary {label : value} of input values.
        to_print : bool, default=False
            Prints the search tree if set to true.
        min_index : int, default=0
            The minumum index of the node to solve for.
        debug_nodes : List[label,], optional
            A list of node labels to log debugging information for.
        debug_edges : List[label,], optional
            A list of edge labels to log debugging information for.
        search_depth : int, default=100000
            Number of nodes to explore before concluding no valid path.
        memory_mode : bool, default=False
            Found TNodes in the path are saved to the Hypergraph.
        logging_level : int | str, optional
            The logging level to use for the simulation. Configures
            logging if not already configured. `logging.DEBUG` or
            `logging.INFO` are informative levels. See
            `Hypergraph.set_logging_level` for more information.
        to_reset : bool, default=True
            Resets the Hypergraph so that only nodes with static values
            are preseeded. Should be `True` for independent simulations,
            `False` for repeated simulations of different values from
            the same scenario.

        Returns
        -------
        TNode | None
            the TNode for the minimum-cost path found
        dict | None
            a dictionary of values found for each node in the search
            path, as {label : List[value,]}
        """
        if logging_level is not None:
            prev_logging_level = logger.getEffectiveLevel()
            self.set_logging_level(logging_level)
        if to_reset:
            self.reset()

        inputs = {} if inputs is None else inputs
        self.set_node_values(inputs)
        source_nodes = self.process_source_nodes(inputs)

        try:
            target_node = self.get_node(target)
        except KeyError:
            msg = f'Target node {str(target)} not found in Hypergraph.'
            raise KeyError(msg)

        pf = Pathfinder(
            target=target_node,
            sources=source_nodes,
            nodes=self.nodes,
            no_weights=self.no_weights,
            memory_mode=self.memory_mode or memory_mode,
        )
        try:
            t = pf.search(
                min_index=min_index,
                debug_nodes=debug_nodes,
                debug_edges=debug_edges,
                search_depth=search_depth,
            )
            if self.memory_mode or memory_mode:
                self.solved_tnodes = pf.explored_nodes
        except Exception as e:
            logger.error(str(e))
            raise e
        finally:
            if logging_level is not None:
                self.set_logging_level(prev_logging_level)
        if to_print:
            print("No solutions found" if t is None else t.print_tree())
        return t

    def process_source_nodes(self, inputs):
        """Processes source nodes for the simulation."""
        source_nodes = []
        for label in inputs:
            try:
                source_nodes.append(self.get_node(label))
            except KeyError:
                msg = f'Input node <{label}> not found in Hypergraph.'
                raise KeyError(msg)
        source_nodes += self.get_constant_nodes(inputs)
        return source_nodes

    def get_constant_nodes(self, inputs: list=None):
        """Returns all the constant nodes in the Hypergraph, optionally
        filtered by nodes not in `inputs`."""
        if inputs is None:
            inputs = []
        constant_nodes = [node for node in self.nodes.values()
                          if node.is_constant and node.label not in inputs]
        return constant_nodes

    def print_paths(self, target, to_print: bool=False) -> str:
        """Prints the hypertree of all paths to the target node."""
        try:
            target_node = self.get_node(target)
        except KeyError:
            msg = f'Target node {str(target)} not found in Hypergraph.'
            raise KeyError(msg)
        target_tnode = self.print_paths_helper(target_node)
        out = target_tnode.print_tree()
        if to_print:
            print(out)
        return out

    def print_paths_helper(self, node: Node, join_status='none',
                           trace: list=None) -> TNode:
        """Recursive helper to print all paths to the target node."""
        if isinstance(node, tuple):
            return None
        label = f'{node.label}#{0 if trace is None else len(trace)}'
        t = TNode(label, node.label, node.static_value,
                  join_status=join_status, trace=trace)
        branch_costs = []
        for edge in node.generating_edges:
            if self.edge_in_cycle(edge, t):
                t.node_label += '[CYCLE]'
                return t

            child_cost = 0
            for i, child in enumerate(edge.source_nodes.values()):
                c_join_status = self.get_join_status(i, len(edge.source_nodes))
                c_trace = t.trace + [(t, edge)]
                c_tnode = self.print_paths_helper(child, c_join_status, c_trace)
                if c_tnode is None:
                    continue
                child_cost += c_tnode.cost if c_tnode.cost is not None else 0.0
                t.children.append(c_tnode)
            branch_costs.append(child_cost + edge.weight)

        t.cost = min(branch_costs) if len(branch_costs) > 0 else 0.
        return t
    
    def print_nodes(self) -> str:
        out = 'Nodes in Hypergraph:'
        out += ''.join([f'\n - {n}' for n in self.nodes.values()])
        return out
        
    def edge_in_cycle(self, edge: Edge, t: TNode):
        """Returns true if the edge is part of a cycle in the tree rooted at
        the TNode."""
        return edge.label in [e.label for tt, e in t.trace]

    def get_join_status(self, index, num_children):
        """Returns whether or not the node at the given index is part of a
        hyperedge (`join`) or specifically the last node in a hyperedge
        (`join_stop`) or a singular edge (`none`)"""
        if num_children > 1:
            return 'join_stop' if index == num_children - 1 else 'join'
        return 'none'
