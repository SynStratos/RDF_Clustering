import rdflib
import sys
from time import time
from hashlib import md5
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
from sortedcontainers import SortedSet, SortedList

from knowledge_graph import Vertex, KnowledgeGraph, kg_to_rdflib
from rdf_graph_utils import root_node

m = md5()
stop_patterns = []


class Visited(list):
    def __init__(self):
        super().__init__()

    def add_new(self, a, b, x, T_x):
        w, _ = self.get(a, b)
        if not w:
            self.append((SortedList((a, b)), x, T_x))

    def get(self, a, b):
        ab = SortedList((a, b))
        for (z, x, t_x) in self:
            if z == ab:
                return x, t_x
        return None, None


class LCS(rdflib.Graph):
    def __init__(self, graph1, graph2, depth, stop_patterns=[], uninformative_triples=[]):
        super().__init__()
        self.a_T = kg_to_rdflib(graph1, depth) if isinstance(graph1, KnowledgeGraph) else graph1
        self.b_T = kg_to_rdflib(graph2, depth) if isinstance(graph2, KnowledgeGraph) else graph2
        self.max_depth = depth
        self.stop_patterns = stop_patterns
        self.uninformative_triples = [str(t) for t in uninformative_triples]
        self.visited = Visited()
        # self.sigmas = dict()

        # self.cleaned = dict()

        # self.i = 0

    def find(self):
        """
        funzione per la costruzione del grafo LCS a partire dai root node dei due grafi dati come parametro
        avvia la funzione ricorsiva explore che verificherà tutte le triple
        successivamente il grafo LCS verrà completato con tutti i sotto grafi CS identificati
        :return:
        """
        a = root_node(self.a_T)
        b = root_node(self.b_T)
        print("starting graphs exploration...")
        self.explore(a, self.a_T, b, self.b_T)  # clean=self.clean)
        print("exploration ended.")
        print("filling LCS graph.")
        for (_, _, T_x) in self.visited:
            for t in T_x:
                self.add(t)
        print("graph completed.")

    def explore(self, a, a_T, b, b_T, depth=0):
        """

        :param a: prima risorsa da confrontare
        :param a_T: grafo a cui appartiene la prima risorsa
        :param b: seconda risorsa da confrontare
        :param b_T: grafo a cui appartiene la seconda risorsa
        :param depth: livello di esplorazione su cui si trova la funzione
        :return: restituisce la risorsa creata dal confronto, T/F se blank senza child e T/F se uninformative
        """
        # verifico che la coppia di risorse 'a' e 'b' non sia già stata valutata
        # e eventualmente ne recupero il grafo risultante
        x, x_T = self.visited.get(a, b)
        # boolean che aggiornerò durante l'esplorazione per segnare che la risorsa sia un nodo blank senza child o meno
        blank = False

        # verifico che x non sia nullo (in tal caso la coppia è già stata esplorata)
        if x:
            print("coppia di risorse già esplorata")
            print(str(a), str(b), str(x))
            # se x_T è vuoto la risorsa non ha nodi child e se il prefisso "blank:" è nel nome
            # rispetta le condizioni per essere segnata come blank
            if len(x_T) == 0 and "blank:" in x:
                blank = True
        else:
            # in questo caso la coppia di risorse non è già stata esplorata
            x_T = rdflib.Graph()
            # controllo che le due risorse coincidano o meno
            # print("check")
            # print(str(a), str(b))
            if str(a) == str(b):
                # if a == b:
                print("le due risorse sono uguali")
                x = a
            else:
                print("le due risorse sono differenti")
                x = blank_node()
                # aggiorno il valore del booleano blank
                # (verrà aggiornato nuovamente a false nel momento in cui ha nodi child)
                blank = True

            # aggiungo la coppia di risorse all'elenco di nodi esplorati
            self.visited.add_new(a, b, x, x_T)

            # se la profondità non è ancora quella imposta come massima, continuo l'esplorazione
            if depth < self.max_depth:
                # se le risorse sono uguali, x_T corrisponderà alle triple ottenute dal sigma della risorsa stessa,
                # specificando una profondità pari a max_depth - depth
                if a == b:
                    x_T = self.compute_sigma(a, a_T, self.max_depth - depth)
                else:
                    for (s_a, p_a, o_a) in self.compute_sigma(a, a_T):

                        to_add = []
                        complete_triple = None
                        blank_p = False
                        blank_o = False

                        for (s_b, p_b, o_b) in self.compute_sigma(b, b_T):
                            y, y_blank, y_uninformative = self.explore(p_a, a_T, p_b, b_T, depth + 1)
                            z, z_blank, _ = self.explore(o_a, a_T, o_b, b_T, depth + 1)

                            # verifico che le due risorse risultanti non siano entrambe blank senza child
                            # (o con predicato uninformative)
                            # in quel caso non voglio aggiungerle al grafo risultante
                            blank = blank and ((y_blank or y_uninformative) and z_blank)
                            if (y_blank or y_uninformative) and z_blank:
                                pass
                            else:
                                # verifico la presenza della tripla con sole risorse (predicato e oggetto) uguali
                                if "blank:" not in y and "blank:" not in z:
                                    # print("complete triple", x, y, z)
                                    complete_triple = (x, y, z)
                                    break
                                # verifico di aver già aggiunto la tripla con predicato blank senza child
                                # e medesimo oggetto non blank
                                elif y_blank and "blank:" not in z:
                                    if not blank_p:
                                        blank_p = True
                                        to_add.append((x, y, z))
                                # verifico di aver già aggiunto la tripla con oggetto blank senza child
                                # medesimo predicato non blank
                                elif "blank:" not in y and z_blank:
                                    if not blank_o:
                                        blank_o = True
                                        to_add.append((x, y, z))
                                # altrimenti il risultato sarà generalmente una tripla con oggetto e/o predicato blank
                                # ma con nodi child
                                else:
                                    # print("standard triple", x, y, z)
                                    to_add.append((x, y, z))

                        # infine, se ho individuato la tripla "completa" di predicato e oggetto,
                        # aggiungo solamente quella al grafo risultante
                        if complete_triple:
                            # print("ADDING COMPLETE TRIPLE TO X_T")
                            x_T.add(complete_triple)
                        # in caso contrario aggiungo tutte le triple che ho salvato nella lista "to_add"
                        else:
                            for triple in to_add:
                                x_T.add(triple)

        # verifico che la risorsa sia o meno "uninformative" (utilizzato solo per predicati durante l'esplorazione")
        uninformative = str(x) in self.uninformative_triples

        return x, blank, uninformative

    def compute_sigma(self, node, graph, max_depth=0, depth=0):
        """
        funzione per la creazione di un nuovo graph da quello dato, con le triple collegate al nodo dato
        :param node: risorsa di cui creare il grafo
        :param graph: intero dataset su cui effettuare la query
        :param max_depth: profondità massima del grafo da creare
        :param depth: profondità attuale della ricerca
        :return: viene restituita una lista contenente tutte le triple ottenute dalla query
        """
        query = """
        CONSTRUCT { ?s ?p ?o. }
        WHERE { ?s ?p ?o.
        """.replace("?s", "<%s>" % node)

        filter_block = self.__make_filter_block__(graph)

        query = query + filter_block + '}'

        # effettuo la query solamente nel momento in cui il soggetto passato come argomento è una risorsa rdf e non un literal
        # nel secondo caso restituisco una lista vuota
        if "http" in node:
            sigma_q = graph.query(query)
            sigma = rdflib.Graph()
            for triple in sigma_q:
                # print(triple)
                sigma.add(triple)
            if depth < max_depth:
                depth += 1
                child = []
                for (s, p, o) in sigma:
                    child.append(p)
                    child.append(o)
                for c in child:
                    g_child = self.compute_sigma(c, graph, max_depth, depth)
                    for (s, p, o) in g_child:
                        sigma.add((s, p, o))
                        # try:
                        #     sigma.add((s, p, o))
                        # except:
                        #     continue
            # print("sigma dim: ", len(sigma))
        else:
            print("sigma not resource but literal.")
            sigma = []
        return sigma

    def __make_filter_block__(self, graph=None):
        """
        funzione per aggiungere alla query campi filter per ogni stop pattern
        :param graph: necessario solo se si inserisce un campo come "root_node" negli stop pattern che preveda il recupero
        di informazioni dal grafo
        :return: restituisce la stringa contenente tutti i campi filter
        """
        if len(self.stop_patterns) == 0:
            return ""
        stops = list(stop_patterns)
        filter_string = "FILTER({}) "
        filter_block = ""
        for line in stops:
            if "root_node" in line:
                line = line.replace("root_node", "<%s>" % root_node(graph))

            fs = filter_string.format(line)
            filter_block += fs
        return filter_block


def blank_node():
    # return rdflib.BNode()
    return rdflib.Literal("blank:r_%s" % str(md5(str(time()).encode()).hexdigest()))
