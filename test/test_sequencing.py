from dev.sequencing import Node, Edge

def rel_sum(*source):
    return sum(*source)

def rel_multiply(*source):
    i = 1
    for s in source:
        i *= s
    return i

# def makeForestOld(hasInvalid: bool=False) -> Forest:
#     '''Makes a demonstration forest'''
#     A, B, C, D = [Edge('ABCD'[i], value=i+1) for i in range(4)]
#     Z, Y, X, W = [Edge('ZYXW'[i], value=i*10) for i in range(4)]

#     if hasInvalid:
#         D.value = None

#     e00 = Edge('e00', [B, C, D], rel_multiply)
#     e01 = Edge('e01', [A, e00], rel_multiply)
#     e10 = Edge('e10', [Z, Y], rel_sum)
#     e11 = Edge('e11', [X, W], rel_sum)
#     e12 = Edge('e12', [e10, e11], rel_sum)

#     t01 = Forest([e01, e12])
#     t02 = Forest([e00, A])
#     t03 = Forest([B, C, D])
#     t12 = Forest([e10, e11])
#     t13 = Forest([Z, Y])
#     t14 = Forest([X, W])

#     forest = Forest([e01, e12])
#     return forest

def makeForest(hasInvalid: bool=False) -> Node:
    labels = ['A', 'B', 'C', 'D', 'E', 'G', 'H', 'I', 'J', 'T']
    cNodes = [Node(label=label) for label in labels]
    A, B, C, D, E, G, H, I, J, T = cNodes
    bA, bB, bC, bD, bE, bG, bH, bI, bJ, bT = [Edge([cNode], rel=rel_sum) for cNode in cNodes]
    bDE = Edge([D, E])
    bBC = Edge([B, C])

    A.value = 1
    B.generating_edges = [bA]
    C.generating_edges = [bA]
    D.generating_edges = [bB, bE]
    E.generating_edges = [bBC]
    G.generating_edges = [bC, bH]
    H.generating_edges = [bDE]
    I.generating_edges = [bD]
    J.generating_edges = [bI]
    T.generating_edges = [bJ, bH, bG]

    return T

class TestForest():
    T = makeForest()
    T.getValue()
    
    # forest2 = makeForest(hasInvalid=True)

    def test_T(self):
        assert self.T.value == 5


    # def test_forest_normal(self):
    #     assert self.forest1() == 24, "Should be 24"

    # def test_forest_branching(self):
    #     assert self.forest2() == 70, "Should be 70"


if __name__ == '__main__':
    tf = TestForest()
    tf.test_forest_normal()