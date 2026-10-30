"""Validation driver for openworm__owmeta-core__owmeta_core_dataobject.py__<module>_634.

The region is one class attribute of BaseDataObject, flattened to module
scope: ``base_data_namespace = R.Namespace(BASE_DATA_URL + "/")``.  Its whole
point is that the *name* survives the block and is a real rdflib Namespace:
owmeta_core/mapped_class.py:51-52 tests ``self.base_data_namespace is not
None`` and then subscripts it, ``self.base_data_namespace[self.__name__] +
'#'`` (datasource.py and dataobject_property.py define the same attribute).

The generic module-state comparison (``run_pair(entry=None)``) only compares
the names BOTH modules define, so a translation that no longer defines
``base_data_namespace`` at all (for instance ``@prefix basedata: f<...>``
without ``as base_data_namespace``) was reported equivalent.  This driver
compares that name explicitly, the way the repository uses it:

  * the name exists on both sides, is not None, is the same class
    (rdflib Namespace, hence a str) and the same string;
  * subscription, as mapped_class.py does it, for the class name
    ``BaseDataObject`` and for other keys, including "" and a key that
    contains a slash: the result is a URIRef, equal on both sides, and
    ``[...] + '#'`` is the same str as in the original;
  * attribute access (``ns.Foo``), ``ns.term('Foo')`` and ``'..' in ns``
    behave the same;
  * the other module-level names both sides define (BASE_DATA_URL, ...) are
    still compared by value, as module-state does, and the names only the
    original defines are listed in the verdict as ``names_only_original``.
"""
import traceback
from pathlib import Path

from rdfeval.harness import (_compare_value, _emit, _exec_ldpy, _exec_python,
                             _values)

NAME = "base_data_namespace"
KEYS = ["BaseDataObject", "Foo", "", "a/b", "x#y", "Neuron 1"]


def outcome(call):
    """Return value (typed), or the exception raised, as the repository sees it."""
    try:
        v = call()
        return ["returns", type(v).__name__, repr(v)]
    except Exception as e:  # noqa: BLE001 -- the exception IS the observation
        return ["raises", type(e).__name__, str(e)]


def observations(ns: dict) -> dict:
    """Everything the repository does with the name, by label."""
    obs: dict = {}
    obs["defined"] = NAME in ns
    if NAME not in ns:
        return obs
    n = ns[NAME]
    obs["is not None (mapped_class.py:51)"] = n is not None
    obs["class"] = type(n).__module__ + "." + type(n).__name__
    obs["is str"] = isinstance(n, str)
    obs["str"] = str(n)
    obs["len"] = len(n)
    for k in KEYS:
        obs[f"[{k!r}]"] = outcome(lambda: n[k])
        obs[f"[{k!r}] + '#' (mapped_class.py:52)"] = outcome(lambda: n[k] + "#")
    obs["[0]"] = outcome(lambda: n[0])
    obs[".Foo"] = outcome(lambda: n.Foo)
    obs[".term('Foo')"] = outcome(lambda: n.term("Foo"))
    obs["'http://data.openworm.org/Foo' in ns"] = \
        outcome(lambda: "http://data.openworm.org/Foo" in n)
    obs["'http://data.openworm.org/' in ns"] = \
        outcome(lambda: "http://data.openworm.org/" in n)
    obs["'http://data.openworm.org' in ns"] = \
        outcome(lambda: "http://data.openworm.org" in n)
    obs["startswith"] = n.startswith("http://data.openworm.org/")
    return obs


def main() -> dict:
    ex_dir = Path(__file__).resolve().parent
    verdict: dict = {"example": ex_dir.name, "equivalent": False,
                     "method": "custom:module-names", "diffs": [], "error": None}
    try:
        ns_o, out_o = _exec_python(ex_dir / "original.py")
        ns_t, out_t = _exec_ldpy(ex_dir / "translated.ldpy")
    except Exception:
        verdict["error"] = traceback.format_exc(limit=8)
        _emit(verdict)
        return verdict

    diffs: list[str] = []
    try:
        obs_o, obs_t = observations(ns_o), observations(ns_t)
    except Exception:
        verdict["error"] = traceback.format_exc(limit=8)
        _emit(verdict)
        return verdict
    if not obs_o["defined"]:
        diffs.append(f"original does not define {NAME}")
    if not obs_t["defined"]:
        diffs.append(f"translation does not define {NAME}")
    if obs_o.keys() != obs_t.keys():
        diffs.append("the two sides observed different cases")
    for label in obs_o:
        if label in obs_t and obs_o[label] != obs_t[label]:
            diffs.append(f"{label}: {obs_o[label]!r} vs {obs_t[label]!r}")

    # module-state, as run_pair does it, for every other shared value
    vo, vt = _values(ns_o), _values(ns_t)
    shared = sorted(set(vo) & set(vt))
    for name in shared:
        _compare_value(vo[name], vt[name], f"value {name}", diffs, True)
    verdict["values_compared"] = shared
    verdict["names_only_original"] = sorted(set(vo) - set(vt))
    if out_o != out_t:
        diffs.append("stdout differs")

    verdict["cases"] = len(obs_o)
    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
    _emit(verdict)
    return verdict


VERDICT = main()
