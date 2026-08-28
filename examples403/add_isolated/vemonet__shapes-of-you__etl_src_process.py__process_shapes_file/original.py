# Extracted from vemonet/shapes-of-you@cf8efe48ef : etl/src/process.py
# region: process_shapes_file (lines 283-297, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import RDF, ConjunctiveGraph, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DC, DCTERMS, OWL, RDFS, SKOS, VOID, XSD
from src.config import CSVW, DCAT, NP_TEMPLATE, R2RML, RML, SCHEMA, SH, SHEX, SIO

for shape_file in g.subjects(RDF.type, DCAT.Dataset):
    shape_found = True
    shapes_graph.add((file_uri, RDF.type, SCHEMA['SoftwareSourceCode']))
    shapes_graph.add((file_uri, RDF.type, DCAT.Dataset))
    shapes_graph.add((file_uri, RDFS.label, Literal(rdf_file_path.name)))
    shapes_graph.add((file_uri, SCHEMA.codeRepository, URIRef(repo_url)))
    # Get file label
    for file_label in g.objects(shape_file, RDFS.label):
      shapes_graph.add((file_uri, RDFS.comment, Literal(str(file_label))))
      break
    for sparql_endpoint in g.objects(None, VOID.sparqlEndpoint):
      shapes_graph.add((file_uri, VOID.sparqlEndpoint, URIRef(sparql_endpoint)))
      # TODO: currently break to only add 1 if multiple, multi endpoints need to be checked
      # TODO: test it with GSS-Cogs/csvw-example DCAT datasets
      break
