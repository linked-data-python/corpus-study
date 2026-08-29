# Extracted from IndustryFusion/DigitalTwin@3b40088b88 : semantic-model/opcua/tests/test_libshacl.py
# region: TestShaclAdditional.test_create_datatype_and_iri_shapes_and_shacl_or (lines 89-125, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, SH, XSD
from rdflib.collection import Collection

def test_create_datatype_and_iri_shapes_and_shacl_or(self):
    # datatype shapes
    dt_nodes = self.sh.create_datatype_shapes([XSD.boolean, XSD.double])
    self.assertEqual(len(dt_nodes), 2)
    # each node should have a precise datatype triple
    expected = {XSD.boolean, XSD.double}
    seen = set()
    for n in dt_nodes:
        for _, _, dt in self.sh.shaclg.triples((n, SH.datatype, None)):
            seen.add(dt)
    self.assertEqual(seen, expected)

    # IRI shapes
    iri_nodes = self.sh.create_iri_shape()
    self.assertEqual(len(iri_nodes), 1)
    n = iri_nodes[0]
    self.assertIn((n, SH.nodeKind, SH.IRI), list(self.sh.shaclg))

    # shacl_or: single
    single = BNode()
    # inject a triple
    self.sh.shaclg.add((single, SH.datatype, XSD.string))
    single_tup = self.sh.shacl_or([single])
    # should return one tuple for the single shape
    self.assertEqual(single_tup, [(SH.datatype, XSD.string)])
    # and remove the triple from graph
    self.assertNotIn((single, SH.datatype, XSD.string), self.sh.shaclg)

    # multiple
    a = BNode(); b = BNode()
    self.sh.shaclg.add((a, SH.nodeKind, SH.Literal))
    self.sh.shaclg.add((b, SH.nodeKind, SH.Literal))
    or_tup = self.sh.shacl_or([a,b])
    pred, obj = or_tup[0]
    self.assertEqual(pred, SH['or'])
    lst = list(Collection(self.sh.shaclg, obj))
    self.assertCountEqual(lst, [a, b])
