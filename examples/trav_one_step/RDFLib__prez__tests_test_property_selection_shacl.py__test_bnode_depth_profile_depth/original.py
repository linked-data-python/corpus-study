# Extracted from RDFLib/prez@421ee0a9fe : tests/test_property_selection_shacl.py
# region: test_bnode_depth_profile_depth (lines 346-364, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib import DCTERMS, PROV, RDF, SH, Graph, URIRef, SKOS
from sparql_grammar_pydantic import (
    IRI,
    Filter,
    GroupOrUnionGraphPattern,
    OptionalGraphPattern,
    TriplesSameSubject,
    TriplesSameSubjectPath,
    Var,
)
from prez.services.query_generation.shacl import PropertyShape

def test_bnode_depth_profile_depth():
    g = Graph().parse(
        data="""
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX reg: <http://purl.org/linked-data/registry#>
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX shext: <http://example.com/shacl-extension#>

    <http://example-profile> sh:property [
        sh:path [ shext:bNodeDepth "25" ]
        ]
    .
    """
    )
    path_bn = g.value(subject=URIRef("http://example-profile"), predicate=SH.property)
    ps = PropertyShape(
        uri=path_bn, graph=g, kind="profile", focus_node=Var(value="focus_node")
    )
