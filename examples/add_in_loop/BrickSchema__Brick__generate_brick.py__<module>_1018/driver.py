"""Validation driver for BrickSchema__Brick__generate_brick.py__<module>_1018.

The region is a piece of the generate_brick.py script: it reads the module
graph G (every `brick:Quantity` that has a `brick:hasQUDTReference`) and, for
each, adds a `qudt:applicableUnit` triple per unit found by `get_units` and by
`get_units_brick`.  context_shim.py gives G the slice of the Brick graph the
earlier passes of the script had built by then:

  * four quantities with a QUDT reference: two with units from both lookups
    (Temperature, Thickness), one from QUDT only (Length), one whose QUDT
    reference has no unit at all (Luminosity, the zero-unit case);
  * one quantity that already carries a unit (Power: the add is idempotent);
  * neighbours that must NOT be read: a quantity without a reference, a
    reference on a subject that is not typed `brick:Quantity`, and a
    `brick:Class` with a reference to a quantity kind that has units.

entry=None: both modules are executed and the graph G they leave behind is
compared by isomorphism (and the loop variables, as module values).
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
)
