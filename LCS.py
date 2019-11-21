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
    """
    questa funzione avvia la costruzione del grafo risultante dal LCS
    vengono dati in input gli starting node dei due grafi di partenza, i due grafi e la profondità massima richiesta nella
    ricerca dei CS.

    viene creato un nuovo oggetto di tipo KnowledgeGraph, a cui andremo ad aggiungere di volta in volta tutti i vertici
    in comune e i nodi blank.
    una volta creato e aggiunto il nodo di partenza (blank se diversi), viene avviato il metodo ricorsivo 'walk'.
    questo andrà a ricercare tutti i neighbors (in modo alternato saranno predicati e oggetti) per aggiungere al grafo
    risultante ogni vertice comune o i blank nodes.

    al termine della ricerca, viene lanciata la funzione 'clean_blank_branch', che rimuove dal grafo ogni ramo costituito
    interamente da predicati e blank nodes, in quanto non danno alcuna informazione utile alla costruzione del LCS.

    :param node1: starting node del primo grafo
    :param node2: starting node del secondo grafo
    :param graph1: primo grafo
    :param graph2: secondo grafo
    :param depth: profondità massima desiderata (1 == coppia p-o)
    :return:
    """

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

    # viene moltiplicata per 2 la profondità perchè non più corrispondente ad una coppia p-o ma ad ogni singolo layer
    walk(x_Tx, childs1, childs2, graph1, graph2, depth=(depth*2))
    clean_blank_branch(start_vertex, x_Tx)
    return x_Tx


def walk(new_graph, childs_1, childs_2, graph1, graph2, depth):
    """
    questo metodo analizza ricorsivamente tutti i vertici contenuti nei due array passati come parametri.
    verifica che ci siano nodi in comune e gli aggiunge al grafo risultante.
    tutti i nodi non in comune vengono temporaneamente aggiunti come nodi blank in modo da poter comunque collegare
    ulteriori nodi in comune tra i due grafi sottostanti a questo livello.
    ogni volta viene verificata la presenza di un vertice analogo all'interno del grafo, in modo da non aggiungere più
    nodi che facciano riferimento alla medesima risorsa.

    per ogni nodo analizzato verranno poi prelevati i children e aggiunti all'array (rispettivamente del primo o del
    secondo grafo), che costituiranno i nodi relativi al layer successivo. viene quindi lanciata ricorsivamente la
    stessa funzione walk sulle due nuove liste ottenute (con depth ridotta di 1).

    tramite l'utilizzo della funzione 'loop_over_parents', nel momento in cui si sta aggiungendo un nuovo vertice IN
    COMUNE, si verifica di non collegarlo a più blank nodes diversi che riportano un path analogo (ovvero costituito da
    risorse uguali o blank nodes). la presenza di questo tipo di collegamenti sarebbe inutile per il lcs e priva di
    alcun significato.

    inoltre tutti i branch costituiti da sole risorse blank, verranno eliminate al termine della prima costruzione del
    grafo.

    al termine dell'esecuzione si avrà un grafo risultante interamente riempito.

    :param new_graph: knowledge graph risultante su cui aggiungere i nuovi vertici
    :param childs_1: lista di nodi da analizzare per il primo grafo
    :param childs_2: lista di nodi da analizzare per il secondo grafo
    :param graph1: primo grafo
    :param graph2: secondo grafo
    :param depth: livello di profondità
    :return:
    """
    childs_1_name = [c.name for c in childs_1]
    childs_2_name = [c.name for c in childs_2]

    to_pass_1 = []
    to_pass_2 = []

    for c1 in childs_1:
        remove_edge = False
        if c1.name in childs_2_name:
            n_v = new_graph.get_vertex(c1.name)
            if not n_v:
                n_v = Vertex(name=c1.name, predicate=c1.predicate)
                new_graph.add_vertex(n_v)
            else:
                remove_edge = loop_over_parents(n_v, c1)
        else:
            blank_n = "/:r_%s" % str(time())  # TODO HASH FUNCTION
            n_v = Vertex(name=blank_n, predicate=c1.predicate, blank=True)
            new_graph.add_vertex(n_v)

        if not remove_edge:
            new_graph.add_edge(c1.parent_vertex, n_v)
        for n in graph1.get_neighbors(c1):
            n.parent_vertex = n_v
            to_pass_1.append(n)

    for c2 in childs_2:
        remove_edge = False
        if c2.name in childs_1_name:
            n_v = new_graph.get_vertex(c2.name)
            remove_edge = loop_over_parents(n_v, c2)
        else:
            blank_n = "/:r_%s" % str(time())
            n_v = Vertex(name=blank_n, predicate=c2.predicate, blank=True)
            new_graph.add_vertex(n_v)

        if not remove_edge:
            new_graph.add_edge(c2.parent_vertex, n_v)
        for n in graph2.get_neighbors(c2):
            n.parent_vertex = n_v
            to_pass_2.append(n)

    if depth == 0 or len(to_pass_1) == 0 or len(to_pass_2) == 0:
        return
    else:
        walk(new_graph, to_pass_1, to_pass_2, graph1, graph2, depth-1)


def loop_over_parents(n1, n2):
    """
    questo metodo aiuta nell'evitare che vengano aggiunti vertici figli di nodi blank che hanno un percorso equivalente,
    ovvero costituito da soli nodi blank o nodi uguali.
    :param n1: primo dei due nodi di cui analizzare gli ancestors
    :param n2: secondo dei due nodi di cui analizzare gli ancestors
    :return: restituisce True o False a seconda se l'edge analizzata vada aggiunta o meno al grafo
    """
    remove_edge = True
    while n1.parent_vertex and n2.parent_vertex:
        n1 = n1.parent_vertex
        n2 = n2.parent_vertex
        if not n1.blank and not n2.blank:
            if n1 != n2:
                remove_edge = False
                break

    return remove_edge


def clean_blank_branch(vertex, graph):
    """
    per il vertice analizzato, nel caso in cui si tratti di un blank node, si verifica che il path a questo sottostante
    sia vuoto. La presenza di una risorsa blank è infatti superflua nel momento in cui non sia collegata ad altre risorse
    nominali, e per questo viene rimossa dal grafo risultante dal LCS.

    :param vertex: vertice di cui ricorsivamente viene analizzata l'utilità all'interno del grafo
    :param graph: grafo esaminato
    :return: restituisce True o False a seconda che ci siano o meno nodi non rimovibili sotto quello analizzato
    """
    all_removed = True
    # if maximum depth, returning True as there are no children vertex
    if len(graph.get_neighbors(vertex)) > 0:
        predicates = graph.get_neighbors(vertex)

        for p in predicates:
            for o in set(graph.get_neighbors(p)):
                # check if there are no children vertex (last layer or removed)
                no_child = clean_blank_branch(o, graph)
                if o.blank and no_child:  #  and p.blank
                    graph.remove_edge(p, o)
                    graph.remove_vertex(o)
                else:
                    all_removed = False

    return all_removed
