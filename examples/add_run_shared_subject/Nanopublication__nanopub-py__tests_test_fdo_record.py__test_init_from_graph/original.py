# Extracted from Nanopublication/nanopub-py@05022dc4bc : tests/test_fdo_record.py
# region: test_init_from_graph (lines 25-34, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDFS, DCTERMS
from nanopub.fdo.fdo_record import FdoRecord
PROFILE_URI = "https://hdl.handle.net/21.T11966/abc123"
LABEL = "Example FDO"

def test_init_from_graph():
    g = Graph()
    subj = URIRef("https://hdl.handle.net/21.T11966/abc123")
    g.add((subj, DCTERMS.conformsTo, URIRef(PROFILE_URI)))
    g.add((subj, RDFS.label, Literal(LABEL)))
    record = FdoRecord(assertion=g)

    assert record.get_profile() == URIRef(PROFILE_URI)
    assert record.get_label() == LABEL
    assert record.get_id() == subj
