# Extracted from ScaDS/KGpipe@67ca171cfd : src/kgpipe_view/owl_to_mermaid.py
# region: get_available_layers (lines 26-33, stratum trav_navigation)
# licence of the source repository: see meta.json
from pathlib import Path
from rdflib.namespace import OWL, RDF, RDFS

def get_available_layers(ttl_path: Path) -> list[str]:
    graph = _load_graph(ttl_path)
    layer_names: set[str] = set()
    for class_node in graph.subjects(RDF.type, OWL.Class):
        for class_type in graph.objects(class_node, RDF.type):
            if class_type != OWL.Class:
                layer_names.add(_local_name(class_type))
    return sorted(layer_names)
