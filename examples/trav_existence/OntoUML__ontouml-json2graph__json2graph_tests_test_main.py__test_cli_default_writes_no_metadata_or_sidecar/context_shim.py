# Context shim (see meta.json): stand-in for two module-level test helpers
# from json2graph/tests/test_main.py in OntoUML/ontouml-json2graph@982f12b9c4
# that this region calls but the extraction does not carry:
# `write_cardinality_project` (writes an input JSON project file) and
# `run_metadata_cli` (shells out to `python -m json2graph.decode` as a
# subprocess). Running the real CLI package is out of scope for a region
# whose own graded construction is the trav_existence read three lines
# below it (`not any(output_graph.triples((None, RDF.type, PROV.Entity)))`)
# -- the CLI invocation is scaffolding that produces a Turtle file, not an
# RDF operation itself (categories in meta.json: graph_ctor 1, graph_read 1,
# namespace_term 2 -- exactly the parse + the read under test).
#
# The shim keeps the CALL SHAPE identical to the real helpers --
# `write_cardinality_project` still returns a Path, `run_metadata_cli`
# still returns an object with `.returncode`/`.stderr` -- but instead of
# running the package it copies a Turtle fixture, chosen by a marker file
# the driver drops into `output_directory` beforehand, to
# `output_directory / "cardinality.ttl"`. This lets the driver control
# whether the region's own read sees a graph WITH or WITHOUT a
# `prov:Entity` triple, which the single upstream test (always the
# metadata-free path) never varies.
import shutil
from pathlib import Path


class _CompletedProcess:
    def __init__(self, returncode: int = 0, stderr: str = ""):
        self.returncode = returncode
        self.stderr = stderr


def write_cardinality_project(tmp_path: Path, cardinality: str) -> Path:
    input_file = tmp_path / "cardinality.json"
    input_file.write_text("{}", encoding="utf-8")
    return input_file


def run_metadata_cli(input_file: Path, output_directory: Path, mode=None):
    marker = output_directory / "_use_prov_fixture"
    fixture_name = "fixture_with_prov.ttl" if marker.exists() else "fixture.ttl"
    src = Path(__file__).resolve().parent / fixture_name
    shutil.copyfile(src, output_directory / "cardinality.ttl")
    return _CompletedProcess(returncode=0, stderr="")
