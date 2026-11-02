"""Execution/comparison helpers used by example validation drivers.

A driver calls :func:`run_pair`, which

  1. executes ``original.py`` and ``translated.ldpy`` (through the ldpy
     transpiler), each in a process of its own forked from the driver, so
     that nothing one side leaves behind — a patched shim, a cache, an
     imported submodule — is seen by the other; each side reduces what it
     observed to canonical data (see "what one side does, observed"
     below), which the driver compares;
  2. either compares *module state* — every rdflib Graph in the globals,
     paired by variable name, PLUS every other module-level value both
     modules define (without which a region that only reads a graph gets a
     hollow green: its graphs are equal because nothing touched them) —
     or — when ``entry`` names a function — calls it with each fixture in
     ``calls`` and compares the results;
  3. besides values and mutations, it compares what each side writes to
     stdout and stderr, the region's own log records, and the files it
     writes in the example directory;
  4. graph comparison is rdflib graph isomorphism (``rdflib.compare``),
     never raw serialisation — a dataset graph by graph; other values are
     normalised
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

import atexit
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import traceback
from pathlib import Path


DEFAULT_SIDES = ("original.py", "translated.ldpy")
SIDES_ENV = "RDFEVAL_SIDES"
ARTEFACTS = ("original.py", "translated.ldpy", "optimized.py", "optimized.ldpy",
             "optimized_header.py", "optimized_header.ldpy")

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
    # a subclass is rebuilt as its base: `type(value)(gen)` fails on a
    # tuple whose __new__ wants more (ldpy's Row, a namedtuple), and a row
    # nested in a dict or a list never reached the comparison
    if isinstance(value, tuple):
        return tuple(materialise(v) for v in value)
    if isinstance(value, list):
        return [materialise(v) for v in value]
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


def dataset_key(ds) -> tuple:
    """A dataset compared graph by graph: each named graph by its name (a
    blank node name by nothing) and its isomorphism digest.
    ``rdflib.compare`` reads triples and a dataset yields quads, so a
    dataset could not be compared at all."""
    from rdflib import BNode, Graph
    from rdflib.compare import to_isomorphic
    parts = []
    for ctx in ds.contexts():
        g = Graph()
        for triple in ctx.triples((None, None, None)):
            g.add(triple)
        name = "bnode" if isinstance(ctx.identifier, BNode) \
            else str(ctx.identifier)
        parts.append((name, to_isomorphic(g).graph_digest()))
    return ("dataset", tuple(sorted(parts)))


def graphs_isomorphic(g1, g2) -> bool:
    from rdflib import ConjunctiveGraph
    from rdflib.compare import to_isomorphic
    if isinstance(g1, ConjunctiveGraph) or isinstance(g2, ConjunctiveGraph):
        return (isinstance(g1, ConjunctiveGraph)
                and isinstance(g2, ConjunctiveGraph)
                and dataset_key(g1) == dataset_key(g2))
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
    import types
    if isinstance(value, types.SimpleNamespace):
        return True                     # its __eq__ is exactly that
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


def bindings_lost(original, translated) -> list[tuple[str, str]]:
    """The prefix bindings the original's graph carries and the
    translation's does not, rdflib's own defaults left out.

    The study's rule (design record ldpy/027): equivalence covers the
    triples AND the bindings the original poses; a binding the translation
    adds is tolerated.  ``@graph g`` binds the block's prefixes on ``g``,
    and rdflib's ``bind`` moves a namespace to the new prefix: a repository
    that bound ``xs:`` serialises ``xsd:`` after translation, and no
    isomorphism sees it."""
    defaults = set(type(original)().namespaces())
    posed = set(original.namespaces()) - defaults
    kept = set(translated.namespaces())
    return sorted((p, str(n)) for p, n in posed - kept)


def normalise(value, bnodes: dict | None = None, _depth: int = 0):
    """Make values comparable across the two runs (BNode ids differ).

    ``bnodes`` (:func:`bnode_labels`) names each blank node by its place in
    the graphs of its side; without it, or for a blank node in none of them,
    any two blank nodes are equal.
    """
    from rdflib import BNode, ConjunctiveGraph, Graph
    if isinstance(value, ConjunctiveGraph):
        return dataset_key(value)
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
        lost = bindings_lost(a, b)
        if lost:
            diffs.append(f"{label}: prefix bindings of the original lost "
                         f"({', '.join(f'{p}: <{n}>' for p, n in lost)})")
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


# --- what one side does, observed --------------------------------------------
#
# Each side runs in a process of its own, forked from the driver (record
# corpus/403, défaut 3): run one after the other in a single process, the
# second side saw what the first had left — a shim it had patched, a cache,
# a submodule it had imported. A value cannot cross a process boundary as
# itself, so each side reduces what it observed to a CANONICAL form, plain
# data the driver compares: a graph by its isomorphism digest, a blank node
# by its place, an object compared by identity by the role it plays — the
# argument, the driver global, the shim attribute it IS — and an object of
# the region's own module by its attributes.

ISOLATE_ENV = "RDFEVAL_ISOLATE"
_SIDE_MODULES = ("__original__", "__translated__")
_RDF_SUFFIXES = {".ttl": "turtle", ".nt": "nt", ".n3": "n3", ".rdf": "xml",
                 ".owl": "xml", ".xml": "xml", ".jsonld": "json-ld",
                 ".trig": "trig", ".nq": "nquads"}


def _refs(roots: dict) -> dict[int, str]:
    """``id(obj) -> path`` for every object reachable from ``roots``: what a
    value compared by identity can be named by, the same way on both
    sides."""
    import inspect
    out: dict[int, str] = {}

    def walk(value, path, depth):
        if depth > 3 or id(value) in out or isinstance(
                value, (str, bytes, int, float, bool, type(None))):
            return
        if inspect.ismodule(value):
            return
        out[id(value)] = path
        if isinstance(value, dict):
            for k, v in list(value.items())[:200]:
                walk(v, f"{path}[{k!r}]", depth + 1)
        elif isinstance(value, (list, tuple)):
            for i, v in enumerate(value[:200]):
                walk(v, f"{path}[{i}]", depth + 1)
        elif _structural(value):
            for k, v in list(vars(value).items())[:200]:
                walk(v, f"{path}.{k}", depth + 1)

    for name, value in roots.items():
        walk(value, name, 0)
    return out


def _plain(value) -> bool:
    from rdflib.term import Node
    return value is None or isinstance(value, (str, bytes, bool, int, float,
                                               complex, Node, Raised))


def _deidentify(value, refs: dict, depth: int = 0):
    """Replace what only identity tells apart by its role (:func:`_refs`).

    Done before :func:`normalise`, which sorts sets by ``repr`` — and the
    repr of an identity object carries its address."""
    import inspect
    if _plain(value) or depth > _MAX_DEPTH + 2:
        return value
    from rdflib import Graph
    if isinstance(value, Graph):
        return value
    if isinstance(value, dict):
        return {(_deidentify(k, refs, depth + 1) if not _plain(k) else k):
                _deidentify(v, refs, depth + 1) for k, v in value.items()}
    if isinstance(value, tuple):
        return tuple(_deidentify(v, refs, depth + 1) for v in value)
    if isinstance(value, list):
        return [_deidentify(v, refs, depth + 1) for v in value]
    if isinstance(value, (set, frozenset)):
        return {_deidentify(v, refs, depth + 1) for v in value}
    if inspect.ismodule(value):
        return ("module", value.__name__)
    if inspect.isclass(value) or inspect.isroutine(value):
        if id(value) in refs:
            return ("ref", refs[id(value)])
        return ("callable", getattr(value, "__qualname__", repr(value)))
    if _structural(value):
        return value                    # normalise compares its attributes
    if type(value).__eq__ is object.__eq__:
        return ("ref", refs[id(value)]) if id(value) in refs else \
            ("opaque", type(value).__qualname__)
    return value                        # its own __eq__: see _portable


def _portable(value, depth: int = 0):
    """``value`` as data the driver process can receive and compare.

    An object with its own ``__eq__`` travels as itself when its class can
    be found again on the other side; a class of the region's own module
    cannot (each side has its module), so it travels by its attributes."""
    import pickle
    from rdflib import Graph
    if isinstance(value, float) and value != value:
        return ("nan",)                 # nan != nan: equal only by identity
    if _plain(value) or depth > _MAX_DEPTH + 2:
        return value
    if isinstance(value, Graph):
        return _canon_graph(value)[:3]
    if isinstance(value, dict):
        return {_portable(k, depth + 1): _portable(v, depth + 1)
                for k, v in value.items()}
    if isinstance(value, tuple):
        return tuple(_portable(v, depth + 1) for v in value)
    if isinstance(value, list):
        return [_portable(v, depth + 1) for v in value]
    if isinstance(value, (set, frozenset)):
        return frozenset(_portable(v, depth + 1) for v in value)
    if type(value).__module__ not in _SIDE_MODULES:
        try:
            pickle.loads(pickle.dumps(value))
            return value
        except Exception:                         # noqa: BLE001 - fallback
            pass
    if hasattr(value, "__dict__"):
        return ("object", type(value).__qualname__,
                _portable(normalise(dict(vars(value))), depth + 1))
    return ("repr", type(value).__qualname__, repr(value))


def _canon_graph(g) -> tuple:
    """A graph as compared: its digest, and the prefix bindings it carries
    (record ldpy/027: a binding of the original lost is a difference)."""
    from rdflib import ConjunctiveGraph
    from rdflib.compare import to_isomorphic
    key = dataset_key(g) if isinstance(g, ConjunctiveGraph) else \
        ("graph", to_isomorphic(g).graph_digest())
    return ("rdf-graph", key, len(g),
            frozenset((p, str(n)) for p, n in g.namespaces()),
            type(g).__name__)


def _canon(value, ordered: bool, bnodes, refs: dict):
    """What :func:`_compare_value` compares, as plain data."""
    from rdflib import Graph
    if isinstance(value, Graph):
        return _canon_graph(value)
    if isinstance(value, Raised):
        return value
    try:
        value = _deidentify(materialise(value), refs)
        value = _unordered(value, bnodes) if not ordered else \
            normalise(value, bnodes)
        return _portable(value)
    except Exception as e:                        # noqa: BLE001 - reported
        return ("comparison-error", f"{type(e).__name__}: {e}")


class _LogRecords:
    """Records the region itself logged — its own files, not a library's."""

    def __init__(self, ex_dir: Path):
        import logging
        self.ex_dir = ex_dir
        self.records: list[tuple[str, str, str]] = []
        outer = self

        class Handler(logging.Handler):
            def emit(self, record):
                if Path(record.pathname).parent == outer.ex_dir:
                    name = record.name
                    for side in _SIDE_MODULES:
                        name = name.replace(side, "__region__")
                    outer.records.append((record.levelname, name,
                                          record.getMessage()))
        self.handler = Handler(logging.DEBUG)


def _files(ex_dir: Path) -> dict[str, tuple]:
    out = {}
    for p in ex_dir.rglob("*"):
        if "__pycache__" in p.parts or not p.is_file():
            continue
        st = p.stat()
        out[str(p.relative_to(ex_dir))] = (st.st_mtime_ns, st.st_size)
    return out


def _file_content(path: Path, stdout_filter):
    """A written file as compared: an RDF document by its graph, a text by
    its (filtered) text, anything else by its bytes."""
    data = path.read_bytes()
    fmt = _RDF_SUFFIXES.get(path.suffix.lower())
    if fmt:
        try:
            from rdflib import Graph
            return _canon_graph(Graph().parse(data=data, format=fmt))[:3]
        except Exception:                         # noqa: BLE001 - as text
            pass
    try:
        return ("text", _filtered(data.decode("utf-8"), stdout_filter))
    except UnicodeDecodeError:
        return ("bytes", data)


@contextlib.contextmanager
def _observed(ex_dir: Path, stdout_filter):
    """Run a block and collect what it shows besides its value: stdout,
    stderr, the region's log records, the files it writes in the example
    directory — which are then removed or restored, so that nothing of one
    side is left for the other."""
    import logging
    import warnings
    seen: dict = {}
    before = _files(ex_dir)
    backup = {rel: (ex_dir / rel).read_bytes() for rel in before}
    out, err = io.StringIO(), io.StringIO()
    logs = _LogRecords(ex_dir)
    root = logging.getLogger()
    level = root.level
    root.addHandler(logs.handler)
    root.setLevel(logging.DEBUG)
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), \
                warnings.catch_warnings():
            warnings.simplefilter("ignore")
            yield seen
    finally:
        root.removeHandler(logs.handler)
        root.setLevel(level)
        after = _files(ex_dir)
        written = {}
        for rel, sig in after.items():
            if before.get(rel) != sig:
                written[rel] = _file_content(ex_dir / rel, stdout_filter)
                if rel in backup:
                    (ex_dir / rel).write_bytes(backup[rel])
                else:
                    (ex_dir / rel).unlink()
        # log records as a multiset: a region that logs once per solution
        # logs in the order of the store, which no store promises
        seen.update(stdout=_filtered(out.getvalue(), stdout_filter),
                    stderr=_filtered(err.getvalue(), stdout_filter),
                    logs=sorted((lv, n, _filtered(m, stdout_filter))
                                for lv, n, m in logs.records),
                    files=written)


def _side(ex_dir: Path, artefact: str, name: str, entry: str | None,
          calls: list | None, ordered: bool, stdout_filter) -> dict:
    """Run one artefact and return, canonical, all it showed."""
    driver = sys.modules.get("__main__")
    driver_globals = {k: v for k, v in vars(driver).items()
                      if not k.startswith("__")} if driver else {}
    side: dict = {}
    with _observed(ex_dir, stdout_filter) as module_seen:
        ns, out = _exec_artefact(ex_dir / artefact, name)
    module_seen["stdout"] = _filtered(out, stdout_filter)
    side["module"] = module_seen
    if entry:
        fn = ns.get(entry)
        if not callable(fn):
            side["missing_entry"] = True
            return side
        results = []
        for case in calls:
            args, kw = case() if callable(case) else case
            refs = _refs({"driver": driver_globals, "arg": list(args),
                          "kwarg": dict(kw), "module": {
                              k: v for k, v in ns.items()
                              if not k.startswith("__")}})
            given = list(args) + list(kw.values())
            before = _fingerprint(given)
            with _observed(ex_dir, stdout_filter) as seen:
                r = _outcome(fn, args, kw)
            after = _fingerprint(given)
            try:
                r = materialise(r)
            except Exception as e:                # noqa: BLE001 - reported
                r = Raised(e)
            bnodes = bnode_labels(r, args, kw)
            results.append({
                "result": _canon(r, ordered, bnodes, refs),
                "raised": isinstance(r, Raised),
                "empty": not isinstance(r, Raised) and _is_empty(r),
                "none": r is None,
                "args": [_canon(a, ordered, bnodes, refs) for a in args],
                "kwargs": {k: _canon(v, ordered, bnodes, refs)
                           for k, v in kw.items()},
                "inputs": bool(args or kw),
                "mutated": before != after,
                **seen,
            })
        side["calls"] = results
    else:
        refs = _refs({"driver": driver_globals})
        graphs = _graphs(ns)
        values = _values(ns)
        bnodes = bnode_labels(graphs, values)
        side["graphs"] = {k: _canon_graph(g) for k, g in graphs.items()}
        side["values"] = {k: _canon(v, ordered, bnodes, refs)
                          for k, v in values.items()}
        side["graphs_empty"] = all(len(g) == 0 for g in graphs.values())
        side["values_empty"] = {k: _is_empty(v) for k, v in values.items()}
    return side


def _in_child(fn, *args):
    """``fn(*args)`` in a forked process; its canonical result comes back
    through a pipe. A side that hangs ends itself before the driver's
    timeout."""
    import pickle
    import signal
    sys.stdout.flush()
    sys.stderr.flush()
    r, w = os.pipe()
    pid = os.fork()
    if pid == 0:                                  # pragma: no cover - child
        os.close(r)
        signal.alarm(115)
        try:
            data = pickle.dumps(("ok", fn(*args)))
        except BaseException:                     # noqa: BLE001 - reported
            data = pickle.dumps(("error", traceback.format_exc(limit=8)))
        with os.fdopen(w, "wb") as f:
            f.write(data)
        os._exit(0)
    os.close(w)
    with os.fdopen(r, "rb") as f:
        data = f.read()
    os.waitpid(pid, 0)
    if not data:
        return ("error", "the side's process died without a result")
    return pickle.loads(data)


def _in_process(fn, *args):
    try:
        return ("ok", fn(*args))
    except Exception:                             # noqa: BLE001 - reported
        return ("error", traceback.format_exc(limit=8))


def _compare_canon(a, b, label: str, diffs: list[str]) -> None:
    """Two canonical values (:func:`_canon`), the original's first."""
    if isinstance(a, tuple) and a[:1] == ("rdf-graph",) and \
            isinstance(b, tuple) and b[:1] == ("rdf-graph",):
        if a[1] != b[1]:
            diffs.append(f"{label}: graphs not isomorphic "
                         f"({a[2]} vs {b[2]} triples)")
        from rdflib import Graph
        defaults = set((p, str(n)) for p, n in Graph().namespaces())
        lost = sorted((a[3] - defaults) - b[3])
        if lost:
            diffs.append(f"{label}: prefix bindings of the original lost "
                         f"({', '.join(f'{p}: <{n}>' for p, n in lost)})")
        return
    for v in (a, b):
        if isinstance(v, tuple) and v[:1] == ("comparison-error",):
            diffs.append(f"{label}: comparison error {v[1]}")
            return
    try:
        equal = a == b
    except Exception as e:                        # noqa: BLE001 - reported
        diffs.append(f"{label}: comparison error {e}")
        return
    if not equal:
        diffs.append(f"{label}: values differ ({a!r} vs {b!r})")


def _compare_seen(o: dict, t: dict, label: str, diffs: list[str]) -> None:
    """What the two sides printed, logged and wrote."""
    for key, what in (("stdout", "stdout"), ("stderr", "stderr"),
                      ("logs", "log records"), ("files", "files written")):
        vo, vt = o.get(key), t.get(key)
        if vo == vt:
            continue
        if isinstance(vo, list) and isinstance(vt, list):
            # the first record that differs, not a prefix both share
            i = next((i for i, (x, y) in enumerate(zip(vo, vt)) if x != y),
                     min(len(vo), len(vt)))
            vo, vt = vo[i:i + 1] or "<end>", vt[i:i + 1] or "<end>"
            what = f"{what} (from #{i})"
        a, b = repr(vo)[:200], repr(vt)[:200]
        diffs.append(f"{label}{what} differ{'s' if key[-1] != 's' else ''}"
                     f" ({a} vs {b})")


def run_pair(driver_file: str, entry: str | None = None,
             calls: list | None = None, fixture: str | None = None,
             ordered: bool | None = None, stdout_filter=None,
             isolate: bool | None = None) -> dict:
    """Establish that ``original.py`` and ``translated.ldpy`` agree.

    ``entry``/``calls``   compare what a function returns and what it mutates
    ``fixture``           a Turtle file, parsed fresh for each side and passed
                          to ``entry`` as its single argument — the reading
                          oracle: same input graph, same values out
    ``stdout_filter``     a ``str -> str`` applied to BOTH sides' output —
                          stdout, stderr, log messages, written text files —
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
    ``isolate``           each side in a process of its own (the default;
                          ``RDFEVAL_ISOLATE=0`` turns it off for debugging).

    Besides values and mutations, each call is compared on what it writes to
    stdout and stderr, what the region logs, and the files it writes in the
    example directory.  A raise is an outcome like a value: same exception
    type and message on both sides, or a difference.
    """
    ex_dir = Path(driver_file).resolve().parent
    if ordered is None:
        ordered = fixture is None
    if isolate is None:
        isolate = os.environ.get(ISOLATE_ENV, "1") != "0"
    # Every module compiled from source, by both sides: a set literal of
    # constants is compiled to a frozenset constant, and the set it builds
    # iterates in one order when just compiled and in another when its
    # .pyc is loaded — same hash seed, other insertion history.  The first
    # side compiled a shim and wrote its .pyc, the second loaded it, and a
    # loop over the set ended on different items (record corpus/403).  An
    # empty cache that nothing is written to leaves no .pyc to load.
    if sys.pycache_prefix is None:
        sys.pycache_prefix = tempfile.mkdtemp(prefix="rdfeval-pyc-")
        atexit.register(shutil.rmtree, sys.pycache_prefix, True)
    sys.dont_write_bytecode = True
    verdict: dict = {"example": ex_dir.name, "equivalent": False,
                     "method": None, "diffs": [], "error": None,
                     "isolated": isolate}
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
    if entry and not calls:
        verdict["error"] = "no fixtures: provide calls=[(args, kwargs), …]"
        _emit(verdict)
        return verdict

    run = _in_child if isolate else _in_process
    status_o, so = run(_side, ex_dir, left, "__original__", entry, calls,
                       ordered, stdout_filter)
    status_t, st = run(_side, ex_dir, right, "__translated__", entry, calls,
                       ordered, stdout_filter)
    for status, payload in ((status_o, so), (status_t, st)):
        if status != "ok":
            verdict["error"] = payload
            _emit(verdict)
            return verdict

    diffs: list[str] = []
    _compare_seen(so["module"], st["module"], "module-level ", diffs)
    if entry:
        verdict["method"] = (f"fixture:{fixture} entry:{entry}"
                             if fixture else f"entry:{entry}")
        verdict["ordered"] = ordered
        if so.get("missing_entry") or st.get("missing_entry"):
            verdict["error"] = f"entry {entry!r} not found in both modules"
            _emit(verdict)
            return verdict
        observed = False
        shown = 0
        for i, (co, ct) in enumerate(zip(so["calls"], st["calls"])):
            if co["raised"] or ct["raised"]:
                if co["result"] != ct["result"]:
                    diffs.append(f"call[{i}]: outcome differs "
                                 f"({co['result']!r} vs {ct['result']!r})")
                observed = True
            else:
                _compare_canon(co["result"], ct["result"],
                               f"call[{i}].result", diffs)
            for j, (ao, at) in enumerate(zip(co["args"], ct["args"])):
                _compare_canon(ao, at, f"call[{i}].arg[{j}]", diffs)
            for k, vo in co["kwargs"].items():
                _compare_canon(vo, ct["kwargs"].get(k),
                               f"call[{i}].kwarg[{k}]", diffs)
            _compare_seen(co, ct, f"call[{i}]: ", diffs)
            said = co["stdout"] or co["stderr"] or co["logs"] or co["files"]
            if not co["none"] or not ct["none"] or co["inputs"] or said:
                observed = True
            # what the ORIGINAL demonstrated on this call: a value, a raise,
            # a change to what it was given, or output of any kind
            if co["raised"] or not co["empty"] or co["mutated"] or said:
                shown += 1
        verdict["calls"] = len(so["calls"])
        verdict["observed"] = observed
        verdict["hollow"] = shown == 0
        if not observed:
            # The call returned nothing, took nothing to mutate, printed,
            # logged and wrote nothing: a green here says only "it did not
            # crash".
            diffs.append("nothing observable to compare: the entry point "
                         "returns None, takes no argument to mutate, prints, "
                         "logs and writes nothing")
    else:
        verdict["method"] = "module-state"
        go, gt = so["graphs"], st["graphs"]
        if set(go) != set(gt):
            diffs.append(f"graph variables differ: {sorted(go)} vs {sorted(gt)}")
        for name in sorted(set(go) & set(gt)):
            _compare_canon(go[name], gt[name], f"graph {name}", diffs)
        vo, vt = so["values"], st["values"]
        shared = sorted(set(vo) & set(vt))
        for name in shared:
            _compare_canon(vo[name], vt[name], f"value {name}", diffs)
        verdict["graphs_compared"] = sorted(set(go) & set(gt))
        verdict["values_compared"] = shared
        m = so["module"]
        verdict["hollow"] = (so["graphs_empty"]
                             and all(so["values_empty"][n] for n in shared)
                             and not (m["stdout"] or m["stderr"] or m["logs"]
                                      or m["files"]))
        # A name the original defines and the translation does not is never
        # compared.  Not a difference by itself — a Namespace replaced by a
        # @prefix is the point of ns_def_local — but a reviewer must see it,
        # since other modules of the repository may import that name.
        verdict["names_only_original"] = sorted(set(vo) - set(vt))
        if not (go or gt) and not shared and not any(
                m[k] for k in ("stdout", "stderr", "logs", "files")):
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
