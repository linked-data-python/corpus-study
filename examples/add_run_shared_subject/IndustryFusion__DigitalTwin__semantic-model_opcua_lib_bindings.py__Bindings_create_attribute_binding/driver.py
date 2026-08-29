"""Validation driver for IndustryFusion__DigitalTwin__semantic-model_opcua_lib_bindings.py__Bindings_create_attribute_binding.

Establishes semantic equivalence of original.py and translated.ldpy.

create_attribute_binding calls `random.choices(...)` once, unseeded, to
mint bindingiri's local name. run_pair calls demo() once per side, in the
same process (original.py's demo() first, then translated.ldpy's). Seeding
`random` from inside a `calls=` callable does not make the two draws match:
run_pair evaluates the callable TWICE -- once to build args_o, once to
build args_t -- and only THEN calls fo(*args_o) followed by ft(*args_t). So
a seed set while building args_o is consumed by fo() before ft() ever
runs, and ft() draws from whatever state fo() left behind, not from a
matching fresh seed (verified: re-seeding inside the callable still
produces two different bindingiri values). Patching `random.choices`
itself to a deterministic, state-free stand-in sidesteps the ordering
problem entirely: both calls mint the identical bindingiri regardless of
when they run, and every other choice inside create_attribute_binding
(which one) is untouched.
"""
import random as _random

from rdflib import URIRef

from rdfeval.harness import run_pair


def _deterministic_choices(population, k=1, **kwargs):
    pop = list(population)
    return [pop[i % len(pop)] for i in range(k)]


_random.choices = _deterministic_choices

VERDICT = run_pair(
    __file__,
    entry='demo',
    calls=[
        # no logic_transform: exercises the five-triple unconditional run
        # only (a, bindsEntity, bindingVersion, bindsFirmware,
        # bindsAttributeType) plus the trailing boundBy triple on the
        # DIFFERENT subject attribute_iri -- bindsLogic must NOT appear.
        (
            (URIRef("http://example.org/parent1"), URIRef("http://example.org/attr1")),
            {},
        ),
        # logic_transform set: exercises the conditional sixth triple
        # (bindsLogic) too, still on bindingiri, plus non-default
        # version/firmware.
        (
            (URIRef("http://example.org/parent2"), URIRef("http://example.org/attr2")),
            {"logic_transform": "scale(2.0)", "version": "0.2", "firmware": "fw-x"},
        ),
    ],
)
