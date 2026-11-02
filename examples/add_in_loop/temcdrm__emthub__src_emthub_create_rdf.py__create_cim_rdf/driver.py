"""Validation driver for temcdrm__emthub__src_emthub_create_rdf.py__create_cim_rdf.

A statement-level region: both sides execute the module and the harness
compares every graph and value left in its globals (g, uuids, key, ID, mtyp,
desc, parms, ...).  context_shim.py binds the free names; dyn_models is the
real detailed_model_types.json of the pinned emthub clone, and
model_types_used selects four of its DYR models (GENCLS and WTARA1 have
exactly 5 parameter descriptors, EXST1 15, REGCA1 18).  The library's other
DYR models (GENROU, GENSAL, ...) are neighbours that must not be written;
the first three descriptors of every model are skipped by `range(3, ...)`,
and the typicalValue field mixes '' / str / float, which Literal(...,
datatype=CIM.String) must stringify the same way on both sides.
uuids, mutated by the loop, is compared as a module value.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry=None, calls=None)
