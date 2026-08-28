# Extracted from pyscal/atomRDF@c9b070e15f : atomrdf/graph.py
# region: KnowledgeGraph.trace (lines 1403-1433, stratum ns_import_project)
# licence of the source repository: see meta.json
def trace(self, sample_or_property):
    """Trace the provenance of a sample or calculated property.

    Parameters
    ----------
    sample_or_property : str or URIRef
        A sample URI (e.g. ``"sample:abc"``) or a calculated-property
        URI.  If the URI matches a sample the trace walks backwards
        from that sample; if it matches a property the owning sample
        is found first.

    Returns
    -------
    Provenance
        An iterable of pipeline step dicts with reconstructed ASE
        structures, method metadata, parameters, etc.
    """
    from atomrdf.io.provenance import Provenance

    uri = str(sample_or_property)
    # Decide: is this a sample or a property?
    from atomrdf.namespace import ASMO as _ASMO

    is_property = bool(
        self.graph.query(
            f"ASK {{ ?s <{str(_ASMO.hasCalculatedProperty)}> <{uri}> }}"
        )
    )
    if is_property:
        return Provenance.from_property(self, uri)
    return Provenance.from_sample(self, uri)
