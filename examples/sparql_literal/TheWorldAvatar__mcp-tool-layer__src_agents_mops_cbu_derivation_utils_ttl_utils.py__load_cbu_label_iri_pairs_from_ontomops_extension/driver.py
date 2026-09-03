"""Validation driver for
TheWorldAvatar__mcp-tool-layer__src_agents_mops_cbu_derivation_utils_ttl_utils.py__load_cbu_label_iri_pairs_from_ontomops_extension.

The region is a reading region (design record corpus/405): it loads a TTL
file from disk -- built from `models.locations.DATA_DIR`/`hash_value`/a
fixed file name -- and returns a plain list of (label, iri) pairs, so the
oracle is value equality, not graph isomorphism.

Two bindings had to be restored (AGENT_BATCH's ~163-regions case), both
verified against the pinned commit and kept minimal, no invented logic
(see `ttl_utils_shim.py` and `models/locations.py` for the detail):

  - `load_graph_from_file` is a SIBLING helper in the same source file
    (ttl_utils.py), stripped by line-range extraction along with every
    other function in that module; restored verbatim.
  - `models.locations.DATA_DIR` is resolved to a fixed path next to the
    shim (`data/`), rather than reproducing the real module's
    `.env`-loading / directory-existence-checking machinery, which is not
    part of what this region reads.

`fixture.ttl` (duplicated at `data/sample-hash/ontomops_extension.ttl` --
the exact path `os.path.join(DATA_DIR, "sample-hash",
"ontomops_extension.ttl")` computes, see that file's own header) holds
three ontomops:ChemicalBuildingUnit individuals, two of them sharing a
label (exercising "deduplicate by label, first seen wins"), plus a
ChemicalBuildingUnit with no label and a labelled resource of a different
type -- neighbourhood that must NOT appear in the result. A second call
uses a hash_value for which no file was ever written: `load_graph_from_file`
's own `os.path.exists` guard then returns an empty graph, the
zero-solution case, without needing a second fixture file. No `ORDER BY`
and no `sorted()` anywhere in the region: `ordered=False`.
"""
from rdfeval.harness import run_pair

_HASH_WITH_DATA = "sample-hash"
_HASH_WITHOUT_DATA = "missing-hash"


VERDICT = run_pair(
    __file__,
    entry="load_cbu_label_iri_pairs_from_ontomops_extension",
    fixture="fixture.ttl",
    calls=[
        ((_HASH_WITH_DATA,), {}),
        ((_HASH_WITHOUT_DATA,), {}),
    ],
    ordered=False,
)
