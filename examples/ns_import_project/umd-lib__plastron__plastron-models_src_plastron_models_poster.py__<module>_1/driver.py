"""Validation driver for umd-lib__plastron__plastron-models_src_plastron_models_poster.py__<module>_1.

The region is a module that defines one class, Poster, whose meaning is the
set of IRIs it hands to plastron's descriptors (``DataProperty(dcterms.title)``
...) and to ``@rdf_type``.  It builds no graph at module level, so run_pair's
module-state comparison would see nothing: the class is not a comparable
value.  This driver therefore executes both sides and compares what Poster
MEANS, by what it does:

  * the class-level facts: ``model_name``, ``is_top_level``, ``HEADER_MAP``
    and the set of mapped property names;
  * every descriptor, by name: its class, its predicate IRI, ``required``,
    ``repeatable``, ``datatype``, the class it maps to and its validator;
  * an instance, ``Poster(uri=...)``, filled through every descriptor: the
    triples of its graph (the ``@rdf_type`` types included) must be the
    same, term by term;
  * the validation outcome of an instance that is only half filled (which
    properties fail), so that ``required=`` flags are exercised too.

Mutants killed (each in a copy): any prefixed name pointing at the wrong
namespace or local name (``dc:date`` for ``dc:created``, ``dcterms:`` for
``dc:`` ...), the ``<...dc/elements/1.1/format>`` IRI altered, ``umd:Poster``
dropped from ``@rdf_type``.
"""
from pathlib import Path

from rdflib import Literal, URIRef

from rdfeval.harness import _emit, _exec_ldpy, _exec_python

HERE = Path(__file__).resolve().parent

verdict = {"example": HERE.name, "equivalent": False,
           "method": "module-state (hand-rolled: the Poster class, compared "
                     "by its descriptors and by an instance's graph)",
           "diffs": [], "error": None, "sides": ["original.py", "translated.ldpy"]}


def _describe(ns):
    P = ns["Poster"]
    out = {
        "model_name": P.model_name,
        "is_top_level": P.is_top_level,
        "header_map": dict(P.HEADER_MAP),
        "property_names": sorted(P.rdf_property_names),
    }

    p = P(uri=URIRef("http://example.org/poster/1"))
    p.title = "A title"
    p.alternative = "An alternative"
    p.publisher = "A publisher"
    p.part_of = "A collection"
    p.format = "image/png"
    p.type = Literal("poster")
    p.date = "2020-01-02"
    p.language = "en"
    p.description = "Description"
    p.extent = "10 cm"
    p.issue = "3"
    p.locator = "RG-1"
    p.location = "College Park"
    p.longitude = "-76.9"
    p.latitude = "38.9"
    p.subject.add(Literal("one"))
    p.subject.add(Literal("two"))
    p.rights = URIRef("http://example.org/rights/1")
    p.copyright_notice = "(c)"
    p.identifier = "id-1"
    p.place = URIRef("http://example.org/place/1")
    out["triples"] = sorted(" ".join(t.n3() for t in tr)
                            for tr in p.graph)

    descriptors = {}
    for name, d in sorted(vars(P).items()):      # the ones Poster itself defines
        if not hasattr(d, "predicate"):
            continue
        descriptors[name] = (
            type(d).__name__, str(d.predicate), d.required, d.repeatable,
            str(getattr(d, "datatype", None)),
            getattr(getattr(d, "object_class", None), "__name__", None),
            getattr(getattr(d, "validate", None), "__name__", None),
            getattr(getattr(d, "values_from", None), "__class__", type(None)).__name__)
    out["descriptors"] = descriptors

    q = P(uri=URIRef("http://example.org/poster/2"))
    q.title = "Only a title"
    q.language = "en"
    out["failing"] = sorted(k for k, v in q.validate().items()
                            if type(v).__name__ == "ValidationFailure")
    return out


try:
    ns_o, out_o = _exec_python(HERE / "original.py")
    ns_t, out_t = _exec_ldpy(HERE / "translated.ldpy")
    do, dt = _describe(ns_o), _describe(ns_t)
    if not do["triples"] or not do["descriptors"] or not do["failing"]:
        verdict["diffs"].append("hollow: the original showed nothing")
    for key in do:
        if do[key] != dt.get(key):
            if isinstance(do[key], dict):
                bad = sorted(k for k in set(do[key]) | set(dt[key])
                             if do[key].get(k) != dt[key].get(k))
                verdict["diffs"].append(f"{key} differs for {bad}")
            else:
                verdict["diffs"].append(
                    f"{key} differs ({do[key]!r:.150} vs {dt[key]!r:.150})")
    if out_o != out_t:
        verdict["diffs"].append("stdout differs")
    verdict["observed"] = {"descriptors": len(do["descriptors"]),
                           "triples": len(do["triples"]),
                           "failing": do["failing"]}
except Exception as e:  # noqa: BLE001 - reported
    import traceback
    verdict["error"] = traceback.format_exc(limit=6)
verdict["equivalent"] = not verdict["diffs"] and verdict["error"] is None
VERDICT = verdict
_emit(verdict)
