# Context shim (see meta.json): subset of lib/shacl.py's Shacl class from
# IndustryFusion/DigitalTwin@3b40088b880811f, so the region executes outside
# the semantic-model/opcua package. Only the constructor and the three
# methods the test under study calls (create_datatype_shapes,
# create_iri_shape, shacl_or) are reproduced, verbatim from the source.
# Identical bindings for both representations.
from rdflib import Graph, Namespace, BNode
from rdflib.namespace import SH
from rdflib.collection import Collection


class Shacl:
    def __init__(self, data_graph, namespace_prefix, basens, opcuans,
                 value_rank_subshapes_enabled=False):
        self.shaclg = Graph()
        self.shacl_namespace = Namespace(f'{namespace_prefix}shacl/')
        self.shaclg.bind('shacl', self.shacl_namespace)
        self.shaclg.bind('sh', SH)
        self.basens = basens
        self.opcuans = opcuans
        self.data_graph = data_graph
        self.value_rank_subshapes_enabled = value_rank_subshapes_enabled

    def create_datatype_shapes(self, datatypes):
        if datatypes is None or len(datatypes) == 0:
            return []
        else:
            dt_items = []
            for dt in datatypes:
                dt_node = BNode()
                self.shaclg.add((dt_node, SH.datatype, dt))
                dt_items.append(dt_node)
            return dt_items

    def create_iri_shape(self):
        dt_items = []
        dt_node = BNode()
        self.shaclg.add((dt_node, SH.nodeKind, SH.IRI))
        dt_items.append(dt_node)
        return dt_items

    def shacl_or(self, shapes):
        if len(shapes) == 1:
            result = []
            for s, p, o in self.shaclg.triples((shapes[0], None, None)):
                result.append((p, o))
                self.shaclg.remove((s, p, o))
            return result
        or_node = BNode()
        Collection(self.shaclg, or_node, shapes)
        return [(SH['or'], or_node)]
