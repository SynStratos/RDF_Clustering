import rdflib
from time import time
from hashlib import md5
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph


from lcs_graph import LCSGraph
from knowledge_graph import Vertex, KnowledgeGraph, kg_to_rdflib
m = md5()


def new_lcs(graph1, graph2, depth, stop_patterns=[], uninformative_triples=[]):
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
    interamente da blank nodes, in quanto non danno alcuna informazione utile alla costruzione del LCS.

    :param uninformative_triples:
    :param stop_predicates:
    :param node1: starting node del primo grafo
    :param node2: starting node del secondo grafo
    :param graph1: primo grafo
    :param graph2: secondo grafo
    :param depth: profondità massima desiderata (1 == coppia p-o)
    :return: restituisco rdflib.Graph risultante
    """

    x_Tx = LCSGraph()

    node1 = graph1.root
    node2 = graph2.root

    if node1.name != node2.name:
        blank_n = "_:x_%s" % str(md5(str(time()).encode()).hexdigest())
        start_vertex = Vertex(name=blank_n, predicate=False, blank=True)
    else:
        start_vertex = Vertex(name=node1.name)

    x_Tx.add_vertex(start_vertex)
    x_Tx.root = start_vertex

    childs1 = graph1.get_neighbors(node1)
    childs2 = graph2.get_neighbors(node2)

    for c in childs1:
        c.parent_vertex = start_vertex
    for c in childs2:
        c.parent_vertex = start_vertex

    # viene moltiplicata per 2 la profondità perchè non più corrispondente ad una coppia p-o ma ad ogni singolo layer
    x_Tx.walk(childs1, childs2, graph1, graph2, depth=(depth*2))
    # vengono rimossi tutti i branch contenenti solo nodi blank o uninformative triples
    x_Tx.clean_blank_branch(start_vertex, uninformative_triples)

    # converto knowledge graph to rdflib graph in modo da poter effettuare query
    rdf_x_tx = kg_to_rdflib(x_Tx, depth)

    # viene costruita la query in modo da contenere nel campo filter tutti gli stopping pattern passati alla funzione
    query = "CONSTRUCT{ ?s ?p ?o. } WHERE {?s ?p ?o. "

    filter_string = "FILTER({}) "
    filter_block = ""
    for line in stop_patterns[:3]:
        # NB: di default, se voglio inserire il nodo root nelle query, posso farlo con la keyword 'root_node'
        # verrà automaticamente sostituito in questo step
        # utile per applicare filtri che non debbano interessare le triple del primo livello
        line = line.replace("root_node", x_Tx.root.name)
        fs = filter_string.format(line)
        filter_block += fs

    query = query + filter_block + '}'

    # applico la query appena definita sul grafo
    result = rdf_x_tx.query(query)
    # il risultato sarà un nuovo rdflib graph privato delle triple che soddisfano le condizioni passate come parametro

    return result