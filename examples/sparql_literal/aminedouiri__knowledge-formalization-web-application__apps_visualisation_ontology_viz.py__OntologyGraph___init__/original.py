# Extracted from aminedouiri/knowledge-formalization-web-application@0a8007ff46 : apps/visualisation/ontology_viz.py
# region: OntologyGraph.__init__ (lines 27-46, stratum sparql_literal)
# licence of the source repository: see meta.json
from collections import defaultdict
from rdflib import Graph, URIRef, Literal, BNode
from namespace import NamespaceManager, split_uri
query_classes = prepareQuery("""
SELECT ?s {
  { ?s a owl:Class } UNION
  { ?s owl:subClassOf+ ?o . ?o a owl:Class . }
} """, initNs={'owl': OWL})
query_properties = prepareQuery("""
SELECT ?s {
  { ?s a ?property } UNION { ?s owl:subPropertyOf+ ?o . ?o a ?property }
  FILTER ( ?property IN ( owl:DatatypeProperty, owl:ObjectProperty ) )
} """, initNs={'owl': OWL})

def __init__(self, files, config, format='ttl', ontology=None):
    self.g = Graph()
    self.g.namespace_manager = NamespaceManager(self.g)
    if ontology is not None:
        g = Graph()
        self._load_files(g, ontology)
        self.ontology_defined = True
        self.ontology_cls = {cls for cls, in g.query(query_classes)}
        self.ontology_pty = {pty for pty, in g.query(query_properties)}
    else:
        self.ontology_defined = False
    self.config = config
    self._load_files(self.g, files, format)
    self.classes = set()
    self.instances = dict()
    self.edges = set()
    self.labels = dict()
    self.tooltips = defaultdict(list)
    self.literals = set()
    self._read_graph()
