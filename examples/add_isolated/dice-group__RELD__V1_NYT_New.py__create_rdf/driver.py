"""Validation driver for dice-group__RELD__V1_NYT_New.py__create_rdf.

Establishes semantic equivalence of original.py and translated.ldpy.

The region is a module-level script fragment: its input (``info``,
``subject_dict``, ``object_dict``) is a fixture block written identically in
both artefacts, and run_pair's module-state comparison checks every graph
and every module-level value (counters, last ids and strings) both define.

Two runs, one verdict:

``as-written``  the artefacts as they are.  Their fixture never reaches the
                ``containsNumber`` and ``check_type`` branches, for the
                subject or the object: the text that ``returnValue`` gives
                back ("Some Subject", "NumKey", ...) holds no digit, so only
                the ``else`` is taken.

``extended``    (repair 2026-10-30) the same artefacts with that fixture
                block replaced, textually and identically on both sides, by
                ``EXTENDED`` below; they run from a temporary directory.  The
                seam is the input, never the region, and the artefacts keep
                their size for the study's metrics.  The added entries take
                the shape the repository really builds (V1/NYT_New.py
                ``structured_data``: subject and object are int counters
                starting at 0, keyed by their surface text; the sentence dict
                comes from V1/sentence.py ``tokenize``: int counts, possibly
                0, and a bool ``direction``):

                - counter 0, text "Apollo 11" / "Route 66": a digit, so the
                  two ``containsNumber`` branches (the label keeps the raw
                  text where ``else`` would give "Apollo_11");
                - counter 1, text "..." / "": no digit, only dots or nothing,
                  so the two ``check_type`` branches ("..." where ``else``
                  would give ""; the empty text is also the falsy case);
                - several non-entity keys, a count of 0 and a bool, so
                  ``prop:{key}`` sees more than ``score``;
                - ``val[3] == 0``: a falsy numOfRelation.
"""
import contextlib
import io
import json
import shutil
import sys
import tempfile
from pathlib import Path

from rdfeval.harness import ARTEFACTS, run_pair

ex_dir = Path(__file__).resolve().parent

FIXTURE_START = "info = [\n"
FIXTURE_END = 'object_dict = {"Some Object": "objA", "ObjNum": "456"}\n'
EXTENDED = '''info = [
    ("subjA", "objA", [
        ("A sentence about entities.", {
            "listOfNamedEntities": [("Entity One", "Person"), ("Entity Two!", "Organization")],
            "score": 5,
        }),
    ], 2, "distA"),
    ("123", "456", [
        ("Another sentence with numbers.", {"listOfNamedEntities": [], "score": 7}),
    ], 1, "distB"),
    (0, 0, [
        ("Apollo 11 took Route 66.", {
            "listOfNamedEntities": [("Apollo 11", "CARDINAL")],
            "numOfSubToken": 2, "numOfTokens": 0, "direction": False,
        }),
    ], 0, "train"),
    (1, 1, [
        ("Dots and nothing.", {
            "listOfNamedEntities": [("Dots", "GPE"), ("Nothing", "ORG")],
            "numBefToken": 3, "direction": True,
        }),
    ], 4, "test"),
]
subject_dict = {"Some Subject": "subjA", "NumKey": "123", "Apollo 11": 0, "...": 1}
object_dict = {"Some Object": "objA", "ObjNum": "456", "Route 66": 0, "": 1}
'''


def _extend(text: str, name: str) -> str:
    if text.count(FIXTURE_START) != 1 or text.count(FIXTURE_END) != 1:
        raise ValueError(f"{name}: fixture block not found exactly once")
    i = text.index(FIXTURE_START)
    j = text.index(FIXTURE_END) + len(FIXTURE_END)
    return text[:i] + EXTENDED + text[j:]


def _quiet(**kwargs) -> dict:
    """run_pair's verdict without its stderr line: this driver emits one."""
    with contextlib.redirect_stderr(io.StringIO()):
        return run_pair(**kwargs)


work = Path(tempfile.mkdtemp(prefix="reld_create_rdf_"))
try:
    as_written = _quiet(driver_file=__file__)
    try:
        for name in ARTEFACTS:
            if (ex_dir / name).exists():
                (work / name).write_text(_extend((ex_dir / name).read_text(), name))
        extended = _quiet(driver_file=str(work / "driver.py"))
    except ValueError as e:
        extended = {"equivalent": False, "diffs": [], "error": str(e)}
finally:
    shutil.rmtree(work, ignore_errors=True)

verdict = dict(as_written)
verdict["method"] = f"{as_written.get('method')} (as-written + extended fixture)"
verdict["diffs"] = ([f"as-written: {d}" for d in as_written.get("diffs", [])]
                    + [f"extended: {d}" for d in extended.get("diffs", [])])
errors = [f"{k}: {v['error']}" for k, v in
          (("as-written", as_written), ("extended", extended)) if v.get("error")]
verdict["error"] = "\n".join(errors) or None
verdict["runs"] = {"as-written": as_written.get("equivalent"),
                   "extended": extended.get("equivalent")}
verdict["equivalent"] = bool(as_written.get("equivalent")
                             and extended.get("equivalent"))
print("RDFEVAL-VERDICT " + json.dumps(verdict), file=sys.stderr)
VERDICT = verdict
