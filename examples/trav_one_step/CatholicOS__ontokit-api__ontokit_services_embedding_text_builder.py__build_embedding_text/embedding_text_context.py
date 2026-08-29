# Context shim (see meta.json): _local_name from CatholicOS/ontokit-api@23680a4d04
# : ontokit/services/embedding_text_builder.py (lines 56-60), so the region
# executes outside the module. Identical bindings for both representations.


def _local_name(iri: str) -> str:
    """Extract local name from IRI."""
    if "#" in iri:
        return iri.split("#")[-1]
    return iri.rsplit("/", 1)[-1]
