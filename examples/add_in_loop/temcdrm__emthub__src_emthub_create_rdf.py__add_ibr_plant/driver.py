"""Validation driver for temcdrm__emthub__src_emthub_create_rdf.py__add_ibr_plant.

A statement-level region: both sides execute the module and the harness
compares every graph and value left in its globals (g, seq, kind, val, pt,
inf, bFixed, ...).  context_shim.py binds the free names (`g` with one
triple already in it, `dll`, `dllID`, `seq = 0`, `d['ParametersInfo']`) and
carries get_dll_cim_parameter_kind verbatim.

The five parameters exercise what the island has to get right: every
datatype/kind branch used (Real64, Int32, Char_Ptr, Real32, Int8), values
that are float, int, str, bool (str(True), Literal(True, datatype=...)),
an empty string, a non-ASCII string, quotes and a newline in a description,
and FixedValue 0 / 0.0 (False) against 1 / 2 / -1 (True).  The loop leaves
seq == 5.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry=None, calls=None)
