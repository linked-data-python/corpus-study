# Context shim (see meta.json): the names that surround the loop of
# create_cim_rdf in temcdrm/emthub@c9834a2c67 : src/emthub/create_rdf.py, so
# the statement executes outside the package (emthub imports networkx,
# otsrdflib, ... at import time).  Identical bindings for both
# representations.
#
# - dyn_models: what emthub.cim_support.load_detailed_model_types() returns,
#   i.e. json.loads of src/emthub/queries/detailed_model_types.json, read here
#   from the pinned clone made by `rdfeval acquire`
#   (corpus/repos/temcdrm__emthub) - the REAL data, not a transcription.
# - CIM = rdflib.Namespace (CIM_NS), CIM_NS = 'http://www.ucaiug.org/grid18v15#'
#   (create_rdf.py lines 34 and 247).
# - g (an empty graph), uuids ({}, create_rdf.py line 275) and
#   model_types_used (a set of DYR model names, filled by the code above the
#   loop in the original: `model_types_used.add (mdl)`).  Four models are
#   used here; the other DYR models of the library are neighbours that must
#   not appear in the output.
import json
from pathlib import Path

import rdflib

_CLONE = Path(__file__).resolve().parents[3] / "corpus" / "repos" / "temcdrm__emthub"

CIM_NS = 'http://www.ucaiug.org/grid18v15#'
CIM = rdflib.Namespace(CIM_NS)

dyn_models = json.loads(
    (_CLONE / "src" / "emthub" / "queries" / "detailed_model_types.json").read_text())

g = rdflib.Graph()
uuids = {}
# Filled by .add() calls, as in the original, and NOT written as a set literal:
# a literal of constants is compiled to a frozenset constant whose element
# order is frozen into the .pyc under the hash seed of the compiling process,
# so the iteration order of the resulting set depended on whether the first
# side to import this shim compiled it or loaded a cached .pyc -- the two
# sides could then end the loop on different models.
model_types_used = set()
for _mdl in ('GENCLS', 'EXST1', 'REGCA1', 'WTARA1'):
    model_types_used.add(_mdl)
