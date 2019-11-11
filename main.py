import rdflib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from mpl_toolkits.mplot3d import Axes3D

from graph import *
from rdf2vec import RDF2VecTransformer


def foo():
    print(end='Loading data... ', flush=True)
    g = rdflib.Graph()
    g.parse('data/limit10000', type="nt")
    print('OK')

    # Extract all database drugs' URI
    all_drugs_file = pd.read_csv('data/all_drugs.tsv', sep='\t')
    all_drugs = [rdflib.URIRef(x) for x in all_drugs_file['drug']]

    # Define relevant predicates
    predicates = pd.read_csv('data/relevant_predicates.tsv', sep='\t')
    predicates = [rdflib.URIRef(x) for x in predicates['predicate']]

    # Extract graph
    kg = rdflib_to_kg(g, label_predicates=predicates)

    graphs = []
    for drug in all_drugs:
        try:
            graphs.append(extract_instance(kg, drug))
        except Exception:
            pass

    # Embeddings
    transformer = RDF2VecTransformer(_type='walk', walks_per_graph=500)
    embeddings = transformer.fit_transform(graphs)

    kmeans = KMeans(n_clusters=7)
    kmeans.fit(embeddings)
    y_kmeans = kmeans.predict(embeddings)

    # test con alcune entry (?)

    # PCA
    pca = PCA(n_components=2)
    pca = pca.fit_transform(embeddings)

    principalDf = pd.DataFrame(data=pca, columns=['principal component 1', 'principal component 2'])

    # rappresentazione grafica
    plt.scatter(principalDf[:, 0], principalDf[:, 1], c=y_kmeans, s=50, cmap='viridis')

    centers = kmeans.cluster_centers_
    plt.scatter(centers[:, 0], centers[:, 1], c='black', s=200, alpha=0.5)



if __name__ == "__main__":
    foo()
