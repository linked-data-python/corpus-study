# Extracted from TDCC-NES/askwol@3534557e8b : tests/test_imports_check.py
# region: test_imports_ignores_non_uri_objects (lines 86-95, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
import pytest
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import OWL, RDF
from askwol.cache import OntologyCache
from askwol.imports_check import check_imports
from askwol.models import Status
ONT = URIRef("https://example.org/ont")

@pytest.mark.asyncio
async def test_imports_ignores_non_uri_objects():
    g = Graph()
    g.add((ONT, RDF.type, OWL.Ontology))
    g.add((ONT, OWL.imports, Literal("not a uri")))

    report = await check_imports(g, OntologyCache())

    assert report.status == Status.OK
    assert report.checks == []
