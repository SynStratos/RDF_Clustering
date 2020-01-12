import os
import rdflib
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import scipy.sparse as sp
from time import time

from collections import defaultdict, Counter
from functools import lru_cache

from hashlib import md5


class Vertex(object):
    vertex_counter = 0
    
    def __init__(self, name, predicate=False, _from=None, _to=None, wildcard=False, blank=False, parent_vertex=None):
        self.name = name
        self.predicate = predicate
        self._from = _from
        self._to = _to
        self.wildcard = wildcard
        self.blank = blank  # added by me
        self.parent_vertex = parent_vertex  # added by me
        self.literal = False if self.name.startswith("http") else True

        self.id = Vertex.vertex_counter
        Vertex.vertex_counter += 1
        
    def __eq__(self, other):
        if other is None: 
            return False
        return self.__hash__() == other.__hash__()
    
    def __hash__(self):
        if self.predicate:
            return hash((self.id, self._from, self._to, self.name))
        else:
            return hash(self.name)


class KnowledgeGraph(object):
    def __init__(self):
        self.vertices = set()
        self.transition_matrix = defaultdict(set)
        self.label_map = {}
        self.inv_label_map = {}
        self.name_to_vertex = {}
        self.root = None

    # added by me
    def get_vertex(self, name):
        for v in self.vertices:
            if v.name == name:
                return v

        return None
        
    def add_vertex(self, vertex):
        if vertex.predicate:
            self.vertices.add(vertex)
            
        if not vertex.predicate and vertex not in self.vertices:
            self.vertices.add(vertex)

        self.name_to_vertex[vertex.name] = vertex

    # added by me
    def remove_vertex(self, vertex):
        self.vertices.remove(vertex)

    def add_edge(self, v1, v2):
        # Uni-directional edge
        self.transition_matrix[v1].add(v2)
        
    def remove_edge(self, v1, v2):
        if v2 in self.transition_matrix[v1]:
            self.transition_matrix[v1].remove(v2)

    def get_neighbors(self, vertex):
        return self.transition_matrix[vertex]

    # Rappresentazione grafica del knowledge graph
    def visualise(self):
        nx_graph = nx.DiGraph()
        
        for v in self.vertices:
            if not v.predicate:
                name = v.name.split('/')[-1]
                nx_graph.add_node(name, name=name, pred=v.predicate)
            
        for v in self.vertices:
            if not v.predicate:
                v_name = v.name.split('/')[-1]
                # Neighbors are predicates
                for pred in self.get_neighbors(v):
                    pred_name = pred.name.split('/')[-1]
                    for obj in self.get_neighbors(pred):
                        obj_name = obj.name.split('/')[-1]
                        nx_graph.add_edge(v_name, obj_name, name=pred_name)
        
        plt.figure(figsize=(100, 100))
        _pos = nx.spring_layout(nx_graph)
        nx.draw_networkx_nodes(nx_graph, pos=_pos)
        nx.draw_networkx_edges(nx_graph, pos=_pos)
        nx.draw_networkx_labels(nx_graph, pos=_pos)
        nx.draw_networkx_edge_labels(nx_graph, pos=_pos, 
                                     edge_labels=nx.get_edge_attributes(nx_graph, 'name'))
        plt.show()
    
    def _create_label(self, vertex, n):
        neighbor_names = [self.label_map[x][n - 1] for x in self.get_neighbors(vertex)]
        suffix = '-'.join(sorted(set(map(str, neighbor_names))))
        return self.label_map[vertex][n - 1] + '-' + suffix

    # Weisfeiler-Lehman relabeling algorithm
    def weisfeiler_lehman(self, iterations=3):
        # Store the WL labels in a dictionary with a two-level key:
        # First level is the vertex identifier
        # Second level is the WL iteration
        self.label_map = defaultdict(dict)
        self.inv_label_map = defaultdict(dict)

        for v in self.vertices:
            self.label_map[v][0] = v.name
            self.inv_label_map[v.name][0] = v
        
        for n in range(1, iterations+1):

            for vertex in self.vertices:
                # Create multi-set label
                s_n = self._create_label(vertex, n)

                # Store it in our label_map (hash trick from: benedekrozemberczki/graph2vec)
                self.label_map[vertex][n] = str(md5(s_n.encode()).digest())

        for vertex in self.vertices:
            for key, val in self.label_map[vertex].items():
                self.inv_label_map[vertex][val] = key

    def extract_random_walks(self, depth, max_walks=None):
        # Initialize one walk of length 1 (the root)
        walks = [[self.root]]

        for i in range(depth):
            # In each iteration, iterate over the walks, grab the 
            # last hop, get all its neighbors and extend the walks
            walks_copy = walks.copy()
            for walk in walks_copy:
                node = walk[-1]
                neighbors = self.get_neighbors(node)

                if len(neighbors) > 0:
                    walks.remove(walk)

                for neighbor in neighbors:
                    walks.append(list(walk) + [neighbor])

            # TODO: Should we prune in every iteration?
            if max_walks is not None:
                walks_ix = np.random.choice(range(len(walks)), replace=False, 
                                            size=min(len(walks), max_walks))
                if len(walks_ix) > 0:
                    walks = np.array(walks)[walks_ix].tolist()

        # Return a numpy array of these walks
        return np.array(walks)

    def remove_child(self, parent, node):
        """
        funzione per la rimozione di un vertex e di tutti quelli a lui sottostanti
        :param parent: vertex parent di quello da rimuovere, in modo da eliminare anche l'edge
        :param node: vertex su cui applicare la funzione ricorsivamente
        """
        if len(self.get_neighbors(node)) > 0:
            for n in self.get_neighbors(node):
                self.remove_child(node, n)

        self.remove_edge(parent, node)
        self.remove_vertex(node)

    # print knowledge graph as n-triples file
    def print_triples_to_nt(self, path):
        """
        metodo necessario per stampare in formato r-graph testuale le triple contenute nel grafo
        :param path: percorso completo dove salvare il file risultante
        :return:
        """
        s = self.root
        name = s.name.split("/")[-1]
        name = ''.join(e for e in name if e.isalnum())
        name = name + "_" + str(int(time())) + ".nt"
        path = os.path.join(path, name)
        with open(path, 'w+') as f:
            self.__print_triples__(f, s)

    def __print_triples__(self, f, s):
        """
        funzione ausiliaria ricorsiva che percorre tutti i branch e aggiunge la tripla al file in output
        :param f: file in cui scrivere
        :param s: risorsa soggetto analizzata
        :return:
        """
        for p in self.get_neighbors(s):
            for o in self.get_neighbors(p):
                s_n = "<"+s.name+">" if not p.literal else s.name
                p_n = "<" + p.name + ">" if not p.literal else p.name
                o_n = "<" + o.name + ">" if not p.literal else o.name
                # st = s.name + " " + p.name + " " + o.name + ".\n"
                # f.write(st)
                f.write(s_n + " ")
                f.write("  " + p_n + "\n")
                f.write("    " + o_n + ".\n\n")

                if len(self.get_neighbors(o)) > 0:
                    self.__print_triples__(f, o)


# convert back kwnoledge graph to rdflib graph
def kg_to_rdflib(kg, depth):
    g = rdflib.Graph()
    s = kg.root

    _kg_to_rdflib(kg, g, s, depth)
    return g


def _kg_to_rdflib(kg, g, s, depth):
    for p in kg.get_neighbors(s):

        for o in kg.get_neighbors(p):
            sub = _to_rdflib_resource(s)
            prd = _to_rdflib_resource(p)
            obj = _to_rdflib_resource(o)

            g.add((sub, prd, obj))

            if len(kg.get_neighbors(o)) > 0 and depth > 0:
                _kg_to_rdflib(kg, g, o, depth-1)


def _to_rdflib_resource(vertex):
    """
    funzione per trasformare un vertice del kownledge graph in risorsa da inserire in un graph rdflib
    """
    if vertex.blank:
        r = rdflib.Literal(vertex.name) #rdflib.BNode()
    else:
        if vertex.literal:
            r = rdflib.Literal(vertex.name)
        else:
            r = rdflib.URIRef(vertex.name)
    return r


def rdflib_to_kg(rdflib_g, label_predicates=[]):
    # Iterate over triples, add s, p and o to graph and 2 edges (s-->p, p-->o)
    # all predicates in label_predicates get excluded
    kg = KnowledgeGraph()
    for (s, p, o) in rdflib_g:
        if p not in label_predicates:
            s_v, o_v = Vertex(str(s)), Vertex(str(o))
            p_v = Vertex(str(p), predicate=True)
            kg.add_vertex(s_v)
            kg.add_vertex(p_v)
            kg.add_vertex(o_v)
            kg.add_edge(s_v, p_v)
            kg.add_edge(p_v, o_v)
    return kg


def extract_instance(kg, instance, depth=8):
    subgraph = KnowledgeGraph()
    subgraph.label_map = kg.label_map
    subgraph.inv_label_map = kg.inv_label_map
    root = kg.name_to_vertex[str(instance)]
    to_explore = {root}
    subgraph.add_vertex(root)
    subgraph.root = root
    for d in range(depth):
        for v in list(to_explore):
            for neighbor in kg.get_neighbors(v):
                subgraph.add_vertex(neighbor)
                subgraph.add_edge(v, neighbor)
                to_explore.add(neighbor)
            to_explore.remove(v)
    return subgraph