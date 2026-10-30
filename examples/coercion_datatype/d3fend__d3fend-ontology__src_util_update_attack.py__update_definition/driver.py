"""Validation driver for d3fend__d3fend-ontology__src_util_update_attack.py__update_definition.

Establishes semantic equivalence of original.py and translated.ldpy by
calling update_definition(graph, tech, framework) several times. Each call
gets fresh graphs (the fixtures are callables, see rdfeval.harness.run_pair),
and both the return value and the mutated `graph` are compared. The attack
URI is <d3fend#>T1055, built from the shim's _xmlns.

  0. the attack_id is a bare literal in the graph, no d3fend:definition yet:
     both guards take their True branch, one triple is added, returns 1.
     A neighbouring triple (rdfs:label "T1055" on another subject) is what the
     wildcard `?s ?p` of the `in graph` guard matches.
  1. the graph does NOT contain the literal "T1055" at all (only an unrelated
     label): the `in graph` guard is False, nothing is written, returns 0.
     Kills a guard replaced by True.
  2. the attack_uri already has a d3fend:definition: the `def_property is
     None` guard is False, nothing is written, returns 0. Kills that guard
     replaced by True (and a read that ignores the existing value).
  3. the only neighbour is Literal("T1055", datatype=xsd:string): it is not
     equal to the plain Literal("T1055") (rdflib: datatype None vs xsd:string),
     so the guard must stay False and nothing is written (returns 0). Kills a
     translation that types the interpolated attack_id.
  4. same, with a language-tagged neighbour Literal("T1055", lang="en").
  5. a multi-line description with surrounding blanks: only the first line,
     stripped, is written (strip/split/strip chain).
  6. an empty description: Literal("") is written, returns 1 (the value `""`
     must survive the coercion of `{...}`).
  7. a description that looks like an IRI (http://...): still a plain
     literal, not an URIRef.
  8. quotes, braces and backslashes in the description.
  9. the definition is present on ANOTHER technique but not on this one: the
     read `m{ {attack_uri} d3fend:definition ?v }` must be bound to the
     subject, so one is still added (returns 1).

attack_id and description are `str` in the repository (get_attack_id returns
the STIX external_id, description comes from tech['data']).
"""
from rdfeval.harness import run_pair

D3F = "http://d3fend.mitre.org/ontologies/d3fend.owl#"


def _tech(description="Process Injection.\nAdversaries may inject code into running processes.",
          external_id="T1055"):
    return {
        "data": {
            "external_references": [
                {"source_name": "mitre-attack", "external_id": external_id},
            ],
            "description": description,
        }
    }


def _make(triples, description=None):
    """Build a fixture: a fresh Graph holding `triples` (a function returning them)."""
    def fixture():
        from rdflib import Graph
        graph = Graph()
        for t in triples():
            graph.add(t)
        tech = _tech() if description is None else _tech(description)
        return ((graph, tech, "enterprise"), {})
    return fixture


def _label_plain():
    from rdflib import URIRef, RDFS, Literal
    return [(URIRef("http://example.org/technique/T1055"), RDFS.label, Literal("T1055"))]


def _label_other():
    from rdflib import URIRef, RDFS, Literal
    return [(URIRef("http://example.org/technique/T1055"), RDFS.label, Literal("T9999"))]


def _already_defined():
    from rdflib import URIRef, RDFS, Literal
    return _label_plain() + [(URIRef(D3F + "T1055"), URIRef(D3F + "definition"),
                              Literal("An existing definition."))]


def _typed_neighbour():
    from rdflib import URIRef, RDFS, Literal, XSD
    return [(URIRef("http://example.org/technique/T1055"), RDFS.label,
             Literal("T1055", datatype=XSD.string))]


def _lang_neighbour():
    from rdflib import URIRef, RDFS, Literal
    return [(URIRef("http://example.org/technique/T1055"), RDFS.label,
             Literal("T1055", lang="en"))]


def _defined_elsewhere():
    from rdflib import URIRef, Literal
    return _label_plain() + [(URIRef(D3F + "T9999"), URIRef(D3F + "definition"),
                              Literal("Definition of another technique."))]


VERDICT = run_pair(
    __file__,
    entry='update_definition',
    calls=[
        _make(_label_plain),
        _make(_label_other),
        _make(_already_defined),
        _make(_typed_neighbour),
        _make(_lang_neighbour),
        _make(_label_plain, "  \n  First line, padded.  \nSecond line is dropped.\n"),
        _make(_label_plain, ""),
        _make(_label_plain, "http://example.org/looks-like-an-iri\nmore"),
        _make(_label_plain, 'He said "hi" {x} \\ back\\slash\nrest'),
        _make(_defined_elsewhere),
    ],
)
