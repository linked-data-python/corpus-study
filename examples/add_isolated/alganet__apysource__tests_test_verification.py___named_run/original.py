# Extracted from alganet/apysource@f800ec97c1 : tests/test_verification.py
# region: _named_run (lines 820-837, stratum add_isolated)
# licence of the source repository: see meta.json
from unittest.mock import patch
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import PROV, RDF, RDFS
from apysource.namespaces import OA, SCHEMA, SV
from apysource.results import (
    CheckResult,
    Failure,
    FetcherResult,
    RepoResult,
    Supersession,
    TextOutcome,
)
from apysource.verification import (
    failed,
    json_report,
    print_report,
    run_checks,
    strip_headers,
    verdict,
)
from tests.conftest import EMPTY_REGISTRY, MockFetcher, build_chain_graph

def _named_run(source_label, frag_label, url, snippet=None, text="x" * 100):
    frag = URIRef("http://x/frag")
    src = URIRef("http://x/src")
    g = build_chain_graph(frag, src, url, location="", label=frag_label)
    g.set((src, RDFS.label, Literal(source_label)))
    if snippet is not None:
        target = next(g.objects(frag, OA.hasTarget))
        sel = BNode()
        g.add((target, OA.hasSelector, sel))
        g.add((sel, RDF.type, OA.TextQuoteSelector))
        g.add((sel, OA.exact, Literal(snippet)))

    checks_config = [{"name": "Fragments", "class_uri": SV.Fragment, "mode": "chain"}]
    with patch("apysource.verification.load_text",
               return_value=TextOutcome(text)):
        results = run_checks(g, checks_config, EMPTY_REGISTRY,
                             fetcher=MockFetcher())
    return {c.name: c for c in results}
