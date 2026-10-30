"""Validation driver for BrickSchema__Brick__generate_brick.py__add_definitions.

Establishes semantic equivalence of original.py and translated.ldpy by
isomorphism of the graph add_definitions() mutates -- entry=/calls= run the
function on a fresh graph for each side and compare the resulting graphs,
the outcome (a raise is compared by type and message) and stdout.

The function does two things: (1) reads ./bricksrc/definitions.csv (relative
to the current directory) and adds skos:definition/rdfs:seeAlso triples per
row; (2) walks every `?param rdfs:subClassOf* brick:Limit` already in the
graph and adds a generated skos:definition, UNLESS `param` already has a
brick:aliasOf -- the one-step read this stratum targets -- then logs a
warning when the inferred setpoint is not a brick:Class.

What the region logs is part of what it decides (the inferred setpoint per
param, the warning per missing class): a handler on the root logger PRINTS
each record (level and message, not the logger name, which is the module
name and differs by construction), so the harness compares it as stdout,
call by call.  The same handler serves both sides.

call_with_hierarchy() pre-populates the graph passed in with:
  - brick:Min_Limit, brick:Max_Limit rdfs:subClassOf brick:Limit, neither
    aliased -- the zero-solution case for `m{ {param} brick:aliasOf ?o }`,
    so both get a generated skos:definition;
  - brick:Alias_Limit rdfs:subClassOf brick:Limit AND brick:aliasOf
    brick:Min_Limit -- the one-solution case: the read must find it and the
    function must skip adding a definition for it;
  - brick:Setpoint rdfs:subClassOf brick:Class, neighbouring data that must
    NOT satisfy `?param rdfs:subClassOf* brick:Limit` (it isn't a Limit),
    exercised only through the class_exists lookup.
definitions.csv covers a definition-only row, a definition+seeAlso row, and
a row with an empty definition that must add nothing.

Added on repair (2026-10-30):
  - call_with_brick_shapes(): the shapes the repository's own generator
    writes (generate_brick.py:340-353, bricksrc/parameter.py:823-900) --
    limits two and three levels below brick:Limit, one of them under two
    parents (Max_Limit and Speed_Setpoint_Limit: the `*` path yields it
    once), an alias at depth with its owl:equivalentClass pair and copied
    subClassOf, a class linked to brick:Limit only through skos:broader
    (not a param), a param with a neighbour predicate owl:sameAs (not an
    alias), and a brick:Class hierarchy holding some inferred setpoints
    and not others (the warning differs per param);
  - call_without_setpoint_class(): the first hierarchy without
    `brick:Setpoint rdfs:subClassOf brick:Class`, so brick:Limit itself --
    reached only by the zero-length step of `*` -- logs its own warning
    (`*` read as `+` would drop it);
  - CSV_CASES: the CSV is a fixed file read by a relative path, so each case
    writes its own bricksrc/definitions.csv in a temporary directory and
    the call runs there (same directory for both sides): seeAlso without
    definition, a two-column row, a repeated term, a quoted comma; a row
    with more fields than the header after a good one (ValueError, and the
    good row's triples stay in the graph on both sides); a header alone.
The graphs bind their prefixes, as the repository's G does
(generate_brick.py:74, bind_prefixes).
"""
import logging
import os
import shutil
import tempfile
from pathlib import Path

from rdflib import Graph

from rdfeval.harness import run_pair

EX_DIR = Path(__file__).resolve().parent
BRICK = "https://brickschema.org/schema/Brick#"
RDFS = "http://www.w3.org/2000/01/rdf-schema#"

HIERARCHY_TTL = f"""
@prefix brick: <{BRICK}> .
@prefix rdfs: <{RDFS}> .

brick:Min_Limit rdfs:subClassOf brick:Limit .
brick:Max_Limit rdfs:subClassOf brick:Limit .
brick:Alias_Limit rdfs:subClassOf brick:Limit .
brick:Alias_Limit brick:aliasOf brick:Min_Limit .
brick:Setpoint rdfs:subClassOf brick:Class .
"""

BRICK_SHAPES_TTL = f"""
@prefix brick: <{BRICK}> .
@prefix rdfs: <{RDFS}> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .

brick:Limit rdfs:subClassOf brick:Parameter .
brick:Max_Limit rdfs:subClassOf brick:Limit .
brick:Speed_Setpoint_Limit rdfs:subClassOf brick:Limit .
brick:Max_Speed_Setpoint_Limit rdfs:subClassOf brick:Speed_Setpoint_Limit ,
                                               brick:Max_Limit .
brick:Air_Temperature_Setpoint_Limit rdfs:subClassOf brick:Limit .
brick:Supply_Air_Temperature_Setpoint_Limit
    rdfs:subClassOf brick:Air_Temperature_Setpoint_Limit ;
    owl:equivalentClass brick:Discharge_Air_Temperature_Setpoint_Limit .
brick:Discharge_Air_Temperature_Setpoint_Limit
    rdfs:subClassOf brick:Air_Temperature_Setpoint_Limit ;
    owl:equivalentClass brick:Supply_Air_Temperature_Setpoint_Limit ;
    brick:aliasOf brick:Supply_Air_Temperature_Setpoint_Limit .
brick:Min_Supply_Air_Temperature_Setpoint_Limit
    rdfs:subClassOf brick:Supply_Air_Temperature_Setpoint_Limit ;
    owl:sameAs brick:Something_Else .
brick:Broader_Only_Limit skos:broader brick:Limit .

brick:Setpoint rdfs:subClassOf brick:Point .
brick:Point rdfs:subClassOf brick:Class .
brick:Speed_Setpoint rdfs:subClassOf brick:Setpoint .
brick:Air_Temperature_Setpoint rdfs:subClassOf brick:Setpoint .
"""

CSV_CASES = {
    "rows": (
        "Term,Definition,See Also\n"
        f"{BRICK}Only_SeeAlso,,https://example.org/only\n"
        f"{BRICK}Two_Columns,Two columns only\n"
        f"{BRICK}Repeated,First definition,\n"
        f"{BRICK}Repeated,Second definition,https://example.org/r\n"
        f'{BRICK}Quoted,"A definition, with a comma",https://example.org/q\n'
    ),
    "too-many-columns": (
        "Term,Definition,See Also\n"
        f"{BRICK}Good,Kept before the raise,https://example.org/g\n"
        f"{BRICK}Bad,Too,many,fields\n"
        f"{BRICK}Never,Not reached,\n"
    ),
    "header-only": "Term,Definition,See Also\n",
}


class _PrintHandler(logging.Handler):
    """Print each record, so the harness compares it as the call's stdout."""

    def emit(self, record):
        print(f"LOG {record.levelname} {record.getMessage()}")


_root = logging.getLogger()
_root.addHandler(_PrintHandler())
_root.setLevel(logging.INFO)


def _graph(ttl):
    g = Graph()
    g.parse(data=ttl, format="turtle")
    return g


def call_with_hierarchy():
    os.chdir(EX_DIR)
    return ((_graph(HIERARCHY_TTL),), {})


def call_without_setpoint_class():
    os.chdir(EX_DIR)
    ttl = HIERARCHY_TTL.replace("brick:Setpoint rdfs:subClassOf brick:Class .", "")
    assert ttl != HIERARCHY_TTL
    return ((_graph(ttl),), {})


def call_with_brick_shapes():
    os.chdir(EX_DIR)
    return ((_graph(BRICK_SHAPES_TTL),), {})


_TMP = Path(tempfile.mkdtemp(prefix="add_definitions_"))


def _csv_case(name):
    def case():
        where = _TMP / name
        (where / "bricksrc").mkdir(parents=True, exist_ok=True)
        (where / "bricksrc" / "definitions.csv").write_text(
            CSV_CASES[name], encoding="utf-8")
        os.chdir(where)
        return ((_graph(HIERARCHY_TTL),), {})
    return case


try:
    VERDICT = run_pair(
        __file__,
        entry='add_definitions',
        calls=[call_with_hierarchy, call_with_brick_shapes,
               call_without_setpoint_class]
        + [_csv_case(name) for name in CSV_CASES],
    )
finally:
    os.chdir(EX_DIR)
    shutil.rmtree(_TMP, ignore_errors=True)
