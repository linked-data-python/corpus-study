# Context shim (see meta.json): subset of rmlmapper.py from
# Mat-O-Lab/RDFConverter@0d81f4d1ba, so the region executes without the
# rest of that module (which imports `requests` and does live HTTP/RML
# processing unrelated to this region). Identical bindings for both
# representations.
#
# strip_namespace is copied verbatim: it is the only one of the four names
# the region imports that it actually calls. count_rules_str,
# replace_data_source and replace_all_data_sources are imported by the
# original code but never invoked in the extracted lines, so they are
# signature-only stubs here (never exercised by driver.py).
from re import split as re_split

from rdflib import Graph, Literal, Namespace, URIRef

RML = Namespace("http://semweb.mmlab.be/ns/rml#")


def strip_namespace(term) -> str:
    """Strip the namespace from full URI.

    Args:
        term (URIRef): A RDFlib Term

    Returns:
        str: short IRI
    """
    return re_split(r"/|#|:", term[::-1], maxsplit=1)[0][::-1]


def replace_data_source(rules: Graph, new_source: str):
    """Not called in this region; stub only to satisfy the import."""
    raise NotImplementedError("unused in this region")


def replace_all_data_sources(rules: Graph, url_mapping: dict) -> None:
    """Not called in this region; stub only to satisfy the import."""
    raise NotImplementedError("unused in this region")


def count_rules_str(graph_str: str):
    """Not called in this region; stub only to satisfy the import."""
    raise NotImplementedError("unused in this region")
