# Extracted from hidden-graph/rdflib-starlight@b7973da2b5 : tests/integration/test_oxigraph_backend.py
# region: TestOxigraphRoundTrip.test_contains (lines 133-137, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import URIRef, Literal
EX       = 'http://example.org/'

def test_contains(self, sg):
    triple = (URIRef(EX+'alice'), URIRef(EX+'knows'), URIRef(EX+'bob'))
    assert triple not in sg
    sg.add(triple)
    assert triple in sg
