# Context shim (see meta.json): from IndustryFusion/DigitalTwin@
# 3b40088b880811f61df63ba926f78256098ce695:
#
# - `Bindings.__init__` from semantic-model/opcua/lib/bindings.py, copied
#   verbatim -- it is the class whose method the region extracts
#   (`Bindings.create_attribute_binding` is extracted as a bare function
#   taking `self`), just outside the region's own line range (48-75). Only
#   `__init__` is reproduced: no other method of `Bindings` is reachable
#   from `create_attribute_binding`.
# - lib/utils.py's module-level `NGSILD` constant, which
#   `create_attribute_binding` reads via `utils.NGSILD['Property']`
#   (`import lib.utils as utils` becomes `import context_shim as utils` in
#   original.py/translated.ldpy, so the module-attribute-access idiom --
#   not a name import -- still resolves the same way). Value verified
#   against examples403/trav_one_step/IndustryFusion__DigitalTwin__
#   semantic-model_opcua_tests_test_libshacl.py__TestShaclAdditional_
#   test_ngsild_property_constraints_scalar_and_list/context_shim.py, a
#   sibling region's shim for the same repository at the same commit,
#   itself sourced from lib/utils.py.
#
# Identical bindings for both representations.
from rdflib import Graph, Namespace

NGSILD = Namespace('https://uri.etsi.org/ngsi-ld/')


class Bindings:
    def __init__(self, namespace_prefix, basens):
        self.bindingsg = Graph()
        self.basens = basens
        self.binding_namespace = Namespace(f'{namespace_prefix}bindings/')
        self.bindingsg.bind('binding', self.binding_namespace)
