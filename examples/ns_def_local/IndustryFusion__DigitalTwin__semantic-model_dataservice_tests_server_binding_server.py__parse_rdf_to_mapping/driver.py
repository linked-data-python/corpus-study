"""Validation driver for IndustryFusion__DigitalTwin__semantic-model_dataservice_tests_server_binding_server.py__parse_rdf_to_mapping.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

The function itself calls ``g.parse(rdf_file, format="turtle")`` on its first
argument, so it wants a *path*, not a pre-parsed Graph -- the harness's
default fixture= wiring (which passes a parsed Graph as the sole argument)
does not fit, hence the explicit ``calls=``.  ``binding_ns``/``uaentity_ns``
are supplied directly so the run never takes the
``g.namespace_manager.store.namespace(...)`` fallback branch, which is
unrelated to this region's stratum (ns_def_local: the local ``BASE =
Namespace(base_ns)``) and to the constructions this pair exercises.

Repair of 2026-10-30 -- calls added, none removed:

* ``_args_found_ns``: binding_ns and uaentity_ns None, so the region reads
  them from the graph's namespace manager.  In the translation ``@graph g``
  and ``@prefix base:`` bind prefixes on that same graph first; this call
  shows the lookup still finds them.
* ``_args_real``: ``fixture_real.ttl``, a verbatim bindings file of the
  repository, under the CLI's default ``--base-ns`` (binding_server.py:213),
  binding_ns read from the file and uaentity_ns given.  A second base IRI is
  what proves ``@prefix base: f<{base_ns}>`` follows the parameter: a
  translation with the IRI written as a constant passes the first call only.
* ``_branch_cases`` (run before ``run_pair``, which cannot carry them): the
  ``opcua:String`` and default branches return the class ``str``, which the
  harness cannot materialise, and the two guards end in ``sys.exit(1)``, a
  BaseException the harness does not catch.  Both artefacts are executed
  through the harness's own helpers and called on ``fixture_branches.ttl``;
  the driver compares the mapping with each ``datatype`` replaced by its
  name, the exit code, and the printed lines (the warning, the error
  message) as a multiset.  A
  difference ends the driver with a failing verdict before ``run_pair``.
"""
import contextlib
import io
import sys
from pathlib import Path

from rdfeval.harness import _emit, _exec_ldpy, _exec_python, run_pair

_HERE = Path(__file__).parent
_FIXTURE = str(_HERE / "fixture.ttl")
_BASE_NS = "http://example.org/vocab#"
_BRANCHES = str(_HERE / "fixture_branches.ttl")
_REAL = str(_HERE / "fixture_real.ttl")
_REAL_BASE_NS = "https://industryfusion.github.io/contexts/ontology/v0/base/"


def _args_found_ns():
    return ((_FIXTURE, _BASE_NS), {"binding_ns": None, "uaentity_ns": None})


def _args_real():
    return ((_REAL, _REAL_BASE_NS),
            {"binding_ns": None,
             "uaentity_ns": "http://yourorganisation.org/InstanceExample/entity/"})


_BRANCH_CALLS = [
    # String branch, default branch twice, falsy connectors, neighbours,
    # and a map with two values of each property (no join may multiply it).
    ((_BRANCHES, _BASE_NS), {"binding_ns": "http://example.org/binding#",
                             "uaentity_ns": "http://example.org/uaentity#"}),
    # No binding: prefix in the file and none given -> first sys.exit(1).
    ((_BRANCHES, _BASE_NS), {"uaentity_ns": "http://example.org/uaentity#"}),
    # binding: found in the file, no uaentity: anywhere -> second sys.exit(1).
    ((_REAL, _REAL_BASE_NS), {}),
]


def _outcome(fn, args, kwargs):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        try:
            result = fn(*args, **kwargs)
            got = ("returned", {k: dict(v, datatype=getattr(
                v["datatype"], "__name__", v["datatype"]))
                for k, v in result.items()})
        except SystemExit as e:
            got = ("exit", e.code)
        except Exception as e:                    # noqa: BLE001 - compared
            got = ("raised", type(e).__name__, str(e))
    # The lines come out in the order the store yields BoundMaps, which no
    # store promises: compared as a multiset, like the harness's values.
    return got, sorted(out.getvalue().splitlines())


def _branch_cases():
    ns_o, _ = _exec_python(_HERE / "original.py")
    ns_t, _ = _exec_ldpy(_HERE / "translated.ldpy")
    diffs = []
    for i, (args, kwargs) in enumerate(_BRANCH_CALLS):
        o = _outcome(ns_o["parse_rdf_to_mapping"], args, kwargs)
        t = _outcome(ns_t["parse_rdf_to_mapping"], args, kwargs)
        if o != t:
            diffs.append(f"branch_call[{i}]: {o!r} vs {t!r}")
    return diffs


_DIFFS = _branch_cases()
if _DIFFS:
    _emit({"example": _HERE.resolve().name, "equivalent": False,
           "method": "branch cases (driver.py)", "diffs": _DIFFS,
           "error": None})
    sys.exit(1)


def _args():
    return (
        (_FIXTURE, _BASE_NS),
        {"binding_ns": "http://example.org/binding#", "uaentity_ns": "http://example.org/uaentity#"},
    )


VERDICT = run_pair(
    __file__,
    entry='parse_rdf_to_mapping',
    calls=[_args, _args_found_ns, _args_real],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)
