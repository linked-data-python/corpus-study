# Extracted from usc-isi-i2/etk@2084003ae7 : etk/unit_tests/test_kg_shacl.py
# region: TestSHACLOntoConverter.test_cnode (lines 104-119, stratum ns_import_project)
# licence of the source repository: see meta.json
import rdflib
from etk.knowledge_graph.shacl import SH, SHACL, SHACLOntoConverter
from etk.knowledge_graph.node import URI, BNode, Literal, LiteralType

def test_cnode(self):
    converter = SHACLOntoConverter()
    c1 = rdflib.URIRef('http://example.org/Person')
    c2 = rdflib.URIRef('http://example.org/Developer')
    cnode1 = converter.cnode(c1)
    cnode2 = converter.cnode('http://example.org/Person')
    cnode3 = converter.cnode(c2)
    self.assertIsInstance(cnode1, BNode)
    self.assertIsInstance(cnode2, BNode)
    self.assertIsInstance(cnode3, BNode)
    self.assertEqual(cnode1, cnode2)
    self.assertNotEqual(cnode1, cnode3)

    converter = SHACLOntoConverter({str(c1): URI(':Person')})
    cnode4 = converter.cnode(c1)
    self.assertEqual(cnode4, URI(':Person'))
