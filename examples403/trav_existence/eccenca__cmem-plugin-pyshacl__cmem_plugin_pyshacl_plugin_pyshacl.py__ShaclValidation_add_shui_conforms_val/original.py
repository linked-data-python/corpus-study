# Extracted from eccenca/cmem-plugin-pyshacl@faf59e81de : cmem_plugin_pyshacl/plugin_pyshacl.py
# region: ShaclValidation.add_shui_conforms_val (lines 429-444, stratum trav_existence)
# licence of the source repository: see meta.json
from rdflib import (
    PROV,
    RDF,
    RDFS,
    SH,
    SKOS,
    XSD,
    BNode,
    Graph,
    Literal,
    Namespace,
    URIRef,
)

def add_shui_conforms_val(
    self, validation_graph: Graph, validation_result_uris: list, focus_nodes: list
) -> Graph:
    """Add shui conforms flag"""
    self.log.info("Adding shui:conforms flags to validation graph")
    itr = focus_nodes or validation_result_uris
    for i in itr:
        subj = i if focus_nodes else validation_graph.value(subject=i, predicate=SH.focusNode)
        validation_graph.add(
            (
                subj,
                URIRef("https://vocab.eccenca.com/shui/conforms"),
                Literal(False, datatype=XSD.boolean),
            )
        )
    return validation_graph
