"""Validation driver for BD2KOnFHIR__fhirtordf__fhirtordf_rdfsupport_fhirgraphutils.py__extension.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

The fixture is part of the translation: it must hold several solutions of the
pattern the region reads, the zero-solution case, and neighbouring triples
that must NOT match.

Three calls: the target node whose matching extension carries an
Extension.value* predicate (the single expected solution of the fused join),
the second patient whose only extension never carries Extension.value*
(zero-solution case), and a node with no fhir:Element.extension triples at
all (also zero-solution, from a different angle: no ext candidate exists).

Repair of 2026-10-31 (mutation audit), five more calls:

  * the shape the repository really reads (its own test,
    tests/rdfsupport_tests/test_fhirgraphutils.py:34-45, on
    tests/data/patient-example.ttl:83-94): the node is the BLANK node object
    of fhir:Patient.birthDate -- computed from each side's own fresh graph --
    and url and value are blank nodes carrying fhir:value; called with
    asLiteral False and True, as that test does, and with the url of the
    neighbouring extension.  Without these, dropping `asLiteral` from the
    returned `value(...)` call, or returning `o` when asLiteral is set,
    stayed green.
  * two Extension.url values on one extension: `value` raises
    UniquenessError; the harness compares the raise (type and message).
  * zero Extension.url on an extension that has an Extension.value*.

Mutants killed: island emptied, node widened to `[]`, subject of the second
pattern widened, first predicate wrong, url check removed or forced True,
the 'Extension.value' filter forced True, `return o` (before the repair);
`asLiteral` dropped, `return o if asLiteral else ...` (by the new calls).
"""
from pathlib import Path

from rdflib import URIRef

from rdfeval.harness import run_pair, fixture_graph

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"
EX = "http://example.org/"
FHIR = "http://hl7.org/fhir/"
BIRTH_TIME = "http://hl7.org/fhir/StructureDefinition/patient-birthTime"


def _case(node, pred):
    return lambda: ((fixture_graph(FIXTURE), URIRef(node), pred), {})


def _birthdate_case(pred, *rest):
    """The node is the blank node object of ex:patient3 fhir:Patient.birthDate,
    as the repository's test computes it (g.value(s, Patient.birthDate))."""
    def case():
        g = fixture_graph(FIXTURE)
        node = g.value(URIRef(EX + "patient3"), URIRef(FHIR + "Patient.birthDate"))
        return (g, node, URIRef(pred)) + rest, {}
    return case


VERDICT = run_pair(
    __file__,
    entry="extension",
    fixture="fixture.ttl",
    calls=[
        _case(EX + "patient1", EX + "ext/target"),
        _case(EX + "patient2", EX + "ext/target"),
        _case(EX + "no-such-node", EX + "ext/target"),
        _birthdate_case(BIRTH_TIME),            # -> datetime (toPython)
        _birthdate_case(BIRTH_TIME, True),      # -> the Literal itself
        _birthdate_case(EX + "ext/other"),      # the neighbour -> "neighbour"
        _case(EX + "patient4", EX + "ext/target"),  # two urls -> UniquenessError
        _case(EX + "patient5", EX + "ext/target"),  # no url -> None
    ],
)
