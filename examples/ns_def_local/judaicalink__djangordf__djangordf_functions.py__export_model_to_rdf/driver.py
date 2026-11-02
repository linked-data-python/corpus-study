"""Validation driver for judaicalink__djangordf__djangordf_functions.py__export_model_to_rdf.

export_model_to_rdf(model, dump_name, namespace, output_dir) reads a Django
model, builds a graph and WRITES a Turtle file; it returns the file's path. So
everything the region shows is: the returned path, the file written in the
example directory (compared as an RDF document by the harness), the
`logger.warning` records of the unhandled field types, and -- through the
second phase below -- the TEXT of the Turtle file, which carries the prefix
table (`g.bind(model.__name__.lower(), ns)`) that a graph comparison does not
see.

Stand-ins. Django is not in the venv: `model` is an instance of `_Model`
(`__name__`, `.objects.all()`, `._meta.fields` -- the only parts the region
touches) holding rows with every branch of the type chain: int, bool (False,
which must not become an integer), float, datetime, str, None (skipped), and a
list (unhandled: warning, skipped). `context_shim.settings.BASE_DIR` is ".".

Time. `datetime.now()` is called twice (the dump timestamp and the file name);
the driver freezes `now()` for BOTH sides by replacing the `datetime` module in
sys.modules (each side is a fork of this process). The row values are
instances of the frozen class, so `isinstance(value, datetime)` holds on both.

Calls: default namespace + explicit output_dir; custom namespace; output_dir
omitted (settings.BASE_DIR); a model with no row (metadata only); a model whose
name has capitals and a pk that is not an int (string pk); and an unwritable
output_dir (the raise is compared like a value).
"""
import contextlib
import datetime as _real_datetime
import io
import os
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
os.chdir(HERE)


# -- a frozen clock, for both sides ---------------------------------------
class _FrozenDatetime(_real_datetime.datetime):
    @classmethod
    def now(cls, tz=None):
        return cls(2020, 2, 29, 12, 30, 45, 123456)


_fake = types.ModuleType("datetime")
_fake.__dict__.update({k: v for k, v in vars(_real_datetime).items()
                       if not k.startswith("__")})
_fake.datetime = _FrozenDatetime
sys.modules["datetime"] = _fake

from rdflib import Graph                         # noqa: E402

from rdfeval import harness                      # noqa: E402
from rdfeval.harness import run_pair             # noqa: E402

# -- a window on the local graph ---------------------------------------------
# The graph `g` never leaves the function, and Turtle is lossy for an
# ill-typed literal (rdflib writes "true"^^xsd:integer as a bare `true`, which
# reads back as a boolean): the written file cannot tell xsd:boolean from
# xsd:integer. So `Graph.serialize` is wrapped, for both sides, to print the
# graph's exact N-Triples (datatypes included) to stdout, which is compared.
_serialize = Graph.serialize


def _serialize_spy(self, *args, **kw):
    print("GRAPH-NT", sorted(_serialize(self, format="nt").splitlines()))
    return _serialize(self, *args, **kw)


Graph.serialize = _serialize_spy


# -- Django stand-ins -------------------------------------------------------
class _Field:
    def __init__(self, name):
        self.name = name


class _Manager:
    def __init__(self, rows):
        self.rows = rows

    def all(self):
        return list(self.rows)


class _Meta:
    def __init__(self, names):
        self.fields = [_Field(n) for n in names]


class _Row:
    def __init__(self, **kw):
        self.__dict__.update(kw)


class _Model:
    """Stands in for a Django model CLASS (compared by attributes)."""

    def __init__(self, name, names, rows):
        self.__name__ = name
        self._meta = _Meta(names)
        self.objects = _Manager(rows)


FIELDS = ["id", "title", "pages", "in_print", "price", "published", "notes", "tags"]


def book():
    when = _FrozenDatetime(2021, 5, 17, 8, 0, 0)
    return _Model("Book", FIELDS, [
        _Row(pk=1, id=1, title="Ana & co", pages=312, in_print=True, price=12.5,
             published=when, notes=None, tags=["a", "b"]),
        _Row(pk=2, id=2, title="", pages=0, in_print=False, price=0.0,
             published=when, notes="n", tags=[]),
        _Row(pk=3, id=3, title="Tres", pages=-7, in_print=True, price=1e-7,
             published=when, notes=None, tags=None),
    ])


def author():
    return _Model("AuthorProfile", ["id", "name"], [
        _Row(pk="k-9", id="k-9", name="Zoë"),
    ])


def empty():
    return _Model("Empty", FIELDS, [])


CALLS = [
    lambda: ((book(), "books"), {"output_dir": "."}),
    lambda: ((book(), "books_custom"),
             {"namespace": "http://example.org/custom#", "output_dir": "."}),
    lambda: ((book(), "books_default_dir"), {}),
    lambda: ((empty(), "nothing"), {"output_dir": "."}),
    lambda: ((author(), "authors"), {"output_dir": "."}),
    lambda: ((book(), "boom"), {"output_dir": "no-such-dir"}),
]

with contextlib.redirect_stderr(io.StringIO()):
    VERDICT = run_pair(__file__, entry='export_model_to_rdf', calls=CALLS)


# -- phase 2: the TEXT of the Turtle file (prefix table included) -----------
def _written_text(fn, model, *args, **kw):
    with contextlib.redirect_stdout(io.StringIO()):     # the spy's line
        path = fn(model, *args, **kw)
    try:
        return path, Path(path).read_text(encoding="utf-8")
    finally:
        try:
            Path(path).unlink()
        except OSError:
            pass


if VERDICT.get("error") is None:
    try:
        sys.modules.pop("context_shim", None)
        ns_o, _ = harness._exec_python(HERE / "original.py")
        sys.modules.pop("context_shim", None)
        ns_t, _ = harness._exec_ldpy(HERE / "translated.ldpy")
        cases = {
            "default ns": (book, ("books",), {"output_dir": "."}),
            "custom ns": (book, ("c",), {"namespace": "http://example.org/custom#",
                                         "output_dir": "."}),
            "capitalised model": (author, ("a",), {"output_dir": "."}),
            "no row": (empty, ("e",), {"output_dir": "."}),
        }
        for label, (make, args, kw) in cases.items():
            out_o = _written_text(ns_o["export_model_to_rdf"], make(), *args, **kw)
            out_t = _written_text(ns_t["export_model_to_rdf"], make(), *args, **kw)
            if out_o != out_t:
                VERDICT["diffs"].append(f"{label}: written Turtle text differs "
                                        f"({out_o!r} vs {out_t!r})")
            if "@prefix" not in out_o[1]:
                VERDICT["diffs"].append(f"{label}: original wrote no prefix?")
        VERDICT["text_compared"] = True
    except Exception as e:                        # noqa: BLE001 - reported
        VERDICT["error"] = f"text phase: {type(e).__name__}: {e}"
    VERDICT["equivalent"] = not VERDICT["diffs"] and VERDICT["error"] is None

harness._emit(VERDICT)
