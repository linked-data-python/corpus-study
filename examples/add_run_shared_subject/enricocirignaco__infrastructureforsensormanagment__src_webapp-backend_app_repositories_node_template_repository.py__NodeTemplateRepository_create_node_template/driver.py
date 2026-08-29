"""Validation driver for enricocirignaco__infrastructureforsensormanagment__src_webapp-backend_app_repositories_node_template_repository.py__NodeTemplateRepository_create_node_template.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='create_node_template',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)
