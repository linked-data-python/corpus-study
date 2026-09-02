# Context shim (see meta.json): minimal stand-ins for the OntoUML/ontouml-json2graph
# modules imported by decode_dictionary (json2graph/modules/arguments.py,
# json2graph/modules/utils_graph.py, json2graph/modules/text_values.py, and the
# module-level LOGGER built by json2graph/modules/logger.py), so the region
# executes outside the package. Reproduces only the bindings decode_dictionary
# touches -- base URI lookup, OntoUML term resolution, the Text.value warning
# hook, and a logger with .error() -- not the projects' internal logic.
# Identical bindings for both representations.
import logging

from rdflib import URIRef

ONTOUML_NS = "https://w3id.org/ontouml#"


class _Args:
    ARGUMENTS = {"base_uri": "https://example.org/ontouml/"}


args = _Args()


def ontouml_ref(name):
    """Resolve a JSON field/type name to its OntoUML-Vocabulary IRI."""
    return URIRef(ONTOUML_NS + name)


def warn_if_text_value_is_unsupported(dictionary_data):
    pass


def initialize_logger():
    return logging.getLogger("ontouml_json2graph_shim")
