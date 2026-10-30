"""Validation driver for altunelyusuf__SemanticTechnologies__landscape_07-tooling_build_page_v4_0_0.py__<module>_53.

Establishes semantic equivalence of original.py and translated.ldpy.

Module-state region: both sides parse the repository's real
04-page/semtech_page_abox_v3_0_0.ttl into `g` (page_context.HERE points at
the clone) and add one triple.  Compared:

  * run_pair, entry=None: `g` by isomorphism, and the shared module values
    (ONT);
  * the prefix bindings of `g`: the repository serialises this graph to
    04-page/semtech_page_abox_v4_0_0.ttl (build_page_v4_0_0.py:100), so
    every binding the original's `g` carries -- the ten prefixes of the
    parsed file plus rdflib's defaults -- must be on the translation's
    (extra ones are tolerated, record ldpy/027).  This catches an `@graph g`
    whose `@prefix` rebinds a namespace the parsed file had bound under
    another name.
"""
import contextlib
import io
import json
import sys
from pathlib import Path

from rdfeval import harness
from rdfeval.harness import run_pair

ex_dir = Path(__file__).resolve().parent


def _quiet(**kwargs) -> dict:
    """run_pair's verdict without its stderr line: this driver emits one."""
    with contextlib.redirect_stderr(io.StringIO()):
        return run_pair(**kwargs)


def _bindings() -> list[str]:
    left, right = harness.sides_from_env()
    ns_o, _ = harness._exec_artefact(ex_dir / left, "__original__")
    ns_t, _ = harness._exec_artefact(ex_dir / right, "__translated__")
    missing = set(ns_o["g"].namespaces()) - set(ns_t["g"].namespaces())
    if missing:
        return ["prefix bindings lost "
                f"{sorted((p, str(n)) for p, n in missing)}"]
    return []


as_written = _quiet(driver_file=__file__, entry=None, calls=None)
try:
    extra, extra_error = _bindings(), None
except Exception:
    import traceback
    extra, extra_error = [], traceback.format_exc(limit=8)

verdict = dict(as_written)
verdict["method"] = f"{as_written.get('method')} (+ prefix bindings of g)"
verdict["diffs"] = list(as_written.get("diffs", [])) + extra
errors = [e for e in (as_written.get("error"), extra_error) if e]
verdict["error"] = "\n".join(errors) or None
verdict["equivalent"] = (bool(as_written.get("equivalent"))
                         and not extra and not extra_error)
print("RDFEVAL-VERDICT " + json.dumps(verdict), file=sys.stderr)
VERDICT = verdict
