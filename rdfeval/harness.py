"""Execution/comparison helpers used by example validation drivers.

A driver calls :func:`run_pair`, which

  1. executes ``original.py`` and ``translated.ldpy`` (through the ldpy
     transpiler) in two fresh module namespaces, capturing stdout;
  2. either compares *module state* — every rdflib Graph in the globals,
     paired by variable name, PLUS every other module-level value both
     modules define (without which a region that only reads a graph gets a
     hollow green: its graphs are equal because nothing touched them) —
     or — when ``entry`` names a function — calls it with each fixture in
     ``calls`` and compares the results;
  3. graph comparison is rdflib graph isomorphism (``rdflib.compare``),
     never raw serialisation; other values are normalised
     (term-by-term for lists/tuples/sets/dicts, attribute by attribute for
     an instance without ``__eq__``, a blank node by its place in the
     graphs of its side) then compared for equality.

**Reading regions** (the oracle of design record ``corpus/403``) are not
covered by graph isomorphism: they produce *values*, so the oracle is the
equality of what the two versions produce from the same input graph.  Pass
``fixture=`` a Turtle file and :func:`run_pair` parses it into a fresh graph
per side and calls the entry point with it.  Two properties of RDF reading
shape the comparison:

  * a lazy result — a generator, an rdflib ``Result``, an ldpy match — is
    **materialised** before anything is compared, on both sides;
  * the order in which a store yields solutions is not specified, so results
    are compared as **multisets** unless ``ordered=True`` says the region
    itself imposes an order (it sorts, or the query has an ``ORDER BY``).

**Which two artefacts.**  By default the pair is ``original.py`` against
``translated.ldpy``.  A region may also carry the two *optimized* artefacts
of design record ``corpus/403`` — ``optimized.py`` (the most compact
equivalent Python) and ``optimized.ldpy`` (the most compact LD Python).  The
same driver proves them: ``RDFEVAL_SIDES=original.py,optimized.py`` in the
environment swaps the right-hand side, so each driver is written once and
:mod:`rdfeval.check` runs it once per artefact.  Each optimized artefact is
proved against the ORIGINAL, never against the other optimized one: a chain
of proofs would let one error excuse another.

The verdict is a JSON-serialisable dict; drivers print it so the validate
stage can collect it from a subprocess.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import traceback
from pathlib import Path


DEFAULT_SIDES = ("original.py", "translated.ldpy")
SIDES_ENV = "RDFEVAL_SIDES"
ARTEFACTS = ("original.py", "translated.ldpy", "optimized.py", "optimized.ldpy")

# The artefacts this process actually executed, by file name.  A driver that
# reads its files some other way cannot then claim to have compared the
# sides it was asked for (see ``_emit``).
_EXECUTED: list[str] = []


def sides_from_env() -> tuple[str, str]:
    """The two artefacts to compare, from ``RDFEVAL_SIDES`` (``a,b``)."""
    raw = os.environ.get(SIDES_ENV)
    if not raw:
        return DEFAULT_SIDES
    names = tuple(n.strip() for n in raw.split(","))
    if len(names) != 2 or not all(n in ARTEFACTS for n in names):
        raise ValueError(f"{SIDES_ENV}={raw!r}: expected two of {ARTEFACTS}")
    return names


def _run_python(path: Path, name: str) -> tuple[dict, str]:
    ns: dict = {"__name__": name, "__file__": str(path)}
    out = io.StringIO()
    code = compile(path.read_text(), str(path), "exec")
    with contextlib.redirect_stdout(out):
        exec(code, ns)
    return ns, out.getvalue()


def _run_ldpy(path: Path, name: str) -> tuple[dict, str]:
    from ldpy.transpiler import transpile
    r = transpile(path.read_text(), filename=str(path))
    ns: dict = {"__name__": name, "__file__": str(path)}
    out = io.StringIO()
    code = compile(r.code, str(path), "exec")
    with contextlib.redirect_stdout(out):
        exec(code, ns)
    return ns, out.getvalue()


def _exec_artefact(path: Path, name: str) -> tuple[dict, str]:
    """Run a ``.py`` as Python and a ``.ldpy`` through the transpiler."""
    path = Path(path)
    _EXECUTED.append(path.name)
    run = _run_ldpy if path.suffix == ".ldpy" else _run_python
    return run(path, name)


def _redirected(path: Path) -> Path:
    """The artefact ``RDFEVAL_SIDES`` puts in place of a default one.

    Some drivers do not call :func:`run_pair`: they execute the two files
    themselves, by name, through the two helpers below.  Redirecting here
    lets the same driver prove an optimized artefact without being edited —
    ``original.py`` becomes the left side, ``translated.ldpy`` the right.
    """
    path = Path(path)
    left, right = sides_from_env()
    swap = {"original.py": left, "translated.ldpy": right}
    return path.with_name(swap.get(path.name, path.name))


def _exec_python(path: Path, name: str = "__original__") -> tuple[dict, str]:
    return _exec_artefact(_redirected(path), name)


def _exec_ldpy(path: Path, name: str = "__translated__") -> tuple[dict, str]:
    return _exec_artefact(_redirected(path), name)


def fixture_graph(path) -> object:
    """A fresh graph parsed from a Turtle fixture.

    Called once per side, so a region that also *writes* cannot leak its
    effects into the other version's input.
    """
    from rdflib import Graph
    p = Path(path)
    return Graph().parse(source=str(p), format="turtle")


_ATOMIC = (str, bytes, bytearray, dict, set, frozenset, list, tuple)


def materialise(value):
    """Walk a lazy result until it is comparable.

    ``g.objects(...)`` is a generator, ``g.query(...)`` an rdflib ``Result``,
    ``m{ }`` a lazy match: none of them compares as a value, and each is
    consumed by being read.  Everything iterable that is not already a
    container, a string or a graph becomes a list; rows become tuples.
    """
    from rdflib import Graph
    from rdflib.query import Result, ResultRow
    if isinstance(value, Result):
        if value.type == "ASK":
            return bool(value)
        return [materialise(row) for row in value]
    if isinstance(value, ResultRow):
        return tuple(value)
    if isinstance(value, (Graph, str, bytes, bytearray)):
        return value
    if isinstance(value, dict):
        return {k: materialise(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return type(value)(materialise(v) for v in value)
    if isinstance(value, (set, frozenset)):
        return {materialise(v) for v in value}
    if hasattr(value, "__iter__") and not isinstance(value, _ATOMIC):
        return [materialise(v) for v in value]
    return value


def _filtered(text: str, stdout_filter) -> str:
    return stdout_filter(text) if stdout_filter is not None else text


def _unordered(value, bnodes: dict | None = None):
    """A comparison key that ignores order — at EVERY depth — not multiplicity.

    "No store promises an order" is not a property of the top-level value: a
    region that returns ``{"Add": {"hasReagent": [...]}}`` built from
    solutions has the same non-determinism one level down.  Comparing only
    the outer list would fail such a pair for a reason that is not its
    meaning.  A region that *does* impose an order says ``ordered=True``, and
    then nothing is sorted.

    A tuple is a row, not a collection: its positions are its meaning (a
    region returning ``(concept, label)`` is not one returning ``(label,
    concept)``), so only its elements are made order-free, never the tuple.
    """
    value = normalise(value, bnodes)
    if isinstance(value, dict):
        return {k: _unordered(v) for k, v in sorted(value.items(), key=repr)}
    if isinstance(value, tuple):
        return tuple(_unordered(v) for v in value)
    if isinstance(value, list):
        return sorted((_unordered(v) for v in value), key=repr)
    return value


def _graphs(ns: dict) -> dict[str, object]:
    from rdflib import Graph
    return {k: v for k, v in ns.items()
            if isinstance(v, Graph) and not k.startswith("_")}


def _comparable(value, depth: int = 0) -> bool:
    """Is this value something the study can judge equal or not?

    RDF terms, primitives, and containers of those.  Deliberately NOT an
    arbitrary object: two module executions build two instances, and a class
    without ``__eq__`` compares by identity, so including them would report a
    difference on every pair.  A logger, a typing alias, an open file are not
    results either.
    """
    from rdflib.term import Node
    if depth > 4:
        return False
    if value is None or isinstance(value, (str, bytes, bool, int, float, Node)):
        return True
    if isinstance(value, (list, tuple, set, frozenset)):
        return all(_comparable(v, depth + 1) for v in value)
    if isinstance(value, dict):
        return all(isinstance(k, (str, bytes, int, float, Node))
                   and _comparable(v, depth + 1) for k, v in value.items())
    return False


def _values(ns: dict) -> dict[str, object]:
    """Module-level results worth comparing, other than graphs.

    A region that neither builds nor mutates a graph — a computation over a
    graph it only reads — leaves its result in a module variable.  Comparing
    only graphs there gives a HOLLOW GREEN: the graphs are equal because
    nothing touched them, and a wrong translation passes.
    """
    from rdflib import Graph
    return {k: v for k, v in ns.items()
            if not k.startswith("_") and not isinstance(v, Graph)
            and _comparable(v)}


def graphs_isomorphic(g1, g2) -> bool:
    from rdflib.compare import to_isomorphic
    return to_isomorphic(g1) == to_isomorphic(g2)


_MAX_DEPTH = 4


def _structural(value) -> bool:
    """An instance compared by its attributes rather than by identity.

    A driver that restores a missing ``self`` builds one stub per side; a
    class without ``__eq__`` compares them by identity, and the pair failed
    for a reason that has nothing to do with the translation.  Classes,
    modules and functions keep their identity: two functions are not equal
    because both have an empty ``__dict__``.
    """
    import inspect
    return (hasattr(value, "__dict__")
            and type(value).__eq__ is object.__eq__
            and not (inspect.isclass(value) or inspect.ismodule(value)
                     or inspect.isroutine(value)))


def _walk_graphs(value, found: list, seen: set, depth: int = 0) -> None:
    from rdflib import Graph
    if depth > _MAX_DEPTH or id(value) in seen:
        return
    seen.add(id(value))
    if isinstance(value, Graph):
        found.append(value)
    elif isinstance(value, dict):
        for k, v in value.items():
            _walk_graphs(k, found, seen, depth + 1)
            _walk_graphs(v, found, seen, depth + 1)
    elif isinstance(value, (list, tuple, set, frozenset)):
        for v in value:
            _walk_graphs(v, found, seen, depth + 1)
    elif _structural(value):
        _walk_graphs(vars(value), found, seen, depth + 1)


def bnode_labels(*values) -> dict:
    """A label for each blank node of the graphs found in ``values``, read
    from its place in them, never from its identifier.

    Each side parses its own fixture, so the same blank node has a fresh
    identifier on each: a result that holds one — a dict keyed by it, a row
    that returns it — was either incomparable or, labels dropped, always
    equal.  Colour refinement (each node's label from its triples, the
    blank neighbours' labels included, until the partition stops growing)
    gives the same label on both sides to nodes in the same place.  Two
    nodes only an automorphism tells apart share a label, which is right:
    nothing the region could observe separates them either.
    """
    import hashlib
    from rdflib import BNode, ConjunctiveGraph
    graphs: list = []
    _walk_graphs(values, graphs, set())
    triples = []
    for g in graphs:
        quads = g.quads((None, None, None)) if isinstance(g, ConjunctiveGraph) \
            else g.triples((None, None, None))
        triples.extend(t[:3] for t in quads)
    nodes = {n for t in triples for n in t if isinstance(n, BNode)}
    colour = dict.fromkeys(nodes, "")
    classes = 1
    for _ in range(8):
        def key(n):
            return colour[n] if n in colour else n.n3()
        sig: dict = {b: [] for b in nodes}
        for s, p, o in triples:
            if s in sig:
                sig[s].append(("out", key(p), key(o)))
            if o in sig:
                sig[o].append(("in", key(s), key(p)))
        colour = {b: hashlib.sha1(repr((colour[b], sorted(sig[b])))
                                  .encode()).hexdigest()[:16]
                  for b in nodes}
        if len(set(colour.values())) == classes:
            break
        classes = len(set(colour.values()))
    return colour


def _key(k, bnodes):
    """A dict key, normalised and still hashable."""
    k = normalise(k, bnodes)
    try:
        hash(k)
    except TypeError:
        return repr(k)
    return k


def normalise(value, bnodes: dict | None = None, _depth: int = 0):
    """Make values comparable across the two runs (BNode ids differ).

    ``bnodes`` (:func:`bnode_labels`) names each blank node by its place in
    the graphs of its side; without it, or for a blank node in none of them,
    any two blank nodes are equal.
    """
    from rdflib import BNode, Graph
    if isinstance(value, Graph):
        from rdflib.compare import to_isomorphic
        return ("graph", to_isomorphic(value).graph_digest())
    if isinstance(value, BNode):
        if bnodes is None:
            return ("bnode",)
        return ("bnode", bnodes.get(value))
    if isinstance(value, dict):
        out = {_key(k, bnodes): normalise(v, bnodes, _depth)
               for k, v in value.items()}
        if len(out) < len(value):
            # two keys only their identifiers told apart: keep both entries
            return ("dict", sorted((repr(_key(k, bnodes)),
                                    repr(normalise(v, bnodes, _depth)))
                                   for k, v in value.items()))
        return out
    if isinstance(value, tuple):
        return tuple(normalise(v, bnodes, _depth) for v in value)
    if isinstance(value, list):
        return [normalise(v, bnodes, _depth) for v in value]
    if isinstance(value, set):
        return sorted(map(repr, (normalise(v, bnodes, _depth) for v in value)))
    if _structural(value) and _depth < _MAX_DEPTH:
        # depth counts objects only: attributes can point back up
        return ("object", type(value).__qualname__,
                normalise(dict(vars(value)), bnodes, _depth + 1))
    return value


def _compare_value(a, b, label: str, diffs: list[str],
                   ordered: bool = True, bnodes=(None, None)) -> None:
    """``bnodes``: the blank-node labels of each side (:func:`bnode_labels`)."""
    from rdflib import Graph
    if isinstance(a, Graph) and isinstance(b, Graph):
        if not graphs_isomorphic(a, b):
            diffs.append(f"{label}: graphs not isomorphic "
                         f"({len(a)} vs {len(b)} triples)")
        return
    try:
        a, b = materialise(a), materialise(b)
        if not ordered:
            equal = _unordered(a, bnodes[0]) == _unordered(b, bnodes[1])
        else:
            equal = normalise(a, bnodes[0]) == normalise(b, bnodes[1])
    except Exception as e:
        diffs.append(f"{label}: comparison error {e}")
        return
    if not equal:
        diffs.append(f"{label}: values differ ({a!r} vs {b!r})")


class Raised:
    """What a call raised, compared by exception type and message."""

    def __init__(self, exc: BaseException):
        self.type = type(exc).__name__
        self.message = str(exc)

    def __eq__(self, other):
        return (isinstance(other, Raised)
                and (self.type, self.message) == (other.type, other.message))

    def __repr__(self):
        return f"raised {self.type}({self.message!r})"


def _is_empty(value) -> bool:
    """Empty in the sense that matters: the region found nothing."""
    from rdflib import Graph
    if value is None or value is False:
        return True
    if isinstance(value, Graph):
        return len(value) == 0
    if isinstance(value, (list, tuple, set, frozenset, dict, str)):
        return len(value) == 0
    return False


def _state(value, depth: int = 0):
    """Everything a call can change in a value, graphs by digest — whatever
    the value's ``__eq__``: a stub whose ``__eq__`` looks at its URI only
    has still been written into if its graph grew."""
    import inspect
    from rdflib import ConjunctiveGraph, Graph
    if isinstance(value, ConjunctiveGraph):
        # rdflib.compare reads triples, a dataset yields quads; within one
        # side the terms are the same objects, so the quads themselves do
        return ("dataset", len(value), hash(frozenset(value.quads())))
    if isinstance(value, Graph):
        from rdflib.compare import to_isomorphic
        return ("graph", to_isomorphic(value).graph_digest())
    if depth > _MAX_DEPTH:
        return repr(value)
    if isinstance(value, dict):
        return sorted(((repr(k), _state(v, depth + 1))
                       for k, v in value.items()), key=lambda kv: kv[0])
    if isinstance(value, (list, tuple)):
        return [_state(v, depth + 1) for v in value]
    if isinstance(value, (set, frozenset)):
        return sorted(repr(_state(v, depth + 1)) for v in value)
    if hasattr(value, "__dict__") and not (
            inspect.isclass(value) or inspect.ismodule(value)
            or inspect.isroutine(value)):
        return (type(value).__qualname__, _state(dict(vars(value)), depth + 1))
    return repr(value)


def _fingerprint(values) -> list:
    """What the call can change in what it was given."""
    out = []
    for v in values:
        try:
            out.append(_state(v))
        except Exception:                         # noqa: BLE001 - opaque
            out.append(None)
    return out


def _outcome(fn, args, kwargs):
    """The call's return value, or a :class:`Raised` for an Exception."""
    try:
        return fn(*args, **kwargs)
    except Exception as e:                        # noqa: BLE001 - compared
        return Raised(e)


def run_pair(driver_file: str, entry: str | None = None,
             calls: list | None = None, fixture: str | None = None,
             ordered: bool | None = None, stdout_filter=None) -> dict:
    """Establish that ``original.py`` and ``translated.ldpy`` agree.

    ``entry``/``calls``   compare what a function returns and what it mutates
    ``fixture``           a Turtle file, parsed fresh for each side and passed
                          to ``entry`` as its single argument — the reading
                          oracle: same input graph, same values out
    ``stdout_filter``     a ``str -> str`` applied to BOTH sides' output
                          before comparing.  Printed output can carry things
                          that are not the program's meaning — a fresh
                          ``Graph()`` identifier, a wall-clock duration.  The
                          driver says explicitly what to drop, in the pair,
                          where a reader can see it; the harness keeps no
                          hidden list of exceptions.
    ``ordered``           whether the order of a sequence is part of the
                          region's meaning.  Defaults to True, and to False
                          for a fixture run: no RDF store promises an order,
                          so a region that wants one must sort or ``ORDER BY``
                          — and then the driver says ``ordered=True``.
    """
    ex_dir = Path(driver_file).resolve().parent
    if ordered is None:
        ordered = fixture is None
    verdict: dict = {"example": ex_dir.name, "equivalent": False,
                     "method": None, "diffs": [], "error": None}
    try:
        left, right = sides_from_env()
    except ValueError as e:
        verdict["error"] = str(e)
        _emit(verdict)
        return verdict
    verdict["sides"] = [left, right]
    if fixture is not None:
        if not entry:
            verdict["error"] = "fixture= needs entry= (the region to call)"
            _emit(verdict)
            return verdict
        path = ex_dir / fixture
        if calls is None:
            calls = [lambda: ((fixture_graph(path),), {})]
    try:
        ns_o, out_o = _exec_artefact(ex_dir / left, "__original__")
        ns_t, out_t = _exec_artefact(ex_dir / right, "__translated__")
    except Exception:
        verdict["error"] = traceback.format_exc(limit=8)
        _emit(verdict)
        return verdict

    diffs: list[str] = []
    observed = False
    shown = 0
    if entry:
        verdict["method"] = (f"fixture:{fixture} entry:{entry}"
                             if fixture else f"entry:{entry}")
        verdict["ordered"] = ordered
        fo, ft = ns_o.get(entry), ns_t.get(entry)
        if not callable(fo) or not callable(ft):
            verdict["error"] = f"entry {entry!r} not found in both modules"
            _emit(verdict)
            return verdict
        if not calls:
            verdict["error"] = "no fixtures: provide calls=[(args, kwargs), …]"
            _emit(verdict)
            return verdict
        for i, case in enumerate(calls):
            # a case is (args, kwargs) — or a callable returning that pair,
            # invoked once per side so mutable arguments (graphs!) stay fresh
            try:
                args_o, kw_o = case() if callable(case) else case
                args_t, kw_t = case() if callable(case) else case
                # A region whose whole effect is printing has nothing else to
                # compare: capture what each side writes while it runs.
                buf_o, buf_t = io.StringIO(), io.StringIO()
                given = list(args_o) + list(kw_o.values())
                before = _fingerprint(given)
                with contextlib.redirect_stdout(buf_o):
                    ro = _outcome(fo, args_o, kw_o)
                after = _fingerprint(given)
                with contextlib.redirect_stdout(buf_t):
                    rt = _outcome(ft, args_t, kw_t)
            except Exception:
                verdict["error"] = traceback.format_exc(limit=8)
                _emit(verdict)
                return verdict
            # a lazy result is read once, here: both the comparison and the
            # hollow-green screen below look at it
            try:
                ro, rt = materialise(ro), materialise(rt)
            except Exception as e:                # noqa: BLE001 - reported
                diffs.append(f"call[{i}].result: comparison error {e}")
                ro = rt = Raised(e)
            # blank nodes are named by their place in what each side holds
            # after the call: its arguments (mutated) and its result
            bnodes = (bnode_labels(ro, args_o, kw_o),
                      bnode_labels(rt, args_t, kw_t))
            if isinstance(ro, Raised) or isinstance(rt, Raised):
                # A raise is an outcome like a value: same exception type and
                # message on both sides, or a difference.  What the call
                # mutated before raising is still compared below.
                if ro != rt:
                    diffs.append(f"call[{i}]: outcome differs ({ro!r} vs {rt!r})")
                observed = True
            else:
                _compare_value(ro, rt, f"call[{i}].result", diffs, ordered,
                               bnodes)
            for j, (ao, at) in enumerate(zip(args_o, args_t)):
                _compare_value(ao, at, f"call[{i}].arg[{j}]", diffs, ordered,
                               bnodes)
            for k in kw_o:
                _compare_value(kw_o[k], kw_t.get(k), f"call[{i}].kwarg[{k}]",
                               diffs, ordered, bnodes)
            so, st_ = _filtered(buf_o.getvalue(), stdout_filter), \
                _filtered(buf_t.getvalue(), stdout_filter)
            if so != st_:
                diffs.append(f"call[{i}]: stdout differs "
                             f"({so[:120]!r} vs {st_[:120]!r})")
            if ro is not None or rt is not None or args_o or kw_o or so:
                observed = True
            # what the ORIGINAL demonstrated on this call: a value, a raise,
            # a change to what it was given, or output
            if (isinstance(ro, Raised) or not _is_empty(ro)
                    or before != after or so):
                shown += 1
        verdict["calls"] = len(calls)
        verdict["observed"] = observed
        verdict["hollow"] = shown == 0
        if not observed:
            # The call returned nothing, took nothing to mutate and printed
            # nothing: a green here says only "it did not crash".  A region
            # whose whole effect is a file write lands exactly here.
            diffs.append("nothing observable to compare: the entry point "
                         "returns None, takes no argument to mutate and "
                         "prints nothing")
        if _filtered(out_o, stdout_filter) != _filtered(out_t, stdout_filter):
            diffs.append("stdout differs at module level")
    else:
        verdict["method"] = "module-state"
        go, gt = _graphs(ns_o), _graphs(ns_t)
        if set(go) != set(gt):
            diffs.append(f"graph variables differ: {sorted(go)} vs {sorted(gt)}")
        for name in sorted(set(go) & set(gt)):
            _compare_value(go[name], gt[name], f"graph {name}", diffs)
        vo, vt = _values(ns_o), _values(ns_t)
        shared = sorted(set(vo) & set(vt))
        bnodes = (bnode_labels(go, vo), bnode_labels(gt, vt))
        for name in shared:
            _compare_value(vo[name], vt[name], f"value {name}", diffs, ordered,
                           bnodes)
        if _filtered(out_o, stdout_filter) != _filtered(out_t, stdout_filter):
            diffs.append("stdout differs")
        verdict["graphs_compared"] = sorted(set(go) & set(gt))
        verdict["values_compared"] = shared
        verdict["hollow"] = (all(len(g) == 0 for g in go.values())
                             and all(_is_empty(vo[n]) for n in shared)
                             and not _filtered(out_o, stdout_filter))
        # A name the original defines and the translation does not is never
        # compared.  Not a difference by itself — a Namespace replaced by a
        # @prefix is the point of ns_def_local — but a reviewer must see it,
        # since other modules of the repository may import that name.
        verdict["names_only_original"] = sorted(set(vo) - set(vt))
        if not (go or gt) and not shared and out_o == out_t == "":
            diffs.append("nothing observable to compare")
    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
    _emit(verdict)
    return verdict


def _emit(verdict: dict) -> None:
    if "sides" not in verdict:
        # a hand-written driver: credit only the sides it actually executed
        # (the default pair is what every driver was written to prove)
        left, right = sides_from_env()
        proved = (left, right) == DEFAULT_SIDES or (
            left in _EXECUTED and right in _EXECUTED)
        verdict["sides"] = [left, right] if proved else None
    print("RDFEVAL-VERDICT " + json.dumps(verdict), file=sys.stderr)
