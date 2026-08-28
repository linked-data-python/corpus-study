# Extracted from BD2KOnFHIR/fhirtordf@05b23ba1df : tests/rdfsupport_tests/test_fhirgraphutils.py
# region: FHIRGraphUtilsTestCase.test_value (lines 17-32, stratum trav_single_value)
# licence of the source repository: see meta.json
import os
from datetime import date, datetime
from rdflib import Graph, URIRef, Literal
from fhirtordf.rdfsupport.namespaces import FHIR

def test_value(self):
    from fhirtordf.rdfsupport.fhirgraphutils import value
    g = Graph()
    g.load(os.path.join(self.base_dir, "account-example.ttl"), format="turtle")
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
