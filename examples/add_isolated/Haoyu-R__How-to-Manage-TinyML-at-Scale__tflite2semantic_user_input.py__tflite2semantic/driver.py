"""Validation driver for Haoyu-R__How-to-Manage-TinyML-at-Scale__tflite2semantic_user_input.py__tflite2semantic.

The region (lines 373-386) is a nested function DEFINITION,
`addCommonInfo`, that closes over a per-model `g` from its enclosing scope
rather than taking it as a parameter. Defining it does nothing observable
by itself, and the harness's entry=/calls= mode only compares a call's
return value and its own args/kwargs -- never a module global a function
merely closes over -- so it cannot see this region's effect either. The
oracle is therefore module-state RDF isomorphism (meta.oracle ==
"isomorphism", entry=None): original.py/translated.ldpy define
addCommonInfo AND call it three times, exactly as the real code does at its
own lines 391/397/404 (input layer, output layer, and a middle layer with
neither flag -- the neighbourhood that must not add shapeIn/shapeOut), so
the module-level `g` ends up holding the traces of the region's own
+{ }/.add() calls plus (identically on both sides) the sibling helpers'.

Context shim tflite_context.py restores addLayer/addQuantization/
addTrainable/addActivation (real sibling closures addCommonInfo calls,
reproduced verbatim) and stand-ins for the TFLite/TensorFlow objects
(model, op, opt, interpreter) and booleans (quantized, hasActivation) the
real code only has after parsing an actual .tflite file -- not needed here
since this region just writes RDF from values already computed. See the
shim's own header for why the helpers are built by a factory bound to each
side's own `g` instead of importing one shared Graph.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry=None, calls=None)
