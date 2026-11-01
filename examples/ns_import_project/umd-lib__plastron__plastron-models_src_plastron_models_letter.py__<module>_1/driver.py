"""Driver for plastron-models `letter.py` (module region).

The module has no function to call and prints nothing: it defines six
classes whose class bodies bind rdflib IRIs (from `plastron.namespaces`)
to RDF properties. `run_pair(entry=None)` would find no graph and no value
to compare and report "nothing observable" — a hollow green. So the driver
executes both artefacts itself and compares what the classes DO:

  * the property table of every class: attribute -> (predicate, required,
    repeatable, datatype, embed, target class, ...);
  * the default `rdf:type` values each class stamps on its instances;
  * `model_name`, `is_top_level`, `HEADER_MAP`;
  * instances actually built and filled through those descriptors: the
    graph each produces (by isomorphism), `validate()` per property and
    `is_valid` — a valid letter, an empty one, one with a malformed date,
    an authority record (Agent / Concept / Place / Collection) each.

A namespace term mistranslated (`dcterms:title` for `dc:title`, ...) changes
a predicate in the table and a triple in every graph.
"""
import json
import sys
import traceback
from pathlib import Path

from rdflib import Graph, Literal, URIRef

from rdfeval import harness

EDTF = URIRef("http://id.loc.gov/datatypes/edtf")
CLASSES = ["AuthorityRecord", "Agent", "Concept", "Place", "Collection", "Letter"]


def _plain(g):
    out = Graph()
    for t in g:
        out.add(t)
    return out


def _table(cls):
    from plastron.rdfmapping.descriptors import Property
    props = {}
    for klass in reversed(cls.__mro__):
        for name, v in vars(klass).items():
            if isinstance(v, Property) and name in cls.rdf_property_names:
                oc = getattr(v, "object_class", None)
                props[name] = (
                    str(v.predicate), v.required, v.repeatable,
                    str(getattr(v, "datatype", None)),
                    getattr(v, "embed", None),
                    oc if isinstance(oc, (str, type(None))) else oc.__name__,
                )
    return props


def _defaults(cls):
    return {k: sorted(str(x) for x in v) for k, v in cls.default_values.items()}


def _report(r):
    return {k: bool(v) for k, v in sorted(r.items())}


def _letter(ns, uri, **extra):
    L = ns["Letter"](uri=URIRef(uri))
    L.set_properties(
        title=Literal("Dear John"), identifier=Literal("ltr-1"),
        type=Literal("letter"), language=Literal("en"),
        description=Literal("A letter"), bibliographic_citation=Literal("Box 1"),
        extent=Literal("1 p."), rights_holder=Literal("UMD"),
        rights=URIRef("http://rightsstatements.org/vocab/InC/1.0/"),
        part_of=URIRef("http://example.org/collection/1"),
        **extra,
    )
    return L


def _scenarios(ns):
    out = {}
    out["classes"] = {c: {"table": _table(ns[c]), "defaults": _defaults(ns[c])}
                      for c in CLASSES}
    L = ns["Letter"]
    out["letter-attrs"] = {"model_name": L.model_name,
                           "is_top_level": L.is_top_level,
                           "HEADER_MAP": L.HEADER_MAP}
    graphs = {}
    reports = {}

    empty = L(uri=URIRef("http://example.org/letter/empty"))
    graphs["empty-letter"] = empty.graph
    reports["empty-letter"] = _report(empty.validate())

    full = _letter(ns, "http://example.org/letter/1",
                   date=Literal("1920-05-01", datatype=EDTF))
    full.add_properties(
        copyright_notice=Literal("(c) UMD"),
        member_of=URIRef("http://example.org/series/1"),
        author=URIRef("http://example.org/agent/a"),
        recipient=URIRef("http://example.org/agent/b"),
        place=URIRef("http://example.org/place/1"),
        subject=URIRef("http://example.org/concept/1"),
    )
    graphs["full-letter"] = full.graph
    reports["full-letter"] = _report(full.validate())
    reports["full-letter.is_valid"] = full.is_valid

    coerced = _letter(ns, "http://example.org/letter/2")
    coerced.date = "1920"          # coerced to a Literal typed with the edtf datatype
    graphs["coerced-date"] = coerced.graph
    reports["coerced-date"] = _report(coerced.validate())

    bad = _letter(ns, "http://example.org/letter/3",
                  date=Literal("not a date", datatype=EDTF))
    reports["bad-date"] = _report(bad.validate())
    reports["bad-date.is_valid"] = bad.is_valid

    agent = ns["Agent"](uri=URIRef("http://example.org/agent/a"),
                        same_as=[URIRef("http://example.org/id/1"),
                                 URIRef("http://example.org/id/2")])
    graphs["agent"] = agent.graph
    concept = ns["Concept"](uri=URIRef("http://example.org/concept/1"),
                            same_as=URIRef("http://example.org/id/3"))
    graphs["concept"] = concept.graph
    place = ns["Place"](uri=URIRef("http://example.org/place/1"),
                        lat=Literal("38.99"), long=Literal("-76.94"),
                        same_as=URIRef("http://example.org/id/4"))
    graphs["place"] = place.graph
    coll = ns["Collection"](uri=URIRef("http://example.org/collection/1"),
                            same_as=URIRef("http://example.org/id/5"))
    graphs["collection"] = coll.graph

    # an embedded author goes through the same graph as its parent
    emb = _letter(ns, "http://example.org/letter/4",
                  date=Literal("1921", datatype=EDTF))
    a = emb.get_fragment_resource(ns["Agent"], "author1")
    a.set_properties(same_as=URIRef("http://example.org/id/6"))
    emb.author.add(a)
    graphs["embedded-author"] = emb.graph

    return out, graphs, reports


def _observe(artefact, runner):
    ns, stdout = runner(Path(__file__).resolve().parent / artefact)
    plain, graphs, reports = _scenarios(ns)
    return plain, {k: _plain(g) for k, g in graphs.items()}, reports, stdout


ex_dir = Path(__file__).resolve().parent
verdict: dict = {"example": ex_dir.name, "equivalent": False,
                 "method": "custom: property tables, defaults, built instances "
                           "(isomorphism), validation reports",
                 "diffs": [], "error": None}
try:
    po, go, ro, so = _observe("original.py", harness._exec_python)
    pt, gt, rt, st = _observe("translated.ldpy", harness._exec_ldpy)
    diffs = []
    if so != st:
        diffs.append("stdout differs at module level")
    for k in po:
        if po[k] != pt[k]:
            diffs.append(f"{k}: differs ({po[k]!r:.150} vs {pt[k]!r:.150})")
    for k in ro:
        if ro[k] != rt[k]:
            diffs.append(f"validation {k}: differs ({ro[k]} vs {rt[k]})")
    for k in go:
        if not harness.graphs_isomorphic(go[k], gt[k]):
            diffs.append(f"graph {k}: not isomorphic ({len(go[k])} vs {len(gt[k])} triples)")
    # the original must show something, or this is a hollow green
    if not (len(go["full-letter"]) > 10 and any(ro["full-letter"].values())
            and not all(ro["empty-letter"].values())):
        diffs.append("hollow: the original's scenarios show nothing")
    verdict["calls"] = len(go) + len(ro) + len(po)
    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
except Exception:
    verdict["error"] = traceback.format_exc(limit=8)

print("RDFEVAL-VERDICT " + json.dumps(verdict), file=sys.stderr)
VERDICT = verdict
