# Extracted from blue-core-lod/bluecore_api@f07d76c83a : tests/api/test_cbd.py
# region: _resources (lines 244-248, stratum trav_one_step)
# licence of the source repository: see meta.json
from bluecore_models.namespaces import BF
from rdflib import RDF, Graph, URIRef

def _resources(graph: Graph) -> set[str]:
    """The Work and Instance uris the CBD graph describes."""
    return {str(s) for s in graph.subjects(RDF.type, BF.Work)} | {
        str(s) for s in graph.subjects(RDF.type, BF.Instance)
    }
