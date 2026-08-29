"""Validation driver for city-knowledge-graphs__python-2023__lab3_solution_Solution_Task3.4.py__Solution_Task3_4.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='Solution_Task3_4',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)
