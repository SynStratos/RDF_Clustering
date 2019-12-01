from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://bio2rdf.org/sparql")
sparql.setQuery("""
    construct{ ?s ?p ?o.
    ?p ?pp ?ok.
    ?o ?po ?oo.}
    where {?s ?p ?o.
    {select distinct ?s where{?s a ?<http://bio2rdf.org/drugbank_vocabulary:Drug>.}}
    optional {?o ?po ?oo.}
    optional {?p ?pp ?ok.}
    }
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()


print(results)

for result in results["results"]["bindings"]:
    print(result["label"]["value"])