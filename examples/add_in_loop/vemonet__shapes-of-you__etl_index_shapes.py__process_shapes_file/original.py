# Extracted from vemonet/shapes-of-you@cf8efe48ef : etl/index_shapes.py
# region: process_shapes_file (lines 806-812, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import RDF, ConjunctiveGraph, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DC, DCTERMS, OWL, RDFS, SKOS, VOID, XSD
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
SHEX = Namespace("http://www.w3.org/ns/shex#")
SCHEMA = Namespace("https://schema.org/")

for shape in g.subjects(RDF.type, SHEX.ShapeAnd):
    shape_found = True
    shapes_graph.add((file_uri, RDF.type, SCHEMA['SoftwareSourceCode']))
    shapes_graph.add((file_uri, RDF.type, SHEX.Schema))
    shapes_graph.add((file_uri, RDFS.label, Literal(rdf_file_path.name)))
    shapes_graph.add((file_uri, SCHEMA.codeRepository, URIRef(repo_url)))
    shapes_graph = add_shape(g, shapes_graph, file_uri, shape)
