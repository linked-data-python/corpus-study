# Extracted from IndustryFusion/DigitalTwin@3b40088b88 : semantic-model/opcua/lib/entity.py
# region: Entity.__init__ (lines 72-80, stratum ns_import_project)
# licence of the source repository: see meta.json
#
# Executability restoration (AGENT_BATCH "163 regions" case, see meta.json):
# `lib.utils` rewritten to `lib_utils_context`, the shim module next to
# this file (the real dotted project path does not resolve for a single
# extracted file).
from rdflib import Graph, Namespace, Literal, URIRef, BNode
from lib_utils_context import NGSILD, collection_to_list, calculate_array_dimensions

def __init__(self, namespace_prefix, basens, opcuans):
    self.e = Graph()
    self.basens = basens
    self.opcuans = opcuans
    self.entity_namespace = Namespace(f'{namespace_prefix}entity/')
    self.e.bind('uaentity', self.entity_namespace)
    self.ngsildns = NGSILD
    self.e.bind('ngsi-ld', self.ngsildns)
    self.types = []


# Demo harness (identical on both sides, see meta.json): __init__ is a
# method body lifted out of Entity, so this appends the minimal `self`
# (a plain object, since __init__ only WRITES attributes and reads none)
# and returns the comparable results of what it sets -- not `self` itself,
# which has no __eq__ and would always compare unequal by identity across
# the two separately-constructed instances (see meta.json for why: same
# failure mode as the acdh-oeaw/vocabseditor and DataDrivenCPS/acquirium
# siblings of this stratum).
class _Blank:
    pass


def demo(namespace_prefix, basens, opcuans):
    self = _Blank()
    __init__(self, namespace_prefix, basens, opcuans)
    return (
        list(self.e),
        sorted((p, str(n)) for p, n in self.e.namespaces()),
        str(self.entity_namespace),
        str(self.ngsildns),
        self.basens,
        self.opcuans,
        self.types,
    )
