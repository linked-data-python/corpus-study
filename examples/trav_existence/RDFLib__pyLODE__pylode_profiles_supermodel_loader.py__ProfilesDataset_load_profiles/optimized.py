# Extracted from RDFLib/pyLODE@0d0471fb99 : pylode/profiles/supermodel/loader.py
# region: ProfilesDataset.load_profiles (lines 101-146, stratum trav_existence)
# licence of the source repository: see meta.json
import logging
from rdflib import DCTERMS, OWL, PROF, RDF, Graph, URIRef
from context_shim import LODE, Loader, fetch
logger = logging.getLogger(__name__)
PYLODE_CONFIG_GRAPH = "urn:graph:pylode-config"
MEDIA_TYPES = {
    "text/turtle": "text/turtle",
    "application/n-triples": "application/n-triples",
    "application/n-quads": "application/n-quads",
}

def load_profiles(self, graph: Graph, prev_graph: Graph):
    for profile in graph.subjects(RDF.type, PROF.Profile):
        profile_graph = Graph(identifier=str(profile))
        profile_graph += graph.cbd(profile)

        for prof_resource_descriptor in profile_graph.objects(None, PROF.hasResource):
            mediatype = profile_graph.value(prof_resource_descriptor, DCTERMS.format)
            role = profile_graph.value(prof_resource_descriptor, PROF.hasRole)
            remote_resource = profile_graph.value(prof_resource_descriptor, PROF.hasArtifact)

            if role == LODE.config:
                logger.debug(
                    f"Fetching remote resource {remote_resource} from PROF resource descriptor. A pylode config."
                )
                data, content_type = fetch(str(remote_resource), self.client, str(mediatype))
                self.get_graph(URIRef(PYLODE_CONFIG_GRAPH)).parse(data=data, format=content_type)

                _config_graph = self.load_owl_imports(Graph().parse(data=data, format=content_type))
                self.load_profiles(_config_graph, graph)
            elif str(mediatype) in MEDIA_TYPES:
                logger.debug(
                    f"Fetching remote resource {remote_resource} from PROF resource descriptor."
                )
                data, content_type = fetch(str(remote_resource), self.client, str(mediatype))
                new_graph = self.load_owl_imports(Graph().parse(data=data, format=content_type))

                if (None, RDF.type, PROF.Profile) in new_graph:
                    self.load_profiles(new_graph, profile_graph)
                else:
                    profile_graph += new_graph
        self.add_graph(profile_graph)


# Demo harness (identical on both sides, see meta.json): the region is a
# method (`self`) that returns nothing -- its only observable effect is the
# set of graphs it hands to `self.add_graph`. `demo` runs it against a fresh
# Loader (the context shim's ProfilesDataset stand-in) and returns the
# graphs collected, sorted by identifier so the oracle sees a fixed order.
def demo(graph, prev_graph):
    self = Loader()
    load_profiles(self, graph, prev_graph)
    return sorted(
        ((str(g.identifier), g) for g in self.added), key=lambda pair: pair[0]
    )
