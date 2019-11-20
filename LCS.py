import graph
from graph import Vertex, KnowledgeGraph
from time import time


a_uri = ""
a_graph = None

b_uir = ""
b_graph = None

blank_node = "n_"
blank_pred = "p_"

i = 0
j = 0

'''
def check(pairs1, pairs2):
    parent = False
    common = []
    for (p, o) in pairs1:
        if (p, o) in pairs2:
            parent = True
            common.append( (p,o) )

    return parent, common

def foo(node, graph, depth):

    couples = []
    if depth != 0:
        preds = graph.get_neighbors(node)
        for pred in preds:
            obj = graph.get_neighbors(pred)
            couples.append( (pred, obj) )

    if depth == 0:
        check()


def search_for_lcs(x_Tx, x, g1, a, g2, b, depth=2, c_depth=0):
    # iterate
    if c_depth==0:
        if a == b:
            x = a
        else:
            x = blank_node

        x_Tx.add_vertex(x)

    couples_1 = []
    couples_2 = []
    preds_1 = g1.get_neighbors(a)
    preds_2 = g2.get_neighbors(b)
    for p in preds_1:
        for o in g1.get_neighbors(p):
            couples_1.append( (p, o) )
    for p in preds_2:
        for o in g2.get_neighbors(p):
            couples_2.append( (p, o) )

    for p, o in couples_1:
        for p1, o1 in couples_2:
            if o1 == o:
                if p1 == p:
                    pred = graph.Vertex(str(p), predicate=True)
                else:
                    pred = graph.Vertex(str(blank_pred), predicate=True)
                obj = graph.Vertex(str(o))
                x_Tx.add_edge(x, pred)
                x_Tx.add_edge(pred, obj)
'''

"""
def start_lcs(a, b, g1, g2, depth=2):
    x_Tx = graph.KnowledgeGraph()

    n1 = Node(a, pred=None, parent=None)
    n2 = Node(b, pred=None, parent=None)

    walk(g1, g2, [n1], [n2], depth, x_Tx)

    return x_Tx


def walk(g1, g2, nodes1, nodes2, depth, x_Tx):

    if depth > 0:
        child_nodes1 = []
        for n1 in nodes1:
            if len(g1.get_neighbors(n1.uri)) > 0:

                for p in g1.get_neighbors(n1.uri):

                    for o in g1.get_neighbors(p):
                        if o.name != n1.uri:
                            print(p.name)
                            print(o.name)
                            print('-----')
                            node1 = Node(o.name, pred=p.name, parent=n1)
                            child_nodes1.append(node1)
            else:
                for n2 in nodes2:
                    if n2.uri == n1.uri:
                        validate_path(n1.uri, n1, n2, x_Tx)

        child_nodes2 = []
        for n2 in nodes2:
            if len(g2.get_neighbors(n2.uri)) > 0:
                for p in g2.get_neighbors(n2.uri):
                    for o in g2.get_neighbors(p):
                        node2 = Node(o.name, pred=p.name, parent=n2)
                        child_nodes2.append(node2)

            else:
                for n1 in nodes1:
                    if n2.uri == n1.uri:
                        validate_path(n2.uri, n1, n2, x_Tx)

        walk(g1, g2, child_nodes1, child_nodes2, depth-1, x_Tx)

    elif depth == 0:
        for n1 in nodes1:
            for n2 in nodes2:
                if n2.uri == n1.uri:
                    validate_path(n1.uri, n1, n2, x_Tx)


def validate_path(uri, node1, node2, x_Tx):

    v = x_Tx.get_vertex(uri)
    if not v:
        v = Vertex(name=uri)
        x_Tx.add_vertex(v)
    if node1.pred == node2.pred:
        pred_v = Vertex(node1.pred, predicate=True) if not x_Tx.get_vertex(node1.pred) else x_Tx.get_vertex(node1.pred)

    else:
        global j
        j += 1
        pred = "blank/p_%s" % str(j)
        pred_v = Vertex(pred, predicate=True)
    x_Tx.add_vertex(pred_v)
    x_Tx.add_edge(pred_v, v)

    if node1.parent.uri == node2.parent.uri:
        node = node1.parent.uri
        node_v = Vertex(node1.parent.uri) if not x_Tx.get_vertex(node1.parent.uri) else x_Tx.get_vertex(node1.parent.uri)
    else:
        global i
        i += 1
        node = "blank/n_%s" % str(j)
        node_v = Vertex(node)
    x_Tx.add_vertex(node_v)
    x_Tx.add_edge(node_v, pred_v)

    if node1.parent.parent and node1.parent.parent:
        validate_path(node, node1.parent, node2.parent, x_Tx)

def __start_lcs__(n1, n2, g1, g2):
    x_Tx = KnowledgeGraph()
    if n1 == n2:
        uri = n1
        v = Vertex(name=n1)
        x_Tx.add_vertex(v)
    else:
        global i
        uri = "blank/:_r%s" % str(i)
        i += 1
        v = Vertex(name=uri)
        x_Tx.add_vertex(v)

    __walk__(v, n1, n2, g1, g2, x_Tx)




def __walk__(top, node1, node2, graph1, graph2, x_Tx):
    pred1 = graph1.get_neighbors(node1)
    pred2 = graph2.get_neighbors(node2)


    for p in pred1:
        pv = None
        pred_found = False
        at_least_one = False

        blank_p = "/:p_%s" % str(time())
        blank_o = "/:r_%s" % str(time())
        if p in pred2:
            pv = Vertex(name=p, predicate=True)
            x_Tx.add_vertex(pv)
            x_Tx.add_edge(top, pv)
            pred_found = True

        for o in graph1.get_neighbors(p):
            if o in graph2.get_neighbors(p):
                at_least_one = True
                ov = Vertex(name=o)
                x_Tx.add_vertex(ov)
                if not pred_found:
                    pred_found = True
                    pv = Vertex(name=blank_pred, predicate=True)
                    x_Tx.add_vertex(pv)
                    x_Tx.add_edge(top, pv)
                x_Tx.add_vertex(ov)
                x_Tx.add_edge(pv, ov)

"""

def new_lcs(node1, node2, graph1, graph2, depth):
    x_Tx = KnowledgeGraph()

    if node1 != node2:
        blank_n = "/:x_%s" % str(time())
        start_vertex = Vertex(name=blank_n, predicate=False, blank=True)
    else:
        start_vertex = Vertex(name=node1)

    x_Tx.add_vertex(start_vertex)
    v1 = graph1.get_vertex(node1)
    v2 = graph2.get_vertex(node2)

    childs1 = graph1.get_neighbors(v1)
    childs2 = graph2.get_neighbors(v2)
    childs1_x = []
    childs2_x = []
    for c in childs1:
        c.parent_vertex = start_vertex
        childs1_x.append(c)
    for c in childs2:
        c.parent_vertex = start_vertex
        childs2_x.append(c)

    walk(x_Tx, childs1, childs2, graph1, graph2, depth=(depth*2))
    clean_blank_branch(start_vertex, x_Tx)
    return x_Tx


def walk(new_graph, childs_1, childs_2, graph1, graph2, depth):
    childs_1_name = [c.name for c in childs_1]
    childs_2_name = [c.name for c in childs_2]

    to_pass_1 = []
    to_pass_2 = []

    for c1 in childs_1:
        if c1.name in childs_2_name:
            n_v = new_graph.get_vertex(c1.name)
            if not n_v:
                n_v = Vertex(name=c1.name, predicate=c1.predicate)
                new_graph.add_vertex(n_v)
        else:
            blank_n = "/:r_%s" % str(time())  # TODO HASH FUNCTION
            n_v = Vertex(name=blank_n, predicate=c1.predicate, blank=True)
            new_graph.add_vertex(n_v)

        print(c1.parent_vertex.name)
        new_graph.add_edge(c1.parent_vertex, n_v)
        for n in graph1.get_neighbors(c1):
            n.parent_vertex = n_v
            to_pass_1.append(n)

    for c2 in childs_2:
        if c2.name in childs_1_name:
            n_v = new_graph.get_vertex(c2.name)
        else:
            blank_n = "/:r_%s" % str(time())
            n_v = Vertex(name=blank_n, predicate=c2.predicate, blank=True)
            new_graph.add_vertex(n_v)

        print(c2.parent_vertex.name)
        new_graph.add_edge(c2.parent_vertex, n_v)
        for n in graph2.get_neighbors(c2):
            n.parent_vertex = n_v
            to_pass_2.append(n)

    if depth == 0 or len(to_pass_1) == 0 or len(to_pass_2) == 0:
        return
    else:
        walk(new_graph, to_pass_1, to_pass_2, graph1, graph2, depth-1)


def clean_blank_branch(vertex, graph):
    all_removed = True

    # if maximum depth, returning True as there are no children vertex
    if len(graph.get_neighbors(vertex)) > 0:
        predicates = graph.get_neighbors(vertex)

        for p in predicates:
            for o in set(graph.get_neighbors(p)):
                # check if there are no children vertex (last layer or removed)
                no_child = clean_blank_branch(o, graph)
                if o.blank and no_child:  #  and p.blank
                    print('removing')
                    graph.remove_edge(p, o)
                    graph.remove_vertex(o)
                else:
                    all_removed = False

    return all_removed



"""
class Node:
    def __init__(self, uri, pred, parent):
        self.uri = uri
        self.pred = pred
        self.parent = parent
"""