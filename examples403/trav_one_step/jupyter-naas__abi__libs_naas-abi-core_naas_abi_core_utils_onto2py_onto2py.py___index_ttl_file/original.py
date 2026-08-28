# Extracted from jupyter-naas/abi@3fb7f5304d : libs/naas-abi-core/naas_abi_core/utils/onto2py/onto2py.py
# region: _index_ttl_file (lines 724-741, stratum trav_one_step)
# licence of the source repository: see meta.json
from pathlib import Path
import rdflib
from rdflib import BNode

def _index_ttl_file(
    ttl_file: Path,
    index: dict[str, OntologyLocator],
    OWL: rdflib.Namespace,
    RDF: rdflib.Namespace,
) -> None:
    """Parse `ttl_file` and add its ontology IRIs (and version IRIs) to `index`."""
    graph = _parse_ttl_cached(ttl_file)
    if graph is None:
        return
    for ontology in graph.subjects(RDF.type, OWL.Ontology):
        if isinstance(ontology, BNode):
            continue
        locator = _locator_from_graph(graph, ontology, ttl_file)
        index.setdefault(str(ontology), locator)
        for version_iri in graph.objects(ontology, OWL.versionIRI):
            if isinstance(version_iri, rdflib.URIRef):
                index.setdefault(str(version_iri), locator)
