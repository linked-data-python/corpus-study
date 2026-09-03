# Extracted from BD2KOnFHIR/fhirtordf@05b23ba1df : tests/rdfsupport_tests/test_fhirgraphutils.py
# region: FHIRGraphUtilsTestCase.test_value (lines 17-32, stratum trav_single_value)
# licence of the source repository: see meta.json
#
# Test harness only (see meta.json): FHIRGraphUtilsTestCase.test_value is a
# unittest.TestCase method that only ever asserts and returns None, and it
# needs `self.base_dir` (bound in the real class's setUpClass) which the
# extracted method no longer has -- driver.py supplies a minimal real
# unittest.TestCase instance, the same convention this study already uses
# for examples/trav_one_step/INM-6__alpaca__.../test_provenance_annotation_multiple_returns.
# `demo` turns a failed assertion into a comparable value instead of
# letting it abort the driver, same convention as that example.
#
# `g.load(...)` -> `g.parse(...)`: `Graph.load` was a deprecated alias for
# `Graph.parse`, removed in the rdflib version this study is pinned to
# (7.2.1) -- same rename on both sides, no RDF meaning changed (same
# finding already made for examples/sparql_interpolated/SynBioDex__sbol_factory__custom_eval.py__<module>_1).
#
# "account-example.ttl" -> "fixture.ttl": the real fixture file on disk is
# not part of this region's captured context; fixture.ttl (this directory)
# is the corpus/405 reading oracle's own authored input graph -- same
# rename on both sides, no RDF meaning changed.
#
# `value()` (imported from fhirtordf.rdfsupport.fhirgraphutils) is NOT part
# of this region: it is a module-level helper defined elsewhere in
# fhirgraphutils.py that the region only calls -- restored verbatim in the
# context shim (see meta.json) and left as plain rdflib code, identically
# on both sides, the same convention as `_term_label` in
# mapsa__blathers__src_blathers_extract.py___extract_nested_node.
import os
from datetime import date, datetime
from rdflib import Graph, URIRef, Literal
from fhirtordf.rdfsupport.namespaces import FHIR

def test_value(self):
    from fhirtordf.rdfsupport.fhirgraphutils import value
    g = Graph()
    g.parse(os.path.join(self.base_dir, "fixture.ttl"), format="turtle")
    s = FHIR['Account/example']
    self.assertEqual("example", value(g, s, FHIR.Resource.id))
    self.assertEqual(Literal("example"), value(g, s, FHIR.Resource.id, True))
    self.assertEqual(FHIR.treeRoot, value(g, s, FHIR.nodeRole))
    period = g.value(s, FHIR.Account.servicePeriod)
    self.assertIsNotNone(period)
    self.assertEqual(date(2016, 1, 1), value(g, period, FHIR.Period.start))
    period_end = g.value(period, FHIR.Period.end)
    self.assertIsNotNone(period_end)
    self.assertEqual(date(2016, 6, 30), value(g, period_end, FHIR.value))
    self.assertIsNone(value(g, s, FHIR.Account.type))
    self.assertIsNone(value(g, s, FHIR.foo))


def demo(self) -> object:
    try:
        test_value(self)
        return "ok"
    except AssertionError as e:
        return ("assertion-failed", str(e))
