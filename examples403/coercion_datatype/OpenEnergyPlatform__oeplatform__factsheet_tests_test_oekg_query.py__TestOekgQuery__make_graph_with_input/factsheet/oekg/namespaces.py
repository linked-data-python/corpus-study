# Context shim (see meta.json): copied verbatim from
# OpenEnergyPlatform/oeplatform@ff28ef6390 factsheet/oekg/namespaces.py, so
# the region executes outside the package. Identical bindings for both
# representations. bind_all_namespaces is never called by this region and is
# dropped (it only binds prefixes onto a graph for serialisation).
from rdflib.namespace import Namespace

OEO = Namespace("https://openenergyplatform.org/ontology/oeo/")
OBO = Namespace("http://purl.obolibrary.org/obo/")
DC = Namespace("http://purl.org/dc/terms/")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
NPG = Namespace("http://ns.nature.com/terms/")
SCHEMA = Namespace("https://schema.org/")
OEKG = Namespace("https://openenergyplatform.org/ontology/oekg/")
DBO = Namespace("http://dbpedia.org/ontology/")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
OBO = Namespace("http://purl.obolibrary.org/obo/")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
