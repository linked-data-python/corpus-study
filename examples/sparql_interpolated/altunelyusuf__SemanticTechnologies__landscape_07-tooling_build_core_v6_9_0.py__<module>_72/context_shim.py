# Context shim (see meta.json): subset of what the real file assembles
# before this region, from altunelyusuf/SemanticTechnologies@bad0fa7c46 :
# landscape/07-tooling/build_core_v6_9_0.py.
#
# `nodes` (real file lines 34-41): a list of dicts built from tax.TAX, each
# carrying at least an "id" key -- `byid = {n["id"]: n for n in nodes}` is
# built from it right where this region starts. Reduced here to just the
# "id" keys the region actually reads.
#
# `eg` (real file line 20): `eg = load("enrichment_g", "v3_0_0")`, where
# `load()` (real file lines 11-13) does
# `importlib.util.spec_from_file_location(name, f"{BASEDIR}/07-tooling/{name}_{ver}.py")`
# against `BASEDIR = "/home/claude/semtech-landscape"`, an absolute path
# that does not exist outside the original environment -- so `eg` stands
# in directly for the imported module, exposing exactly the two attributes
# this region reads: SNIPPETS and SNIPPET_PREFIXES.
#
# SNIPPET_PREFIXES is copied verbatim (trimmed to the three prefixes the
# snippets below use) from enrichment_g_v3_0_0.py's own SNIPPET_PREFIXES at
# the pinned commit. SNIPPETS is NOT copied verbatim: every real entry in
# that file is syntactically valid (the real build script calls
# `sys.exit(1)` on the first pre-check failure, so nothing invalid is ever
# committed) -- so a literal copy would never exercise this region's
# `except Exception` branch, an empty-errors hollow green that would not
# tell a broken translation from a correct one. The entries below keep two
# real ones (T1C2, T1C3, both trimmed from enrichment_g_v3_0_0.py) and add
# deliberately invalid/unknown ones so `errs` ends up with a real,
# multi-shaped result: a valid+known snippet of each check kind (no
# error), a known snippet with broken syntax (checked -> "snippet
# invalid"), an unknown but valid snippet (unchecked class id -> "snippet
# class unknown"), an unknown AND invalid snippet (both errors on the same
# cid), and a known snippet whose check is "none" -- deliberately
# garbage-shaped code that must NOT raise anything, because check == "none"
# skips validation entirely (the neighbourhood that must not match).

SNIPPET_PREFIXES = (
    "@prefix ex: <http://example.org/x#> .\n"
    "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
    "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
)

nodes = [
    {"id": "T1C2"},
    {"id": "T1C3"},
    {"id": "T1C6"},
    {"id": "T2C1"},
    {"id": "T9X1"},
]

SNIPPETS = {
    # valid + known, one per check kind -> no error
    "T1C2": ("turtle", "A class and a subclass",
             "ex:Garment a owl:Class .\nex:TShirt rdfs:subClassOf ex:Garment .",
             "turtle"),
    "T1C3": ("sparql", "Transitive reach with a property path",
             "SELECT ?type WHERE { ex:TShirt rdfs:subClassOf+ ?type . }",
             "sparql"),
    "T1C6": ("json", "A minimal JSON-LD context",
             '{ "@context": { "gtin": "https://gs1.org/voc/gtin" } }',
             "json"),
    # known cid, broken turtle (missing trailing '.') -> "snippet invalid"
    "T2C1": ("turtle", "Broken turtle: missing the final '.'",
             "ex:Bad a owl:Class", "turtle"),
    # unknown cid, otherwise-valid turtle -> "snippet class unknown" only
    "GHOST1": ("turtle", "Valid turtle, but the class id does not exist",
               "ex:Ghost a owl:Class .", "turtle"),
    # unknown cid AND broken sparql -> both errors, same cid
    "GHOST2": ("sparql", "Unclosed WHERE clause, unknown class id",
               "SELECT ?x WHERE {", "sparql"),
    # known cid, garbage code, but check == "none" -> skipped, no error
    "T9X1": ("python", "Not validated at all (check == none)",
             "this is not valid turtle, sparql or json !!!", "none"),
}
