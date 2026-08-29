# Context shim (see meta.json): ontouml_ref, copied verbatim from
# OntoUML/ontouml-json2graph@982f12b9c4 json2graph/modules/utils_graph.py,
# plus the METADATA["conformsTo"] value it reads
# (json2graph/modules/metadata.py: METADATA["conformsTo"] =
# "https://w3id.org/ontouml"). load_ontouml_vocabulary is imported by the
# region but never called from set_cardinality_relations; kept as a
# name-only stub so the import line is unchanged. Identical for both
# representations.
from rdflib import Graph, URIRef

METADATA = {"conformsTo": "https://w3id.org/ontouml"}


def ontouml_ref(entity: str) -> URIRef:
    """Receive the name of the OntoUML Vocabulary's entity as a string and returns the corresponding URIRef."""
    entity_uri = METADATA["conformsTo"] + "#" + entity
    return URIRef(entity_uri)


def load_ontouml_vocabulary(enable_remote: bool = False) -> Graph:
    raise NotImplementedError("not exercised by this region")
