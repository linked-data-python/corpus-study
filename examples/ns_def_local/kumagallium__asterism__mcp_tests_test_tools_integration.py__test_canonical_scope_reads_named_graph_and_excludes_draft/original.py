# Extracted from kumagallium/asterism@f0977d4d3a : mcp/tests/test_tools_integration.py
# region: test_canonical_scope_reads_named_graph_and_excludes_draft (lines 160-179, stratum ns_def_local)
# licence of the source repository: see meta.json
import json
import pytest
import rdflib
from asterism.substrate import (
    CANONICAL_GRAPH_BASE,
    CONTROL_GRAPH_IRI,
    STATUS_PREDICATE,
    STATUS_PROMOTED,
    canonical_graph_iri,
    draft_graph_iri,
    ontology_graph_iri,
)
from asterism_mcp.tools import (
    property_ranking,
    provenance_of,
    sample_search,
    schema_summary,
    sparql_query,
)
SD = DEFAULT_ONTOLOGY

@pytest.mark.filterwarnings("ignore::DeprecationWarning")
async def test_canonical_scope_reads_named_graph_and_excludes_draft() -> None:
    ds = rdflib.Dataset()  # default_union=False: GRAPH-less reads only default
    canon = ds.graph(rdflib.URIRef(canonical_graph_iri("ds1")))
    draft = ds.graph(rdflib.URIRef(draft_graph_iri("ds2")))
    sd = rdflib.Namespace(SD)
    canon.add((rdflib.URIRef("https://ex/s/c1"), rdflib.RDF.type, sd.Sample))
    canon.add((rdflib.URIRef("https://ex/s/c1"), sd.compositionString, rdflib.Literal("CanonComp")))
    draft.add((rdflib.URIRef("https://ex/s/d1"), rdflib.RDF.type, sd.Sample))
    draft.add((rdflib.URIRef("https://ex/s/d1"), sd.compositionString, rdflib.Literal("DraftComp")))
    _flag_promoted(ds, canonical_graph_iri("ds1"))  # ds1 promoted; ds2 is an unflagged draft

    class _C:
        async def sparql_select(self, query: str) -> dict:
            raw = ds.query(query).serialize(format="json")
            return json.loads(raw.decode() if isinstance(raw, bytes) else raw)

    comps = {r["composition"] for r in (await sample_search(_C()))["results"]}
    assert "CanonComp" in comps  # per-dataset canonical named graph IS read
    assert "DraftComp" not in comps  # unreviewed draft graph is excluded from Ask
