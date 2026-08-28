"""Validation driver: Value._to_rdflib is a pure term constructor.

One fixture per branch of the isinstance dispatch (Entity, IRI, Quantity,
Time, Text, String), built from the local kif_shim stand-ins.
"""
import datetime
import decimal

from kif_shim import Entity, IRI, Quantity, String, Text, Time
from rdfeval.harness import run_pair


def call(value):
    return lambda: ((value,), {})


VERDICT = run_pair(
    __file__,
    entry='_to_rdflib',
    calls=[
        call(Entity(IRI('http://www.wikidata.org/entity/Q42'))),
        call(IRI('http://www.wikidata.org/entity/P31')),
        call(Quantity(decimal.Decimal('1.5'))),
        call(Quantity(decimal.Decimal('123'))),
        call(Quantity(decimal.Decimal('1E+2'))),
        call(Time(datetime.datetime(2024, 5, 17, 12, 30, 0,
                                    tzinfo=datetime.timezone.utc))),
        call(Text('hello', 'en')),
        call(String('hello')),
    ],
)
