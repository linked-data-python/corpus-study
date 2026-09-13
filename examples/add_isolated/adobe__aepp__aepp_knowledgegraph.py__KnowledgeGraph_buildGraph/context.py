# Context shim (see meta.json): a minimal reconstruction of the pieces of
# adobe/aepp@05c73dfc6d that KnowledgeGraph.buildGraph closes over, so the
# extracted region can run outside the full aepp package (which needs a live
# AEP sandbox: config, auth, network). Namespace bindings are copied from
# KnowledgeGraph.__init__ (aepp/knowledgegraph.py lines 96-104): each is a
# real f-string pattern of the source, instantiated here for a fixed sandbox
# name instead of a live `self.sandbox`. FakeFlowManager mirrors the public
# attributes documented on flowservice.FlowManager (id, name, datasetId,
# frequency, attributes, audiences) without its network-backed constructor.
# extractPaths is mocked outright (not reimplemented): the real method walks
# a PQL/JSON AST via self.segmentationAPI.__extract_pql_paths__, which is
# itself an algorithm the region under test never calls -- only its RESULT
# (a list of dotted schema paths) is consumed here, so a fixture list stands
# in for it exactly as fixture.ttl stands in for a graph.
# Identical bindings for both representations.
from rdflib import Namespace


SANDBOX_NAME = "prod"


class FakeSegmentationAPI:
    """Returns a fixed path list per audience id instead of parsing PQL."""

    def __init__(self, paths_by_audience_id):
        self._paths_by_audience_id = paths_by_audience_id

    def extractPaths(self, audience, recursive=False):
        return list(self._paths_by_audience_id.get(audience["id"], []))


class FakeKnowledgeGraph:
    """Stand-in for aepp.knowledgegraph.KnowledgeGraph's `self`.

    Only the attributes buildGraph's add_isolated region reads: the five
    per-domain Namespace objects it builds in __init__, plus a
    segmentationAPI that answers extractPaths without a live sandbox.
    """

    def __init__(self, sandbox=SANDBOX_NAME, paths_by_audience_id=None):
        self.sandbox = sandbox
        self.SANDBOX = Namespace(f"https://sandbox/{sandbox}")
        self.SCHEMA = Namespace(f"https://sandbox/{sandbox}/xdm/")
        self.CATALOG = Namespace(f"https://sandbox/{sandbox}/catalog/")
        self.IDENTITY = Namespace(f"https://sandbox/{sandbox}/identity/")
        self.PROFILE = Namespace(f"https://sandbox/{sandbox}/profile/")
        self.FLOWS = Namespace(f"https://sandbox/{sandbox}/flows/")
        self.AUDIENCES = Namespace(f"https://sandbox/{sandbox}/audiences/")
        self.segmentationAPI = FakeSegmentationAPI(paths_by_audience_id or {})
        self.global_graph = None
        self.__dataset_preview__ = []


class FakeFlowManager:
    """Stand-in for aepp.flowservice.FlowManager's public attributes."""

    def __init__(self, id, name, datasetId=None, frequency=None,
                 attributes=None, audiences=None):
        self.id = id
        self.name = name
        self.datasetId = datasetId
        self.frequency = frequency
        self.attributes = attributes or {}
        self.audiences = audiences or []
