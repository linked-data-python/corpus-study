# Extracted from DataDrivenCPS/acquirium@e3bffb4bed : tests/unit/test_csv_ingest.py
# region: test_loop_mints_valid_dummy_point_uri_for_messy_ref_name (lines 403-418, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, URIRef
from acquirium.internals.models import compute_ref_uri
from acquirium.internals.internals_namespaces import (
    ACQUIRIUM_REF_NAME,
    ACQUIRIUM_SOURCE_ID,
    ACQUIRIUM_VALUE_KIND,
    HAS_EXTERNAL_REFERENCE,
)

def test_loop_mints_valid_dummy_point_uri_for_messy_ref_name(tmp_path):
    """A ref_name full of URI-hostile characters still yields a valid dummy point URI."""
    p = tmp_path / "bad_uri.csv"
    p.write_text("time,UV-Ultraviolet Intensity (mW/cm^2)\n2024-01-01T00:00:00Z,1.0\n")
    driver = make_driver(tmp_path=tmp_path)
    driver.tick()

    g = Graph().parse(data=driver.aq.client.insert_graph.call_args[0][0], format="turtle")
    source_id = "csv_files"
    ref_name = "UV-Ultraviolet Intensity (mW/cm^2)"
    ref_uri = compute_ref_uri(source_id, ref_name)
    assert (ref_uri, ACQUIRIUM_SOURCE_ID, Literal(source_id)) in g
    assert (ref_uri, ACQUIRIUM_REF_NAME, Literal(ref_name)) in g
    assert (ref_uri, ACQUIRIUM_VALUE_KIND, Literal("numeric")) in g
    points = list(g.subjects(HAS_EXTERNAL_REFERENCE, ref_uri))
    assert points == [URIRef(f"{ref_uri}__point")]
