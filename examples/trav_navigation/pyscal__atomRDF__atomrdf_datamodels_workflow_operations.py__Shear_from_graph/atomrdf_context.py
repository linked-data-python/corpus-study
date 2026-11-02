# Context shim (see meta.json): subset of pyscal/atomRDF, so the region
# executes outside the package (atomrdf is not installed in the study venv).
# Identical bindings/behaviour for both representations.
#
# atomrdf/namespace.py: plain Namespace(...) bindings, real IRIs (checked
# against atomrdf 0.12.3's atomrdf/namespace.py).  `Literal` there is a
# wrapper function around rdflib's Literal; the region never calls it.
# atomrdf/utils.py: get_sample_object verbatim.
# atomrdf/datamodels/workflow/operations.py: `Shear` reduced to the keyword
# fields the region passes to `cls(...)` (atomrdf's is a pydantic model).
# `classmethod`: the region was extracted from a class body, where
# `@classmethod def from_graph(cls, ...)` is bound to Shear; at module level
# a bare classmethod object is not callable.  Shadowing the builtin by the
# identity makes the extracted function an ordinary function whose first
# argument, `cls`, the driver supplies (Shear).
from rdflib import Namespace, URIRef
from rdflib import Literal

CMSO = Namespace("http://purls.helmholtz-metadaten.de/cmso/")
ASMO = Namespace("http://purls.helmholtz-metadaten.de/asmo/")
LDO = Namespace("http://purls.helmholtz-metadaten.de/cdos/ldo/")
PLDO = Namespace("http://purls.helmholtz-metadaten.de/cdos/pldo/")
PODO = Namespace("http://purls.helmholtz-metadaten.de/cdos/podo/")
CDCO = Namespace("http://purls.helmholtz-metadaten.de/cdos/cdco/")
PROV = Namespace("http://www.w3.org/ns/prov#")


def get_sample_object(sample_id):
    if isinstance(sample_id, str):
        sample_id = URIRef(sample_id)
    return sample_id


def classmethod(func):
    return func


class Shear:
    def __init__(self, id=None, input_sample=None, output_sample=None,
                 shear_vector=None, normal_vector=None, distance=None):
        self.id = id
        self.input_sample = input_sample
        self.output_sample = output_sample
        self.shear_vector = shear_vector
        self.normal_vector = normal_vector
        self.distance = distance
