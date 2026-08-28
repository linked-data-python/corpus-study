# Extracted from ktbs/ktbs@4f9f50c770 : utest/test_ktbs_engine.py
# region: TestObsels.test_create_no_timestamp (lines 525-537, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, RDF, RDFS, URIRef
from datetime import datetime, timedelta
from rdfrest.util.iso8601 import UTC
from ktbs.namespace import KTBS

def test_create_no_timestamp(self, epsilon=0.5):
    g = Graph()
    obs = BNode()
    g.add((obs, RDF.type, self.ot.uri))
    g.add((obs, KTBS.hasTrace, self.trace.uri))
    uris = self.trace.post_graph(g)
    now = datetime.now(UTC)
    assert len(uris) == 1
    obs = self.trace.get_obsel(uris[0])
    begin_dt = self.epoch + timedelta(milliseconds=obs.begin)
    delta = now - begin_dt
    assert abs(delta.total_seconds()) < epsilon
    assert obs.end == obs.begin
