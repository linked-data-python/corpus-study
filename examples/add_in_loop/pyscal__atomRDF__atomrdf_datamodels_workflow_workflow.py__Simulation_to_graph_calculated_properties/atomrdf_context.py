# Context shim (see meta.json): the part of pyscal/atomRDF@c9b070e15f that
# atomrdf/datamodels/workflow/workflow.py imports from atomrdf.namespace, so
# that Simulation.to_graph_calculated_properties executes outside the package
# (atomrdf is not installed here).  Plain Namespace(...) bindings with the
# IRIs of the package; `Literal` is the rdflib class atomrdf.namespace
# re-exports.  Identical bindings for both representations.
from rdflib import Literal, Namespace

CMSO = Namespace("http://purls.helmholtz-metadaten.de/cmso/")
LDO = Namespace("http://purls.helmholtz-metadaten.de/cdos/ldo/")
PLDO = Namespace("http://purls.helmholtz-metadaten.de/cdos/pldo/")
PODO = Namespace("http://purls.helmholtz-metadaten.de/cdos/podo/")
CDCO = Namespace("http://purls.helmholtz-metadaten.de/cdos/cdco/")
PROV = Namespace("http://www.w3.org/ns/prov#")
ASMO = Namespace("http://purls.helmholtz-metadaten.de/asmo/")
MDO = Namespace("https://w3id.org/mdo/calculation/")
