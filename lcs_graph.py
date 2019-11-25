from time import time
from hashlib import md5
from knowledge_graph import Vertex, KnowledgeGraph


class LCSGraph(KnowledgeGraph):
    def __init__(self):
        super().__init__()

    def walk(self, childs_1, childs_2, graph1, graph2, depth):
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
                n_v = self.get_vertex(c1.name)
                if not n_v:
                    n_v = Vertex(name=c1.name, predicate=c1.predicate)
                    self.add_vertex(n_v)
                else:
                    remove_edge = loop_over_parents(n_v, c1)
            else:
                blank_n = "_:r_%s" % str(md5(str(time()).encode()).hexdigest())
                n_v = Vertex(name=blank_n, predicate=c1.predicate, blank=True)
                self.add_vertex(n_v)

            if not remove_edge:
                self.add_edge(c1.parent_vertex, n_v)
            for n in graph1.get_neighbors(c1):
                n.parent_vertex = n_v
                to_pass_1.append(n)

        for c2 in childs_2:
            remove_edge = False
            if c2.name in childs_1_name:
                n_v = self.get_vertex(c2.name)
                remove_edge = loop_over_parents(n_v, c2)
            else:
                blank_n = "_:r_%s" % str(md5(str(time()).encode()).hexdigest())
                n_v = Vertex(name=blank_n, predicate=c2.predicate, blank=True)
                self.add_vertex(n_v)

            if not remove_edge:
                self.add_edge(c2.parent_vertex, n_v)
            for n in graph2.get_neighbors(c2):
                n.parent_vertex = n_v
                to_pass_2.append(n)

        if depth == 0 or len(to_pass_1) == 0 or len(to_pass_2) == 0:
            return
        else:
            self.walk(to_pass_1, to_pass_2, graph1, graph2, depth-1)

    def clean_blank_branch(self, vertex, uninformative_triples=[]):
        """
        per il vertice analizzato, nel caso in cui si tratti di un blank node, si verifica che il path a questo sottostante
        sia vuoto. La presenza di una risorsa blank è infatti superflua nel momento in cui non sia collegata ad altre risorse
        nominali, e per questo viene rimossa dal grafo risultante dal LCS.

        :param vertex: vertice di cui ricorsivamente viene analizzata l'utilità all'interno del grafo
        :return: restituisce True o False a seconda che ci siano o meno nodi non rimovibili sotto quello analizzato
        """
        all_removed = True
        # if maximum depth, returning True as there are no children vertex
        if len(self.get_neighbors(vertex)) > 0:
            predicates = self.get_neighbors(vertex)

            for p in set(predicates):
                one_blank_end = False
                for o in set(self.get_neighbors(p)):
                    # check if there are no children vertex (last layer or removed)
                    no_child = self.clean_blank_branch(o, uninformative_triples)
                    if o.blank and no_child:
                        # verifico che non ci sia già un nodo blank senza nodi child associato a quel predicato
                        if not one_blank_end:
                            # rimuovo la tripla solo se anche il predicato è blank o se nel set di uninformative triples
                            if p.blank or p.name in uninformative_triples:  # DA TESTARE
                                self.remove_edge(p, o)
                                self.remove_vertex(o)
                            else:
                                one_blank_end = True
                        else:
                            self.remove_edge(p, o)
                            self.remove_vertex(o)
                    else:
                        all_removed = False

                if len(self.get_neighbors(p)) == 0:
                    self.remove_edge(vertex, p)
                    self.remove_vertex(p)

        return all_removed


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
