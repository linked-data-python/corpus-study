# Extracted from BD2KOnFHIR/fhirtordf@05b23ba1df : tests/issue_tests/test_issue4.py
# region: Issue4TestCase.test_decimal (lines 40-57, stratum trav_navigation)
# licence of the source repository: see meta.json
import unittest
from fhirtordf_shim import loads
from rdflib import URIRef, Literal, XSD
from fhirtordf_shim import FHIR
from fhirtordf_shim import FHIRGraph
json_data = """{
  "resourceType": "VisionPrescription",
  "id": "33123",
  "text": {
    "status": "generated",
    "div": "(cut)"
  },
   "dispense": [
    {
      "product": {
        "coding": [
          {
            "system": "http://hl7.org/fhir/ex-visionprescriptionproduct",
            "code": "lens"
          }
        ]
      },
      "eye": "right",
      "sphere": -2.00,
      "prism": 0.5,
      "base": "down",
      "add": 2.00
    }
  ]
}
  """

@unittest.expectedFailure
def test_decimal(self):
    from fhirtordf_shim import FHIRResource
    g = FHIRResource(FHIRGraph(), None, "http://hl7.org/fhir", loads(json_data)).graph
    # rdflib supports decimal precision if you create the data as a string.
    self.assertNotEqual(Literal("2.00", datatype=XSD.decimal), Literal("2.0", datatype=XSD.decimal))
    self.assertEqual(Literal(2.00), Literal(2.0))

    # FHIR requires that *all* decimals use the first form.  While the diopter example above
    # would work, issues arise in situations where numbers really ARE decimal...
    self.assertEqual(Literal("2.00", datatype=XSD.decimal),
                     g.value(
                         g.value(
                             g.value(URIRef("http://hl7.org/fhir/VisionPrescription/33123"),
                                     FHIR.VisionPrescription.dispense),
                             FHIR.VisionPrescription.dispense.add), FHIR.value))
