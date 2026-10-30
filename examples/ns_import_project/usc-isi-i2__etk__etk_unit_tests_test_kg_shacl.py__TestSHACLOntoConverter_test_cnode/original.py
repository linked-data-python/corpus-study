# Extracted from usc-isi-i2/etk@2084003ae7 : etk/unit_tests/test_kg_shacl.py
# region: TestSHACLOntoConverter.test_cnode (lines 104-119, stratum ns_import_project)
# licence of the source repository: see meta.json
import rdflib
from etk_context import SH, SHACL, SHACLOntoConverter
from etk_context import URI, BNode, Literal, LiteralType

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


# Demo harness (identical on both sides, see meta.json): test_cnode's own
# `self` needs the unittest assert methods (self.assertIsInstance,
# self.assertEqual, self.assertNotEqual) -- a plain unittest.TestCase
# instance provides exactly those, with no other dependency on the real
# etk.unit_tests.test_kg_shacl.TestSHACLOntoConverter class (verified
# against the pinned commit: TestSHACLOntoConverter has no setUp/fixtures
# this test relies on). Restores the binding the extraction lost
# (AGENT_BATCH's "163 regions" case) without touching the region body.
# `case` lets the driver pass a TestCase that records every assert* call
# (identical on both sides); demo() alone keeps the original behaviour.
import unittest


def demo(case=None):
    case = case if case is not None else unittest.TestCase()
    test_cnode(case)
    return "ok"
