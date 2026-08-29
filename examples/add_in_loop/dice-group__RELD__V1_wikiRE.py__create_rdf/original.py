# Extracted from dice-group/RELD@7ca93acbb6 : V1/wikiRE.py
# region: create_rdf (lines 193-198, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib.namespace import DC, DCTERMS, DOAP, FOAF, SKOS, OWL, RDF, RDFS, VOID, XMLNS, XSD
from rdflib import Graph, URIRef, Literal, Namespace # here is some error
g = Graph()
res = Namespace("https://reld.dice-research.org/resource/")

if str(nyt) != 'nan':
    nytid = rel_data.loc[rel_data['RE-NYT-Relation'] == nyt, 'Nrid'].iloc[0]
    g.add((URIRef(relation), # nyt
      OWL.sameAs, 
      URIRef(res+"R-"+str(nytid))
     ))
