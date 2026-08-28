# Extracted from RDFLib/pyLODE@0d0471fb99 : pylode/profiles/supermodel/loader.py
# region: ProfilesDataset.load_owl_imports (lines 74-99, band medium)
# licence of the source repository: see meta.json
import logging

from rdflib import DCTERMS, OWL, PROF, RDF, Graph, URIRef

from loader_context import fetch

logger = logging.getLogger(__name__)

def load_owl_imports(self, graph: Graph):
    """Load all owl:imports values recursively."""
    import_values = [
        str(v)
        for v in graph.objects(None, OWL.imports)
        if str(v) not in self.external_resources
    ]
    if import_values:
        for remote_resource in import_values:
            if str(remote_resource) not in self.external_resources:
                logger.debug(
                    f"Fetching remote resource {remote_resource} from owl:imports."
                )
                _graph = Graph()
                try:
                    data, content_type = fetch(str(remote_resource), self.client)
                    _graph.parse(data=data, format=content_type)
                    # _graph.parse(str(remote_resource))
                    self.external_resources.add(str(remote_resource))
                    graph.__iadd__(self.load_owl_imports(_graph))
                except Exception as err:
                    raise RuntimeError(
                        f"Failed to parse data from {remote_resource}. {err}"
                    )

    return graph
