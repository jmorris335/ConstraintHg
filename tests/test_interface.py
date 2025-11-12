from constrainthg.hypergraph import Hypergraph, Node
from constrainthg import relations as R

import logging
import pytest

class TestHypergraphInterface:
    def test_pseudonodes(self):
        """Test pseudonode functionality."""
        hg = Hypergraph()
        hg.add_edge('A', 'B', R.Rfirst, weight=5)
        hg.add_edge({'b':'B', 'b_pseudo':('b', 'index')}, 'Index', R.equal('b_pseudo'))
        hg.add_edge({'b':'B', 'b_pseudo':('b', 'cost')}, 'Cost', R.equal('b_pseudo'))
        b = hg.solve('B', {'A': 20})
        assert b.value == 20, "Solution not correctly identified."
        index = hg.solve('Index', {'A': 20})
        assert index.value == 1, "Index not correctly identified."
        cost = hg.solve('Cost', {'A': 20})
        assert cost.value == 5, "Cost not correctly identified."

    def test_no_weights(self):
        """Tests a hypergraph with no weights set."""
        hg = Hypergraph(no_weights=True)
        hg.add_edge(['A', 'B'], 'C', R.Rsum, weight=10.)
        t = hg.solve('C', {'A': 100, 'B': 12.9},)
        assert t.cost == 0.0, "Cost should be 0.0 for no_weights test"

    def test_retain_previous_indices(self):
        """Tests whether a solution can be found by combining any previously found
        source nodes (of any index). The default behavior without disposal."""
        def negate(s: bool)-> bool:
            return not s

        hg_no_disposal = Hypergraph()
        hg_no_disposal.add_edge('SA', 'A', R.Rmean)
        hg_no_disposal.add_edge('SB', 'B', R.Rmean)
        hg_no_disposal.add_edge('A', 'A', negate, index_offset=1)
        hg_no_disposal.add_edge('B', 'B', negate, index_offset=1)
        hg_no_disposal.add_edge({'a':'A', 'b':'B'}, 'C', lambda a, b : a and b)
        hg_no_disposal.add_edge('C', 'T', R.Rmean, via=lambda c : c is True)
        t = hg_no_disposal.solve('T', {'SA': True, 'SB': False})
        assert t.value == True, "Solver did not appropriately combine previously discovered indices"

    def test_disposable(self):
        """Tests disposable sources on an edge."""
        def negate(s: bool)-> bool:
            return not s

        hg = Hypergraph()
        hg.add_edge('SA', 'A', R.Rmean)
        hg.add_edge('SB', 'B', R.Rmean)
        hg.add_edge('A', 'A', negate, index_offset=1)
        hg.add_edge('B', 'B', negate, index_offset=1)
        hg.add_edge({'a':'A', 'b':'B'}, 'C', lambda a, b : a and b,
                    disposable=['a', 'b'])
        hg.add_edge('C', 'T', R.Rmean, via=lambda c : c is True)
        hg.add_edge({'a': 'A', 'a_idx': ('a', 'index')}, 'T', R.equal('a_idx'), 
                    via=lambda a_idx, **kw : a_idx >= 5)
        t = hg.solve('T', {'SA': True, 'SB': False})
        assert t.value != True, "Solver used an invalid combination to solve the C->T edge"
        assert t.value == 5, "Solver encountered some error and did not appropriately use the A->T edge"

    def test_index_via(self):
        """Tests whether the `index_via` functionality is working."""
        hg = Hypergraph()
        hg.add_edge('A', 'B', R.Rfirst)
        hg.add_edge('S', 'B', R.Rfirst)
        hg.add_edge('B', 'C', R.Rfirst)
        hg.add_edge('C', 'A', R.Rfirst, index_offset=1)
        hg.add_edge({'a':'A', 'a_idx': ('a', 'index'),
                     'b':'B', 'b_idx': ('b', 'index'),
                     'c':'C', 'c_idx': ('c', 'index')}, 'T', 
                    rel=lambda a_idx, b_idx, c_idx, **kw : (a_idx, b_idx, c_idx), 
                    via=lambda a_idx, **kw : a_idx >= 3,
                    index_via=R.Rsame)
        t = hg.solve('T', {'S': 0})
        assert t.value == (3, 3, 3), "Index for each node should be the same."

    def test_min_index(self):
        """Tests whether the minumum index of a target node can be searched for."""
        hg = Hypergraph()
        hg.add_edge('A', 'B', R.Rfirst)
        hg.add_edge('B', 'C', R.Rfirst)
        hg.add_edge('C', 'A', R.Rincrement, index_offset=1)
        a0 = hg.solve('A', {'A': 0})
        assert a0.index == 1, "Should be initial index of A"
        af = hg.solve('A', {'A': 0}, min_index=5)
        assert af.index == 5, "Index should be 5"

    def test_memory_mode(self):
        """Tests that memory mode returns a collection of solved TNodes."""
        hg = Hypergraph(memory_mode=True)
        hg.add_edge(['A', 'B'], 'C', R.Rsum)
        hg.add_edge(['A', 'C'], 'D', R.Rsum)
        hg.add_edge('D', 'E', R.Rnegate)
        t = hg.solve('E', {'A': 2, 'B': 3},)
        assert len(hg.solved_tnodes) == 5, "Some TNodes not solved for"
        assert hg.solved_tnodes[-1].value == -7, "TNode order may be incorrect"

    def test_hypergraph_union(self):
        """Tests union method for merging with new Hypergraph."""
        hg1 = Hypergraph()
        hg1.add_edge(['A', 'B'], 'C', R.Rsum)
        hg2 = Hypergraph()
        hg2.add_edge(['C', 'D'], 'E', R.Rsum)

        inputs = {'A': 3, 'B': 6, 'D': 100}
        with pytest.raises(KeyError):
            hg1.solve('E', inputs)
        hg1.union(hg1, hg2)
        t = hg1.solve('E', inputs)
        assert t.value == 109

    def test_iadd(self):
        """Tests iadd (+=) dunder overwrite."""
        hg1 = Hypergraph()
        hg1.add_edge(['A', 'B'], 'C', R.Rsum)
        hg2 = Hypergraph()
        hg2.add_edge(['C', 'D'], 'E', R.Rsum)

        inputs = {'A': 3, 'B': 6, 'D': 100}
        hg1 += hg2
        t = hg1.solve('E', inputs)
        assert t.value == 109

    def test_copy(self):
        """Test shallow copy method."""
        hg1 = Hypergraph()
        hg1.add_edge(['A', 'B'], 'C', R.Rsum)
        hg2 = hg1.__copy__()
        hg2.add_edge(['C', 'D'], 'E', R.Rsum)

        inputs = {'A': 3, 'B': 6, 'D': 100}
        with pytest.raises(KeyError):
            hg1.solve('E', inputs)
        t = hg2.solve('E', inputs)
        assert t.value == 109

    def test_add(self):
        """Tests add (+) dunder overwrite."""
        hg1 = Hypergraph()
        hg1.add_edge(['A', 'B'], 'C', R.Rsum)
        hg2 = Hypergraph()
        hg2.add_edge(['C', 'D'], 'E', R.Rsum)
        hg3 = hg1 + hg2

        inputs = {'A': 3, 'B': 6, 'D': 100}
        with pytest.raises(KeyError):
            hg1.solve('E', inputs)
        t = hg3.solve('E', inputs)
        assert t.value == 109

    def test_resolving_inputs(self):
        """Tests whether CHG resolves inputs (an erroneous behavior)."""
        hg = Hypergraph()
        hg.add_edge('S', 'A', R.Rmean)
        hg.add_edge('A', 'B', R.Rmean)
        hg.add_edge('B', 'C', R.Rincrement)
        hg.add_edge('C', 'A', R.Rmean, index_offset=1)
        hg.add_edge('A', 'T', R.Rmean, index_via=R.geq('s1', 5))
        t = hg.solve('T', {'S': 0, 'A': 10})
        assert t.value != 4, 'Input resolved for'
        assert t.value == 14

    def test_print_nodes(self):
        """Tests proper formatting of Hypergraph.print_nodes()"""
        hg = Hypergraph()
        hg.add_node('A')
        b_desc = 'A node'
        hg.add_node(Node('B', 3, description=b_desc))
        out = hg.print_nodes()
        print(out)

        title_len = len('Nodes in Hypergraph:')
        format_len = len('\n - X')
        spacer_len = len(': ')
        calc_len = title_len + 2*format_len + len(b_desc) + spacer_len 
        assert len(out) == calc_len

    def test_hg_str(self):
        """Tests valid execution of Hypergraph.__str__()"""
        hg = Hypergraph()
        hg.add_edge('A', 'B', R.Rsum)
        hg.add_edge('B', 'C', R.Rmultiply)
        assert isinstance(str(hg), str)

class TestHypergraphRelationProcessing:
    def divide(self, top, bottom, *args, **kwargs):
        return top / bottom
    
    def test_argument_reassignment(self):
        hg = Hypergraph()
        hg.add_edge({'top':'A', 'denominator':'B'}, 'C', self.divide)
        C = hg.solve('C', {'A': 16, 'B': 8})
        assert C.value == 2, "Unfound label(s) not reassigned."

    def test_reassignment_argument_warning(self, caplog):
        """Tests whether a warning is raised for an reassigned arguments"""
        with caplog.at_level(logging.WARNING):
            hg = Hypergraph()
            hg.add_edge({'top':'A', 'denominator':'B'}, 'C', self.divide, label='EDGE1')
            try:
                C = hg.solve('C', {'A': 16, 'B': 8})
            except:
                pass
        
        msg = 'Argument "bottom" not passed to EDGE1. Supplying "denominator" instead'
        assert msg in caplog.text, "Warning for reassigned source node not logged."

    def test_unused_argument_warning(self, caplog):
        """Tests whether a warning is raised for an reassigned arguments"""
        with caplog.at_level(logging.WARNING):
            hg = Hypergraph()
            hg.add_edge({'top':'A'}, 'C', self.divide, label='EDGE1')
            try:
                C = hg.solve('C', {'A': 16, 'B': 8})
            except:
                pass
        
        msg = 'Argument "bottom" not passed to EDGE1.'
        assert msg in caplog.text, "Warning for unfound source node not logged."