# Context shim (see meta.json): stands in for the JonAnderAsua/
# TFG-KG-RelacionesClientelares `TextToTriple` instance that `grafoaSortu`
# reads through `self` (procesSource/source/gate_cloud.py @ 82875c5f94,
# verified against the source repository at that commit).
#
# `getType` is copied verbatim: it is a pure function of its argument, so it
# is safe to reproduce exactly.
#
# `balioztatu` and `bilatuUria` are NOT reproduced. In the real class:
#   - `balioztatu` calls `input(...)` and blocks for a human to confirm each
#     annotation's classification;
#   - `bilatuUria` issues a live SPARQL SELECT against `self.tripleStore`.
# Neither can run inside this harness. Both are fixture-driven stand-ins
# instead: they answer from a dict supplied by the driver, keyed exactly as
# `grafoaSortu` calls them (`subj`/`izena` is the annotation text). This
# reproduces the CONTRACT `grafoaSortu` depends on (a bool+label pair, a
# URI string), not the withheld interactive/networked logic -- identical
# for both the original and translated sides, which import this same class.
from rdflib import Graph


class TextToTripleStub:
    """Duck-types the members of TextToTriple that grafoaSortu uses."""

    def __init__(self, validations, uris):
        self.grafoa = Graph()
        self._validations = dict(validations)  # annotationText -> (bool, obj)
        self._uris = dict(uris)  # annotationText -> uri string

    def getType(self, erlazioa):
        # Verbatim from TextToTriple.getType (pure, no I/O).
        base = 'https://schema.org/'
        if erlazioa == 'Location':
            emaitza = base + 'Place'
        else:
            emaitza = base + erlazioa
        return emaitza

    def balioztatu(self, subj, obj):
        # Stand-in for the interactive confirmation prompt.
        return self._validations[subj]

    def bilatuUria(self, izena):
        # Stand-in for the live SPARQL lookup.
        return self._uris[izena]
