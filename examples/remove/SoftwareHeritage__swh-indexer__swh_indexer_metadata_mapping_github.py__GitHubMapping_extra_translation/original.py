# Extracted from SoftwareHeritage/swh-indexer@95f3e65462 : swh/indexer/metadata_mapping/github.py
# region: GitHubMapping.extra_translation (lines 45-55, stratum remove)
# licence of the source repository: see meta.json
from rdflib import RDF, BNode, Graph, Literal, URIRef
from swh.indexer.namespaces import ACTIVITYSTREAMS, CODEMETA, FORGEFED, SCHEMA, XSD
from .utils import add_url_if_valid, prettyprint_graph  # noqa

def extra_translation(self, graph, root, content_dict):
    graph.remove((root, RDF.type, SCHEMA.SoftwareSourceCode))
    graph.add((root, RDF.type, FORGEFED.Repository))

    if content_dict.get("has_issues"):
        add_url_if_valid(
            graph,
            root,
            CODEMETA.issueTracker,
            URIRef(content_dict["html_url"] + "/issues"),
        )
