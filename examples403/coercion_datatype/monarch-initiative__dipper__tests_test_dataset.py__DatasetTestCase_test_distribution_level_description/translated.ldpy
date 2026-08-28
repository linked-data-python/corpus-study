# Extracted from monarch-initiative/dipper@bf0a86c447 : tests/test_dataset.py
# region: DatasetTestCase.test_distribution_level_description (lines 362-367, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import URIRef, Literal, Graph

def test_distribution_level_description(self):
    triples = list(self.dataset.graph.triples(
        (self.distribution_level_IRI_ttl, self.iri_description,
         Literal(self.ingest_description))))
    self.assertTrue(len(triples) == 1,
                    "missing version level type description triple")
