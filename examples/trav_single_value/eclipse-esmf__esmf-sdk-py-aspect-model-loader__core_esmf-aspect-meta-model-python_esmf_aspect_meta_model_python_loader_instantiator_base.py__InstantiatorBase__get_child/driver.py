"""Validation driver for eclipse-esmf__esmf-sdk-py-aspect-model-loader__core_esmf-aspect-meta-model-python_esmf_aspect_meta_model_python_loader_instantiator_base.py__InstantiatorBase__get_child.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='_get_child',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)
