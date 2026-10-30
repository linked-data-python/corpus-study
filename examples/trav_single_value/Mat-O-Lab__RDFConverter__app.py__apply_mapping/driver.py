"""Validation driver for Mat-O-Lab__RDFConverter__app.py__apply_mapping.

The region is a module-level statement block of `apply_mapping`, so the
oracle is module state: every graph (`data_graph`, `mapping_graph`,
`joined_graph`) and every other module-level value both sides define
(`tablegroup`, `column_maps`, `note_maps`, `for_row_to_set`, ...), plus
stdout (the region prints `column_map:` and `to set for row:`).

Its inputs are the locals restored at the top of both artefacts, between
`data_graph = Graph()` and `rows = [EX.row1]` (identical text on both
sides).  To run the region on more than that one input, the driver copies
the artefacts into a scratch directory per INPUT and replaces that block,
on both sides alike, by the input's two graphs; `rows` is then computed as
the origin repository computes it (app.py:1461,
`rows = list(data_graph[: RDF.type : CSVW.Row])`).  The region itself is
untouched.

For every input the driver also executes the two sides itself and compares
what run_pair does not see:
  * the outcome: a module-level raise is compared like a value (same type,
    same message) -- run_pair would only report it as an error;
  * the warnings each side emits (recorded, compared as a list);
  * the prefix bindings of `joined_graph`: every binding the original
    makes (`row<...>`) must be in the translation (extra ones tolerated).

The inputs, and what each one exercises:

  shipped            the block as shipped (one row, one matched lookup,
                     one column without propertyUrl, one note)
  two-tablegroups-ab / -ba
                     two csvw:TableGroup: next() takes the first the store
                     yields, the translation must take the same (`tablegroup`
                     is module state)
  no-tablegroup      none, with a csvw:Table and a node pointing at
                     csvw:TableGroup through another predicate:
                     StopIteration on both sides
  row-no-describes   the row has no csvw:describes (a neighbour that is not a
                     Row has one, the row has another predicate):
                     data_node is None, `None + "/"` raises TypeError
  two-describes-ab / -ba
                     the row describes two nodes: g.value takes the first
  lookups            two rows; per row the joined lookup
                     `next(joined_graph.objects(data_node, property), None)`
                     meets: two values (first taken), no value while a
                     NEIGHBOUR node has one (a widened subject would add a
                     triple), a falsy "" and a falsy 0 (skipped by
                     `if subject:`), a column with no propertyUrl (the
                     column itself is the property); column neighbours
                     (a csvw:Table, a node linked to csvw:Column by another
                     predicate), two notes.  No blank-node column: each side
                     parses its own graph, so a BNode key of `column_maps`
                     and its printed id differ between the sides whatever
                     the translation does (a harness limit, not a meaning)
  literal-propertyUrl
                     propertyUrl is a literal, not an IRI
  empty-mapping      the mapping graph is empty: nothing is added
"""
import contextlib
import io
import json
import shutil
import tempfile
import warnings
from pathlib import Path

from rdfeval.harness import ARTEFACTS, Raised, _emit, _exec_artefact, run_pair, sides_from_env

EX_DIR = Path(__file__).resolve().parent
BLOCK_START = "data_graph = Graph()\n"
BLOCK_END = "rows = [EX.row1]\n"

_PRE = """\
@prefix ex:   <http://example.org/> .
@prefix csvw: <http://www.w3.org/ns/csvw#> .
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
"""
_TG = "ex:tg a csvw:TableGroup .\n"
_COL1 = "ex:col1 a csvw:Column ; csvw:propertyUrl ex:propA .\n"
_ROW1 = "ex:row1 a csvw:Row ; csvw:describes ex:node1 .\n"
_MAP1 = _PRE + """
ex:col1 ex:hasType ex:SomeType .
ex:note1 ex:hasComment "hello" .
"""

INPUTS = {
    "two-tablegroups-ab": (_PRE + """
ex:tgA a csvw:TableGroup .
ex:tgB a csvw:TableGroup .
""" + _COL1 + _ROW1 + "ex:node1 ex:propA ex:objA .\n", _MAP1),
    "two-tablegroups-ba": (_PRE + """
ex:tgB a csvw:TableGroup .
ex:tgA a csvw:TableGroup .
""" + _COL1 + _ROW1 + "ex:node1 ex:propA ex:objA .\n", _MAP1),
    "no-tablegroup": (_PRE + """
ex:t a csvw:Table .
ex:u ex:seeAlso csvw:TableGroup .
""" + _COL1 + _ROW1 + "ex:node1 ex:propA ex:objA .\n", _MAP1),
    "row-no-describes": (_PRE + _TG + _COL1 + """
ex:row1 a csvw:Row ; ex:seeAlso ex:node8 .
ex:row9 csvw:describes ex:node9 .
ex:node8 ex:propA ex:objA .
ex:node9 ex:propA ex:objA .
""", _MAP1),
    "two-describes-ab": (_PRE + _TG + _COL1 + """
ex:row1 a csvw:Row ; csvw:describes ex:nodeA , ex:nodeB .
ex:nodeA ex:propA ex:objA .
ex:nodeB ex:propA ex:objB .
""", _MAP1),
    "two-describes-ba": (_PRE + _TG + _COL1 + """
ex:row1 a csvw:Row ; csvw:describes ex:nodeB , ex:nodeA .
ex:nodeA ex:propA ex:objA .
ex:nodeB ex:propA ex:objB .
""", _MAP1),
    "lookups": (_PRE + _TG + """
ex:col1 a csvw:Column ; csvw:propertyUrl ex:propA .
ex:col2 a csvw:Column ; csvw:propertyUrl ex:propB .
ex:col3 a csvw:Column ; csvw:propertyUrl ex:propC .
ex:col4 a csvw:Column ; csvw:propertyUrl ex:propD .
ex:col5 a csvw:Column .
ex:tbl a csvw:Table ; csvw:propertyUrl ex:propA .
ex:colX ex:seeAlso csvw:Column ; csvw:propertyUrl ex:propA .
ex:row1 a csvw:Row ; csvw:describes ex:node1 .
ex:row2 a csvw:Row ; csvw:describes ex:node2 .
ex:node1 ex:propA ex:objA1 , ex:objA2 ;
         ex:propC "" ;
         ex:propD 0 ;
         ex:col5 ex:objC5 .
ex:node2 ex:propA ex:objA3 ;
         ex:propB ex:objB2 .
ex:node9 ex:propB ex:objB9 .
""", _PRE + """
ex:col1 ex:hasType ex:SomeType .
ex:col2 ex:hasLabel "Foo" .
ex:col3 ex:hasType ex:TypeC .
ex:col4 ex:hasType ex:TypeD .
ex:col5 ex:hasUnit <http://example.org/units#metre> .
ex:colX ex:hasType ex:TypeX .
ex:tbl ex:hasType ex:TypeT .
ex:note1 ex:hasComment "hello" .
ex:note2 ex:hasComment "world" ; ex:hasType ex:Note .
"""),
    "literal-propertyUrl": (_PRE + _TG + """
ex:col1 a csvw:Column ; csvw:propertyUrl "http://example.org/propA" .
""" + _ROW1 + "ex:node1 ex:propA ex:objA .\n", _MAP1),
    "empty-mapping": (_PRE + _TG + _COL1 + _ROW1 + "ex:node1 ex:propA ex:objA .\n", ""),
}


def _block(data_ttl: str, mapping_ttl: str) -> str:
    return (f"data_graph = Graph().parse(data={data_ttl!r}, format='turtle')\n"
            f"mapping_graph = Graph().parse(data={mapping_ttl!r}, format='turtle')\n"
            "rows = list(data_graph[: RDF.type : CSVW.Row])\n")


def _variant_dir(root: Path, name: str, block: str) -> Path:
    d = root / name
    d.mkdir()
    for artefact in ARTEFACTS:
        src = EX_DIR / artefact
        if not src.exists():
            continue
        text = src.read_text()
        i = text.index(BLOCK_START)
        j = text.index(BLOCK_END, i) + len(BLOCK_END)
        assert text.count(BLOCK_START) == 1 and text.count(BLOCK_END) == 1, artefact
        (d / artefact).write_text(text[:i] + block + text[j:])
    return d


def _verdict_of(stderr_text: str) -> dict:
    for line in stderr_text.splitlines():
        if line.startswith("RDFEVAL-VERDICT "):
            return json.loads(line[len("RDFEVAL-VERDICT "):])
    raise RuntimeError("run_pair printed no verdict: " + stderr_text[-500:])


def _module_state(d: Path) -> dict:
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        run_pair(str(d / "driver.py"), entry=None, calls=None)
    return _verdict_of(buf.getvalue())


def _side(path: Path, name: str):
    """Outcome, warnings and joined_graph bindings of one side."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            ns, _ = _exec_artefact(path, name)
            outcome, jg = "ok", ns.get("joined_graph")
        except Exception as e:                     # noqa: BLE001 - compared
            outcome, jg = Raised(e), None
    seen = [(w.category.__name__, str(w.message)) for w in caught]
    bindings = set() if jg is None else {(p, str(n)) for p, n in jg.namespaces()}
    return outcome, seen, bindings


def _scenario(d: Path) -> dict:
    left, right = sides_from_env()
    oo, wo, bo = _side(d / left, "__original__")
    ot, wt, bt = _side(d / right, "__translated__")
    diffs = []
    if oo != ot:
        diffs.append(f"outcome differs ({oo!r} vs {ot!r})")
    if wo != wt:
        diffs.append(f"warnings differ ({wo!r} vs {wt!r})")
    missing = sorted(b for b in bo - bt if b[0].startswith("row"))
    if missing:
        diffs.append(f"joined_graph bindings of the original missing: {missing}")
    verdict = {"equivalent": not diffs, "diffs": diffs, "error": None,
               "sides": [left, right], "outcome": repr(oo)}
    if oo == ot == "ok":
        state = _module_state(d)
        verdict["equivalent"] = verdict["equivalent"] and state["equivalent"]
        verdict["diffs"] += state["diffs"]
        verdict["error"] = state["error"]
    return verdict


verdicts = {"shipped": _scenario(EX_DIR)}
with tempfile.TemporaryDirectory() as tmp:
    for name, (data_ttl, mapping_ttl) in INPUTS.items():
        d = _variant_dir(Path(tmp), name, _block(data_ttl, mapping_ttl))
        verdicts[name] = _scenario(d)

first = verdicts["shipped"]
VERDICT = {
    "example": EX_DIR.name,
    "equivalent": all(v["equivalent"] for v in verdicts.values()),
    "method": f"module-state x {len(verdicts)} inputs",
    "diffs": [f"[{n}] {d}" for n, v in verdicts.items() for d in v["diffs"]],
    "error": "; ".join(f"[{n}] {v['error']}" for n, v in verdicts.items() if v["error"]) or None,
    "sides": first["sides"],
    "scenarios": {n: v["outcome"] for n, v in verdicts.items()},
}
_emit(VERDICT)
