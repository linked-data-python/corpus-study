"""Validation driver for IndustryFusion__DigitalTwin__semantic-model_opcua_owl2instances.py__<module>_855.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.

Module-state oracle: the graphs `g` and `e_graph` (what the CONSTRUCT and
add_subclasses_recursive put into the Entity), compared by isomorphism.
Audit of 2026-10-31: fixture.ttl gives the root opcua:BaseObjectType a
superclass (owl:Thing), reached only through the zero-length step of
`rdfs:subClassOf*`; before it, a query whose `*` became `+` stayed green.

Not exercised here: the repository's store.  owl2instances.py:732 opens
`Graph(store='Oxigraph')`; there the original's text query runs on
Oxigraph, while the prepared query of `s{ }(g)` is refused by oxrdflib
(NotImplementedError: "already parsed Queries are not supported") and rdflib
falls back to its own engine.  Checked once on a copy (meta.json "repair"):
same CONSTRUCT result on both sides.

The file the region writes (`e.serialize(destination=entitiesname)`): both
sides write the same path, one after the other, so the file left on disk
proves nothing.  `_recording_serialize` wraps the shim's `Entity.serialize`
(same wrapper for both sides: one shim module) and, after the real write,
stores the destination and the text written in the running module's
globals as `serialized_entities`, a value the module-state comparison then
diffs (the harness skips names that start with an underscore).  The
wrapped `Entity.__init__` first sets it to None in the module that builds
the Entity, so a side that never writes still has the name, and differs
(module-state only compares the names both sides define).
"""
import sys
from pathlib import Path

import entity_shim
from rdfeval.harness import run_pair

_real_init = entity_shim.Entity.__init__
_real_serialize = entity_shim.Entity.serialize


def _seeding_init(self, *args, **kwargs):
    _real_init(self, *args, **kwargs)
    sys._getframe(1).f_globals["serialized_entities"] = None


def _recording_serialize(self, destination):
    _real_serialize(self, destination)
    sys._getframe(1).f_globals["serialized_entities"] = (
        str(destination), Path(destination).read_text())


entity_shim.Entity.__init__ = _seeding_init
entity_shim.Entity.serialize = _recording_serialize

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
)
