"""Validation driver for
kracr__cog-csv-owl-bridge__src_csv_to_owl_csv_owl_code.py__csv_to_owl_subclass.

Establishes semantic equivalence of original.py and translated.ldpy.

csv_to_owl_subclass's whole observable effect is the OWL file it serializes
-- it takes no graph argument to mutate and returns nothing -- so
``run_pair(entry=...)`` alone would only ever compare the (trivially equal)
string arguments: a hollow green. Instead we call each side's function
directly and, for every case below, compare:

  * whether each side wrote its output file (the missing-CSV case writes
    none);
  * the two RDF/XML files, by isomorphism;
  * the prefix bindings: every ``xmlns`` (prefix, namespace) the
    original's file declares must be declared by the translation's file too (``@graph`` may
    add the bindings of its block, design record ldpy/027, which is
    tolerated);
  * the return value and what the call printed (its [WARN] lines decide
    which branch a row fell into), the output path being replaced by a
    placeholder since the two sides write to different files.

Cases:

  ``synthetic``  the CSV the translator wrote: simple A <= B, a textual
                 ``some`` restriction, an ``&`` intersection with a
                 superclass, A <= (some R.C), a GCI row with ``all``, and an
                 empty row.
  ``branches``   (repair 2026-10-30) the rows ``synthetic`` never reaches:
                 A <= (all R.C) -- the ``owl:allValuesFrom`` island of the
                 A <= R.C case, and an ``only`` quantifier, which takes the
                 same ``else``; an upper-case ``SOME`` (lower-cased by the
                 region); a textual ``all`` restriction (``build_restriction``
                 else branch from the textual case); a textual restriction
                 with no superclass (WARN, then falls through to the
                 "unhandled" WARN); an intersection without a superclass
                 (its subClassOf island must NOT fire); a row with subclass,
                 property and superclass but no quantifier (falls to the
                 simple A <= B case); a row with only a property (unhandled
                 WARN); and a GCI with ``some``.
  ``repo``       the repository's own input files, verbatim
                 (``Testing & Output/Output- OWL_to_CSV/subclass.csv`` and
                 ``prefixiri.csv``): a default ``:`` prefix bound to the OWL
                 namespace beside ``owl:`` itself, an ``xml:base``, and the
                 column order Subclass, onProperty, quantifier, Superclass.
  ``missing``    a subclass CSV that does not exist: both sides print the
                 WARN, return None and write no file.
"""
import contextlib
import io
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

from rdflib import Graph

from rdfeval import harness

_TMP = tempfile.mkdtemp(prefix="csv_owl_subclass_")
ex_dir = Path(__file__).resolve().parent

_PREFIX_CSV = """prefix,namespace
ex,http://example.org/onto#
"""

_SUBCLASS_CSV = """Subclass,Superclass,Restriction (onProperty),Restriction (quantifier)
ex:Cat,ex:Animal,,
ex:hasOwner some ex:Person,ex:Dog,,
ex:Cat & ex:Pet,ex:HouseholdAnimal,,
ex:Fish,ex:Animal,ex:livesIn,some
,ex:Water,ex:contains,all
,,,
"""

_BRANCHES_CSV = """Subclass,Superclass,Restriction (onProperty),Restriction (quantifier)
ex:Bird,ex:Wing,ex:has,all
ex:Snake,ex:Scale,ex:coveredBy,only
ex:Whale,ex:Ocean,ex:livesIn,SOME
ex:eats all ex:Plant,ex:Herbivore,,
ex:hasOwner some ex:Person,,,
ex:Cat & ex:Pet,,,
ex:Mouse,ex:Rodent,ex:livesIn,
,,ex:orphanProperty,
,ex:Land,ex:walksOn,some
"""


def _write(name: str, text: str) -> str:
    path = os.path.join(_TMP, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


_prefix_path = _write("prefixes.csv", _PREFIX_CSV)
CASES = [
    ("synthetic", _write("subclass.csv", _SUBCLASS_CSV), _prefix_path),
    ("branches", _write("branches.csv", _BRANCHES_CSV), _prefix_path),
    ("repo", str(ex_dir / "subclass_repo.csv"), str(ex_dir / "prefixiri_repo.csv")),
    ("missing", os.path.join(_TMP, "no_such_subclass.csv"), _prefix_path),
]


def _call(fn, case, side, csv_path, prefix_path):
    out_file = os.path.join(_TMP, f"{case}_{side}.owl")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        result = fn(csv_path, prefix_path, output_file=out_file)
    return result, buf.getvalue().replace(out_file, "<OUT>"), out_file


def _bindings(path: str) -> set:
    """The ``xmlns`` declarations of the written file's root element.

    Parsing the file back cannot give them: a fresh Graph() already carries
    rdflib's default bindings and the RDF/XML parser binds nothing new.  The
    serializer only declares the namespaces it uses, so this is exactly what
    the repository writes to disk.
    """
    text = Path(path).read_text(encoding="utf-8")
    root = text[text.index("<rdf:RDF"):text.index(">", text.index("<rdf:RDF"))]
    return set(re.findall(r'xmlns(?::([\w.-]+))?="([^"]*)"', root))


verdict: dict = {"example": ex_dir.name, "equivalent": False,
                 "method": "entry:csv_to_owl_subclass (output files, isomorphism, "
                           "bindings, stdout)",
                 "diffs": [], "error": None}
try:
    ns_o, out_o = harness._exec_python(ex_dir / "original.py")
    ns_t, out_t = harness._exec_ldpy(ex_dir / "translated.ldpy")
    diffs = []
    if out_o != out_t:
        diffs.append("module-level stdout differs")
    for case, csv_path, prefix_path in CASES:
        r_o, s_o, f_o = _call(ns_o["csv_to_owl_subclass"], case, "o", csv_path, prefix_path)
        r_t, s_t, f_t = _call(ns_t["csv_to_owl_subclass"], case, "t", csv_path, prefix_path)
        if r_o != r_t:
            diffs.append(f"{case}: return value differs ({r_o!r} vs {r_t!r})")
        if s_o != s_t:
            diffs.append(f"{case}: stdout differs ({s_o[-300:]!r} vs {s_t[-300:]!r})")
        if os.path.exists(f_o) != os.path.exists(f_t):
            diffs.append(f"{case}: output file written on one side only")
            continue
        if not os.path.exists(f_o):
            continue
        g_o = Graph().parse(f_o, format="xml")
        g_t = Graph().parse(f_t, format="xml")
        if not harness.graphs_isomorphic(g_o, g_t):
            diffs.append(f"{case}: output graphs not isomorphic "
                         f"({len(g_o)} vs {len(g_t)} triples)")
        lost = _bindings(f_o) - _bindings(f_t)
        if lost:
            diffs.append(f"{case}: prefix bindings lost by the translation: {sorted(lost)}")
    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
    verdict["calls"] = len(CASES) * 2
except Exception:
    import traceback
    verdict["error"] = traceback.format_exc(limit=8)
finally:
    shutil.rmtree(_TMP, ignore_errors=True)

print("RDFEVAL-VERDICT " + json.dumps(verdict), file=sys.stderr)
VERDICT = verdict
