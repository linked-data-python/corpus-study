# Context shim (see meta.json): minimal stand-in for lib.shacl.Shacl and
# lib.shacl.Validation from IndustryFusion/DigitalTwin@3b40088b88, so the
# region executes outside the package. The real Shacl class builds SHACL
# shapes into its data graph; setUp only needs a constructor that accepts
# and records (graph, namespace_prefix, basens, opcuans) the way the real
# one does. Identical bindings for both representations.
class Shacl:
    def __init__(self, data_graph, namespace_prefix, basens, opcuans):
        self.data_graph = data_graph
        self.namespace_prefix = namespace_prefix
        self.basens = basens
        self.opcuans = opcuans


class Validation:
    pass
