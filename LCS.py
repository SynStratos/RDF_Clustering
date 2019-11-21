from graph import Vertex, KnowledgeGraph
from time import time
from hashlib import md5

m = md5()


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
        blank_n = "/:x_%s" % str(md5(str(time()).encode()).hexdigest())
        start_vertex = Vertex(name=blank_n, predicate=False, blank=True)
    else:
        start_vertex = Vertex(name=node1)

    x_Tx.add_vertex(start_vertex)
    v1 = graph1.root
    v2 = graph2.root

    childs1 = graph1.get_neighbors(v1)
    childs2 = graph2.get_neighbors(v2)
    
    for c in childs1:
        c.parent_vertex = start_vertex
    for c in childs2:
        c.parent_vertex = start_vertex

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
            blank_n = "/:r_%s" % str(md5(str(time()).encode()).hexdigest())
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
            blank_n = "/:r_%s" % str(md5(str(time()).encode()).hexdigest())
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
