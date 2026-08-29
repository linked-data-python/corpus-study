# Extracted from matthiasprobst/h5RDMtoolbox@1baa9284dc : tests/ld/test_ld.py
# region: TestLinkedData.test_serialize_multiple_types (lines 174-189, stratum sparql_literal)
# licence of the source repository: see meta.json
import rdflib
from ontolutils.namespacelib import M4I
import h5rdmtoolbox as h5tbx

def test_serialize_multiple_types(self):
    with h5tbx.File() as h5:
        h5.rdf.type = [M4I.Tool, 'https://www.wikidata.org/wiki/Q1058834']
    ttl = h5tbx.serialize(h5.hdf_filename, fmt="ttl", structural=False)
    sparql_query = """SELECT ?type
    WHERE {
        ?s a ?type
    }
    """
    g = rdflib.Graph()
    g.parse(data=ttl, format="ttl")
    res = g.query(sparql_query)
    self.assertEqual(
        sorted(b[rdflib.Variable("type")] for b in res.bindings),
        sorted([rdflib.URIRef(uri) for uri in [M4I.Tool, 'https://www.wikidata.org/wiki/Q1058834']])
    )
