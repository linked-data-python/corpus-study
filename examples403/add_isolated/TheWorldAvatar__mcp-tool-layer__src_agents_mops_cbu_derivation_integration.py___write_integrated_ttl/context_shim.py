# Context shim (see meta.json), for TheWorldAvatar/mcp-tool-layer@c440a33e08 :
# src/agents/mops/cbu_derivation/integration.py.
#
# ONTOMOPS is the real namespace constant _write_integrated_ttl uses
# (line 536 of the source file, a local defined earlier in the same
# function) -- restored here unchanged. mop_subject and selected_cbus are
# further locals the enclosing function builds earlier in its body
# (MOP-subject selection over a parsed source TTL, an LLM-provided
# metal/organic CBU pair) -- reproduced here with minimal, hand-written
# test data instead of that upstream pipeline (parsing a source TTL,
# calling an LLM), covering:
#  * a CBU with a non-empty label that is also newly generated (exercises
#    every conditional add in the region: label, formula, ChemicalInput);
#  * a CBU with an empty-string label that already exists (label IS added
#    -- "" is not None -- but formula is NOT, since "" is falsy, and
#    ChemicalInput is NOT added either, since is_generated is False);
#  * a CBU with no label at all (None) that already exists (neither label
#    nor formula added).
#
# outg is NOT shimmed here on purpose: original.py and translated.ldpy each
# still write `outg = Graph()` themselves (matching the source's own line
# 605, restored the same way as the missing-graph-binding case), so each
# side gets its own fresh Graph. A shared outg here would be the SAME
# Graph object imported by both sides (module import is cached), so run_pair
# would compare it to itself and pass even if the +{ } rewrite were wrong --
# confirmed empirically (see meta.json translation_notes).
from rdflib import Namespace, URIRef

ONTOMOPS = Namespace("https://www.theworldavatar.com/kg/ontomops/")

mop_subject = URIRef("https://www.theworldavatar.com/kg/ontomops/MOP_1")
selected_cbus = [
    ("https://www.theworldavatar.com/kg/ontomops/CBU_metal_1", "Zn3(COO)6", True),
    ("https://www.theworldavatar.com/kg/ontomops/CBU_organic_1", "", False),
    ("https://www.theworldavatar.com/kg/ontomops/CBU_existing_1", None, False),
]
