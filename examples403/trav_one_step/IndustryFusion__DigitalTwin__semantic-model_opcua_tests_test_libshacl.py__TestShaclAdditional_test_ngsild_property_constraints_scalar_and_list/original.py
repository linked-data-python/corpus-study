# Extracted from IndustryFusion/DigitalTwin@3b40088b88 : semantic-model/opcua/tests/test_libshacl.py
# region: TestShaclAdditional.test_ngsild_property_constraints_scalar_and_list (lines 58-87, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, SH, XSD
from rdflib.collection import Collection

def test_ngsild_property_constraints_scalar_and_list(self):
    # scalar: value_rank None, no JSON, literal path
    self.sh.shaclg = Graph()  # reset
    shapes = self.sh.get_ngsild_property_constraints(
        value_rank=None, array_dimensions=None,
        datatype=[XSD.integer], pattern=None,
        is_iri=False, contentclass=None
    )
    # should produce at least one property‐shape (scalar)
    self.assertTrue(len(shapes) >= 1)
    inner = next(self.sh.shaclg.objects(shapes[0], SH.property))
    self.assertIn((inner, SH.path, self.sh.ngsildns['hasValue']), list(self.sh.shaclg))

    # list: force list by non‐negative value_rank
    self.sh.shaclg = Graph()
    # create array_dimensions
    arr = BNode()
    Collection(self.data_graph, arr, [Literal(3)])
    shapes2 = self.sh.get_ngsild_property_constraints(
        value_rank=Literal(0), array_dimensions=arr,
        datatype=[XSD.string], pattern=None,
        is_iri=False, contentclass=None
    )
    # should include a property‐shape with SH.path → ngsi-ld:hasListValue
    found = False
    for s in shapes2:
        inner = next(self.sh.shaclg.objects(s, SH.property))
        if (inner, SH.path, self.sh.ngsildns['hasValueList']) in self.sh.shaclg:
            found = True
    self.assertTrue(found)
