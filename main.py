# # %%
#
# import rdflib
# import pandas as pd
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.metrics import confusion_matrix
# from sklearn.cluster import KMeans, DBSCAN
# from sklearn.decomposition import PCA
# from mpl_toolkits.mplot3d import Axes3D
# from matplotlib import pyplot
# from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
# import networkx as nx
#
# from knowledge_graph import *
# from rdf2vec import RDF2VecTransformer
# from LCS import new_lcs
#
# # %%
#
# print(end='Loading data... ', flush=True)
# g = rdflib.Graph()
# g.parse('data/new_limit_500k.nt', format="nt")
# print('OK')
#
# # Extract all database drugs' URI
# all_drugs_file = pd.read_csv('data/all_drugs.tsv', sep='\t')
# all_drugs = [rdflib.URIRef(x) for x in all_drugs_file['drug']]
#
# # Define irrelevant predicates
# predicates = pd.read_csv('data/bad_predicates.tsv', sep='\t')
# predicates = [rdflib.URIRef(x) for x in predicates['predicate']]
#
# # %%
# # conversione da rdflib.Graph a KnowledgeGraph -> necessaria per applicare rdf2vec
# # con label_predicates si vanno ad indicare i predicati che verranno esclusi nella costruzione del kg risultante
# kg = rdflib_to_kg(g, label_predicates=predicates)
#
# # %%
# # estraggo un'istanza di knowledge graph per ogni drug presente in quello iniziale
# i = 1
# j = 1
#
# drugs = []
# graphs = []
# for drug in all_drugs:
#     try:
#         g = extract_instance(kg, drug)
#         graphs.append(g)
#         drugs.append(drug)
#         i += 1
#     except Exception as e:
#         j += 1
#
# print('ok:' + str(i))
# print('failed:' + str(j))
#
#
#
# # Embeddings
# transformer = RDF2VecTransformer(_type='walk', walks_per_graph=500)
# embeddings = transformer.fit_transform(graphs)
#
# # Clustering KMeans
# kmeans = KMeans(n_clusters=7)
# k = kmeans.fit(embeddings)
# y_kmeans = kmeans.predict(embeddings)
#
#
# #
# k = 0
# for y in y_kmeans:
#     print(str(k) + ': ' + str(y))
#     k += 1
#
# # %%
# graph1 = graphs[6]
# graph2 = graphs[8]
#
#
# def lcs():
#     x_Tx = new_lcs(graph1, graph2, 2)
#     x_Tx.visualise()
#
#
# def cluster_to_plot():
#     # RAPPRESENTAZIONE GRAFICA
#     # %%
#     # rappresentazione grafica 2d
#     # PCA
#     pca = PCA(n_components=2)
#     pca = pca.fit_transform(embeddings)
#
#     principalDf = pd.DataFrame(data=pca, columns=['pc1', 'pc2'])
#
#     # %%
#     # Kmeans applicato nuovamente sulle 2 pc per avere relativamente i centri dei cluster nella proiezione 2D
#     # step inutile se non si vuole avere i punti rappresentati sul grafico
#     kmeans2 = KMeans(n_clusters=7)
#     kmeans2.fit(principalDf)
#
#     plt.scatter(principalDf['pc1'], principalDf['pc2'], c=y_kmeans, s=50, cmap='viridis')
#     centers = np.asarray(kmeans2.cluster_centers_)
#     plt.scatter(centers[:, 0], centers[:, 1], c='black', s=200, alpha=0.5)
#
#     # %%
#     # RAPPRESENTAZIONE GRAFICA 3D
#     # PCA
#     pca = PCA(n_components=3)
#     pca = pca.fit_transform(embeddings)
#
#     principalDf = pd.DataFrame(data=pca, columns=['pc1', 'pc2', 'pc3'])
#
#     kmeans2 = KMeans(n_clusters=7)
#     kmeans2.fit(principalDf)
#
#     fig = pyplot.figure()
#     ax = Axes3D(fig)
#     ax.scatter(principalDf['pc1'], principalDf['pc2'], principalDf['pc3'], c=y_kmeans, s=50, cmap='viridis')
#
#     centers = np.asarray(kmeans2.cluster_centers_)
#     ax.scatter(centers[:, 0], centers[:, 1], centers[:, 2], c='black', s=200, alpha=0.5)
#
#
#
