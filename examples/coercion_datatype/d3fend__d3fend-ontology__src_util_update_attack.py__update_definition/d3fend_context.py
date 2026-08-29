# Context shim (see meta.json): subset of src/util/update_attack.py from
# d3fend/d3fend-ontology@cce593d61c, so the region executes outside the file.
#
# get_attack_id is defined at module scope of update_attack.py (lines 98-106),
# outside this region (lines 455-475); reproduced here verbatim.
#
# _xmlns: the real file imports it with `from build import get_graph, _xmlns
# as _XMLNS` (src/util/update_attack.py line 7). At this commit,
# src/util/build.py (the only build.py in the repository, and the one on the
# path when update_attack.py is run from src/util/) defines no `_xmlns` at
# all -- checked by grep over the whole file: apparent drift/breakage
# upstream, not something this shim can recover. We supply the d3fend
# ontology namespace instead, which is what `attack_uri = URIRef(_XMLNS +
# attack_id)` needs to build a "http://d3fend.mitre.org/...#T####"-style
# attack-technique URI (consistent with the `d3fend = Namespace(...)` already
# declared in the region's own context, same base IRI).
#
# get_graph (also imported by the real line 7) is not called anywhere in this
# region's body, so it is not reproduced here.
#
# Identical bindings for both representations.

_xmlns = "http://d3fend.mitre.org/ontologies/d3fend.owl#"


def get_attack_id(stix_object, framework):
    return next(
        (
            ref.get("external_id")
            for ref in stix_object["external_references"]
            if ref.get("source_name") == "mitre-attack"
            or ref.get("source_name") == f"mitre-{framework}-attack"
        ),
        None,
    )
