import rdflib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix

from graph import *
from rdf2vec import RDF2VecTransformer


print(end='Loading data... ', flush=True)
g = rdflib.Graph()
g.parse('data/limi1000.rdf')
print('OK')

test_data = pd.read_csv('data/sparql.tsv', sep='\t')
#train_data = pd.read_csv('data/AIFB_train.tsv', sep='\t')

test = [rdflib.URIRef(x) for x in test_data['s']]
#train_labels = train_data['label_affiliation']

print(test)

#test_people = [rdflib.URIRef(x) for x in test_data['person']]
#test_labels = test_data['label_affiliation']

label_predicates = [
    rdflib.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
]

# Extract the train and test graphs

kg = rdflib_to_kg(g, label_predicates=label_predicates)

#train_graphs = [extract_instance(kg, person) for person in train_people]
test_graphs = []
for person in test:
    try:
        test_graphs.append(extract_instance(kg, person))
    except Exception:
        print('lol')


transformer = RDF2VecTransformer(_type='walk', walks_per_graph=500)
embeddings = transformer.fit_transform(test_graphs)

#train_embeddings = embeddings[:len(train_graphs)]
#test_embeddings = embeddings[len(train_graphs):]

for t in embeddings:
    print(len(t))

'''
rf = RandomForestClassifier(n_estimators=100)
rf.fit(train_embeddings, train_labels)

print(confusion_matrix(test_labels, rf.predict(test_embeddings)))
'''
