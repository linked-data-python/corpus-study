# Context shim (see meta.json): the one name original.py takes from
# nidm.core (PyNIDM, https://github.com/incf-nidash/PyNIDM, nidm/core/Constants.py
# line 60): `Constants.SIO`, the SIO namespace. The package itself is not in the
# study venv. Identical bindings for both representations.
from types import SimpleNamespace
from rdflib import Namespace

Constants = SimpleNamespace(
    SIO=Namespace("http://semanticscience.org/ontology/sio.owl#"),
)
