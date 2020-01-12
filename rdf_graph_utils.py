import os
from time import time
import networkx as nx
import matplotlib.pyplot as plt


def rdf_to_plot(graph):
    nx_graph = nx.DiGraph()
    plt.figure(figsize=(30, 30))

    for (s, p, o) in graph:
        s_n = s.split('/')[-1]
        p_n = p.split('/')[-1]
        o_n = o.split('/')[-1]

        nx_graph.add_node(s_n, name=s_n, pred=False)
        nx_graph.add_node(o_n, name=o_n, pred=False)
        nx_graph.add_edge(s_n, o_n, name=p_n)

    pos = nx.spring_layout(nx_graph)
    edge_labels = nx.get_edge_attributes(nx_graph, 'name')
    nx.draw_networkx_nodes(nx_graph, pos=pos)
    nx.draw_networkx_edges(nx_graph, pos=pos)
    nx.draw_networkx_labels(nx_graph, pos=pos)
    nx.draw_networkx_edge_labels(nx_graph, pos, edge_labels=edge_labels)

    plt.show()


# funzione per stampare file
def rdf_to_text(graph, path, format):
    file = "output_" + str(int(time())) + '.' + format
    path = os.path.join(path, file)

    strings = graph.serialize(format=format)
    print(strings)
    with open(path, 'wb+') as f:
        f.write(strings)


# estrae root node dal graph rdflib
def root_node(graph):
    ss = set()
    oo = set()
    for (s, p, o) in graph:
        ss.add(s)
        oo.add(p)
        oo.add(o)

    ss = ss.difference(oo)
    if len(ss) == 0:
        raise Exception("Error: no root node found.")
    elif len(ss) == 1:
        return ss.pop()
    else:
        raise Exception("Error: multiple root nodes found.")
