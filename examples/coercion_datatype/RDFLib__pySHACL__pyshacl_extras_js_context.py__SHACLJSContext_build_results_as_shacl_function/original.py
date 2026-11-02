# Extracted from RDFLib/pySHACL@469cca7a22 : pyshacl/extras/js/context.py
# region: SHACLJSContext.build_results_as_shacl_function (lines 555-573, stratum coercion_datatype)
# licence of the source repository: see meta.json
from decimal import Decimal
from context_shim import JSProxy  # context shim, see meta.json
from rdflib import BNode, Literal, URIRef
from rdflib.namespace import XSD

@classmethod
def build_results_as_shacl_function(cls, res, return_type=None):
    if isinstance(res, JSProxy):
        try:
            return res.toPython()
        except AttributeError:
            return None
    elif isinstance(res, (Literal, URIRef, BNode)):
        pass
    elif return_type is not None and isinstance(res, (int, float)):
        lex = str(res)
        res = Literal(lex, datatype=return_type, normalize=False)
    elif isinstance(res, (float, Decimal)):
        res = Literal(str(res), datatype=XSD['decimal'])
    elif isinstance(res, bool):
        res = Literal(res, datatype=XSD['boolean'])
    elif isinstance(res, (int, float, str, bytes, bool)):
        res = Literal(res, datatype=return_type, normalize=False)
    return res


# Binding restoration (identical on both sides, see meta.json): the region is
# a classmethod extracted without its enclosing class, and a classmethod
# object is not callable by itself; this alias makes it reachable as the
# plain callable `build` for the driver.
class SHACLJSContext:
    build_results_as_shacl_function = build_results_as_shacl_function


build = SHACLJSContext.build_results_as_shacl_function
