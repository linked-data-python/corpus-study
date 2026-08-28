# Extracted from kumagallium/asterism@f0977d4d3a : ingest/tests/test_substrate.py
# region: test_from_merge_enables_cross_dataset_join (lines 1416-1439, stratum sparql_interpolated)
# licence of the source repository: see meta.json
import pytest
import rdflib
from asterism.substrate import (
    CANONICAL_GRAPH_BASE,
    GRAPH_BASE,
    ONTOLOGY_GRAPH_BASE,
    absolutize_rml_sources,
    alignment_report,
    batch_fingerprint,
    canonical_graph_iri,
    classify_alignment,
    count_nt_lines,
    draft_graph_iri,
    ingest_graph_to_oxigraph,
    materialize_to_graph,
    materialize_to_nt_file,
    normalize_dialect_sources,
    ontology_graph_iri,
    rml_source_names,
    run_append_ingest,
    run_id_for_batch,
    run_substrate_ingest,
    stream_nt_file_to_oxigraph,
    versioned_graph_iri,
)

@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_from_merge_enables_cross_dataset_join() -> None:
    """The point of FROM-merge: a join whose two facts live in DIFFERENT canonical
    graphs resolves once the graphs are merged via FROM (cross-dataset linking)."""
    from asterism.substrate import canonical_from_clauses, canonical_graph_iri

    ds = rdflib.Dataset()
    ex = rdflib.Namespace("https://ex/")
    g_a = rdflib.URIRef(canonical_graph_iri("a"))
    g_b = rdflib.URIRef(canonical_graph_iri("b"))
    ds.graph(g_a).add((ex.sample1, ex.madeOf, ex.bismuth))  # dataset A
    ds.graph(g_b).add((ex.bismuth, rdflib.RDFS.label, rdflib.Literal("Bismuth")))  # dataset B

    body = "WHERE { ?s <https://ex/madeOf> ?e . ?e rdfs:label ?l }"
    prefix = "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n"

    # Without FROM (default graph only), the cross-graph join finds nothing.
    none = list(ds.query(prefix + "SELECT ?l " + body))
    assert none == []

    # With FROM over both canonical graphs, the join across A and B resolves.
    frm = canonical_from_clauses([str(g_a), str(g_b)])
    rows = list(ds.query(prefix + "SELECT ?l " + frm + body))
    assert len(rows) == 1 and str(rows[0][0]) == "Bismuth"
