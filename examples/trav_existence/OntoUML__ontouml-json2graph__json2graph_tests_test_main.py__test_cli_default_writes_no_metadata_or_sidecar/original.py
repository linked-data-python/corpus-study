# Extracted from OntoUML/ontouml-json2graph@982f12b9c4 : json2graph/tests/test_main.py
# region: test_cli_default_writes_no_metadata_or_sidecar (lines 1774-1783, stratum trav_existence)
# licence of the source repository: see meta.json
from pathlib import Path
from rdflib import RDF, RDFS, XSD, Graph, Literal, Namespace, URIRef
from context_shim import write_cardinality_project, run_metadata_cli  # context shim -- see meta.json
PROV = Namespace("http://www.w3.org/ns/prov#")

def test_cli_default_writes_no_metadata_or_sidecar(tmp_path: Path) -> None:
    """Verify that omitting the new CLI option preserves metadata-free output."""
    input_file = write_cardinality_project(tmp_path, "0..1")

    result = run_metadata_cli(input_file, tmp_path)

    assert result.returncode == 0, result.stderr
    output_graph = Graph().parse(tmp_path / "cardinality.ttl", format="turtle")
    assert not any(output_graph.triples((None, RDF.type, PROV.Entity)))
    assert not (tmp_path / "cardinality.provenance.ttl").exists()


# Demo harness (identical on both sides, see meta.json): the region is a
# pytest test that only ever asserts. To exercise the FALSE / zero-solution
# side of `bool(m{ })` as well as the TRUE side (the trav_existence stratum
# is only half-shown by a test that always passes -- the real upstream test
# only ever writes metadata-free output), `demo` calls the region and turns
# a failed assertion into a comparable value instead of letting it
# propagate -- an uncaught AssertionError would abort the driver on the
# first non-matching case rather than let both sides be compared.
def demo(tmp_path: Path) -> object:
    try:
        test_cli_default_writes_no_metadata_or_sidecar(tmp_path)
        return "ok"
    except AssertionError as e:
        return ("assertion-failed", str(e))
