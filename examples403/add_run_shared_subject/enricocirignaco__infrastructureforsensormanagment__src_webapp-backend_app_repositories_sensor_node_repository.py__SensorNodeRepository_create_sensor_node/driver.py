"""Validation driver for enricocirignaco__infrastructureforsensormanagment__src_webapp-backend_app_repositories_sensor_node_repository.py__SensorNodeRepository_create_sensor_node.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='create_sensor_node',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)
