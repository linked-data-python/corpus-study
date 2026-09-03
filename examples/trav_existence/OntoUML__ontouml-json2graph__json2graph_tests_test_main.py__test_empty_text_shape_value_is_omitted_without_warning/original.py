# Extracted from OntoUML/ontouml-json2graph@982f12b9c4 : json2graph/tests/test_main.py
# region: test_empty_text_shape_value_is_omitted_without_warning (lines 860-871, stratum trav_existence)
# licence of the source repository: see meta.json
import warnings
from pathlib import Path
from rdflib import RDF, RDFS, XSD, Graph, Literal, Namespace, URIRef
from context_shim import decode_ontouml_json2graph, write_graph_file  # context shim -- see meta.json
from context_shim import UnsupportedTextValueWarning  # context shim -- see meta.json
from context_shim import write_text_shape_project  # context shim -- see meta.json
BASE_URI = "https://example.org#"
ONTOUML = Namespace("https://w3id.org/ontouml#")

def test_empty_text_shape_value_is_omitted_without_warning(tmp_path: Path) -> None:
    """Verify that an empty legacy Text.value is omitted without misusing ontouml:text."""
    input_file = write_text_shape_project(tmp_path, width=80, height=42)

    with warnings.catch_warnings():
        warnings.simplefilter("error", UnsupportedTextValueWarning)
        ontouml_graph = decode_ontouml_json2graph(json_file_path=str(input_file), base_uri=BASE_URI)

    text_shape_uri = URIRef(BASE_URI + "view-1_shape")
    assert (text_shape_uri, RDF.type, ONTOUML.Text) in ontouml_graph
    assert not any(ontouml_graph.triples((text_shape_uri, ONTOUML.text, None)))
    assert not any(ontouml_graph.triples((text_shape_uri, ONTOUML.value, None)))


# Demo harness (identical on both sides, see meta.json): the region is a
# pytest test that only ever asserts. The upstream test only ever exercises
# the scenario where all three assertions pass (an empty legacy value); to
# also exercise their FALSE side -- so a broken translation has something
# to be caught by (see corpus/405, the anti-hollow-green discipline) --
# `demo` calls the region and turns a failed assertion into a comparable
# value instead of letting it propagate and abort the driver.
def demo(tmp_path: Path) -> object:
    try:
        test_empty_text_shape_value_is_omitted_without_warning(tmp_path)
        return "ok"
    except AssertionError as e:
        return ("assertion-failed", str(e))
