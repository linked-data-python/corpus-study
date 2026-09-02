"""Validation driver for
isaacgravenor__neo-galacteek__galacteek_ld_rdf_resources_multimedia.py__MultimediaPlaylistResource_addTrack.

`addTrack` is a method (`self` an explicit first parameter), so both sides
carry an identical `demo(rsc1, rsc2, wrap_as_resource)` harness (see
meta.json and original.py) that builds a real MultimediaPlaylistResource
(context_shim.py, copied verbatim from the pinned commit) over a fresh
Graph, calls addTrack twice, and returns the resource's `.graph` --
comparing that graph, not the resource instance (which would need an
__eq__ for no benefit; the graph is the only observable effect).

CALL_1 -- wrap_as_resource=False: rsc1/rsc2 are bare URIRefs, the simple
case. Exercises the coercion_datatype site (Literal(len(self.track)) vs the
language's default int coercion) and the self.remove(..., None) wildcard on
the second addTrack call, once numTracks already has a value from the
first.

CALL_2 -- wrap_as_resource=True: rsc1/rsc2 are themselves
MultimediaPlaylistResource instances, matching the one real call site found
in the source repository (galacteek/ui/mediaplayer/__init__.py:1075,
`self.model.rsc.addTrack(rsc)` where rsc is a Resource). Exercises
rdflib.resource.Resource.add/remove's transparent Resource -> .identifier
unwrap, which original.py gets for free through inheritance and
translated.ldpy reproduces explicitly (see meta.json).
"""
from rdflib import URIRef

from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry="demo",
    calls=[
        ((URIRef("ips://galacteek.ld/track/1"), URIRef("ips://galacteek.ld/track/2"), False), {}),
        ((URIRef("ips://galacteek.ld/track/3"), URIRef("ips://galacteek.ld/track/4"), True), {}),
    ],
)
