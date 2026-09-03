# Context shim (see meta.json): stand-in for module-level helpers this
# region calls but the extraction does not carry, from
# json2graph/tests/test_main.py in OntoUML/ontouml-json2graph@982f12b9c4:
#
# - `write_text_shape_project` (writes an input JSON project describing a
#   diagrammatic Text shape) -- a sibling test helper defined earlier in
#   the same test_main.py, not part of this region's own line range.
# - `decode_ontouml_json2graph` / `write_graph_file` (the package's own
#   JSON->RDF decoder), imported in the real file via `from ..decode import
#   ...` -- a relative import that cannot resolve once this region is
#   extracted to a standalone file.
#
# Running the real decoder is out of scope for a region graded on its own
# three read assertions, not on the whole JSON->RDF pipeline -- same
# reasoning as the trav_existence sibling
# `test_cli_default_writes_no_metadata_or_sidecar` in this same
# repository/stratum (see its context_shim.py). The shim keeps the call
# shape identical to the real helpers -- `write_text_shape_project` still
# returns a Path, `decode_ontouml_json2graph` still returns a Graph -- but
# instead of running the package it copies a Turtle fixture into a fresh
# graph, chosen by a marker file (`_fixture_name`) the driver drops next to
# the JSON input beforehand. This lets the driver control what the
# region's own assertions see, which the single upstream test (always the
# empty-legacy-value / all-three-assertions-pass path) never varies.
#
# `UnsupportedTextValueWarning` is transcribed verbatim
# (json2graph/modules/text_values.py) -- the real `warnings.simplefilter
# ("error", ...)` in the region body then arms a genuine warning class,
# even though this stub never raises it (the scenario under test, an empty
# legacy value, is the one upstream case that never warns).
#
# `write_graph_file` is imported by the real file (context line, kept
# verbatim in original.py/translated.ldpy) but never called by THIS
# region's own body -- left as a placeholder that raises if ever invoked.
#
# Identical bindings for both representations.
from pathlib import Path

from rdflib import Graph


class UnsupportedTextValueWarning(UserWarning):
    """Warn that a Text shape contains content unsupported by the vocabulary."""


def write_text_shape_project(tmp_path: Path, width: int, height: int, value: str = "") -> Path:
    input_file = tmp_path / "text-shape.json"
    input_file.write_text("{}", encoding="utf-8")
    return input_file


def decode_ontouml_json2graph(json_file_path: str, base_uri: str | None = None, **kwargs) -> Graph:
    json_path = Path(json_file_path)
    marker = json_path.parent / "_fixture_name"
    fixture_name = marker.read_text(encoding="utf-8").strip() if marker.exists() else "fixture_clean.ttl"
    src = Path(__file__).resolve().parent / fixture_name
    return Graph().parse(source=str(src), format="turtle")


def write_graph_file(*args, **kwargs):
    raise NotImplementedError("not reached by this region")
