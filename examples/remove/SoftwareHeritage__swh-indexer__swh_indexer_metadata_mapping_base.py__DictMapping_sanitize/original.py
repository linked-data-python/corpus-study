# Extracted from SoftwareHeritage/swh-indexer@95f3e65462 : swh/indexer/metadata_mapping/base.py
# region: DictMapping.sanitize (lines 349-360, stratum remove)
# licence of the source repository: see meta.json
import logging
import rdflib

def sanitize(self, graph: rdflib.Graph) -> None:
    # Remove triples that make PyLD crash
    for subject, predicate, _ in graph.triples((None, None, rdflib.URIRef(""))):
        graph.remove((subject, predicate, rdflib.URIRef("")))

    # Should not happen, but we's better check as this may lead to incorrect data
    invalid = False
    for triple in graph.triples((rdflib.URIRef(""), None, None)):
        invalid = True
        logging.error("Empty triple subject URI: %r", triple)
    if invalid:
        raise ValueError("Empty triple subject(s)")
