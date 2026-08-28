# Context shim (see meta.json): stand-in for the `asterism` project package
# (kumagallium/asterism), which is not installed in the study venv.
# original.py does `from asterism import crosswalk_runtime, substrate`
# unmodified; this file is named `asterism.py` and sits next to the pair on
# sys.path (the driver runs with cwd=<region dir>), so that same bare import
# resolves to it, identically for both representations.
#
# `substrate` below is not a fabricated stand-in: it reproduces, verbatim,
# the handful of names `_seed_promoted` actually touches, copied from
# ingest/src/asterism/substrate.py at kumagallium/asterism@f0977d4d3a
# (fetched via `gh api repos/kumagallium/asterism/contents/...`) --
# CONTROL_GRAPH_IRI, STATUS_PREDICATE, and canonical_graph_iri() with its
# real dataset-id validation regex. `crosswalk_runtime` is imported by the
# real test file but never referenced inside this extracted region: an empty
# stand-in, only the name needs to resolve.

import re

_DATASET_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class crosswalk_runtime:
    """Unused within this region; only the name needs to resolve."""


class substrate:
    LIFECYCLE_GRAPH_BASE = "https://kumagallium.github.io/asterism/graph/"
    CANONICAL_GRAPH_BASE = LIFECYCLE_GRAPH_BASE + "canonical/"
    CONTROL_GRAPH_IRI = LIFECYCLE_GRAPH_BASE + "control"
    ASTERISM_NS = "https://kumagallium.github.io/asterism/vocab#"
    STATUS_PREDICATE = ASTERISM_NS + "status"

    @staticmethod
    def canonical_graph_iri(dataset_id: str) -> str:
        if not _DATASET_ID.match(dataset_id):
            raise ValueError(f"unsafe dataset_id for graph IRI: {dataset_id!r}")
        return f"{substrate.CANONICAL_GRAPH_BASE}{dataset_id}"
