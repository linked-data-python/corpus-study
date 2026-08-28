# Extracted from OpenEnergyPlatform/oeplatform@ff28ef6390 : factsheet/tests/test_oekg_query.py
# region: TestOekgQuery._make_graph_with_input (lines 18-28, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import RDF, Graph, Literal, URIRef
from factsheet.oekg import namespaces

def _make_graph_with_input(self, table_iri_literal: str):
    g = Graph()
    bundle = URIRef("https://oekg.test/bundle1")
    scenario = URIRef("https://oekg.test/scenario/A")
    input_ds = URIRef("https://oekg.test/dataset/in1")

    g.add((bundle, RDF.type, namespaces.OEO.OEO_00020227))
    g.add((bundle, namespaces.OBO.BFO_0000051, scenario))
    g.add((scenario, namespaces.OEO.OEO_00020437, input_ds))
    g.add((input_ds, namespaces.OEO.OEO_00390094, Literal(table_iri_literal)))
    return g, bundle, scenario
