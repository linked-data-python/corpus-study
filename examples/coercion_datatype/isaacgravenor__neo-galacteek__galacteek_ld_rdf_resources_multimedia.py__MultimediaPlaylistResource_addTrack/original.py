# Extracted from isaacgravenor/neo-galacteek@e201b39d78 : galacteek/ld/rdf/resources/multimedia.py
# region: MultimediaPlaylistResource.addTrack (lines 77-80, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import Literal, Graph, URIRef
from context_shim import ipsTermUri as term, MultimediaPlaylistResource  # context shim, see meta.json

def addTrack(self, rsc):
    self.add(term('track'), rsc)
    self.remove(term('numTracks'), None)
    self.add(term('numTracks'), Literal(len(self.track)))


# Demo harness (identical on both sides, see meta.json): addTrack is a
# bound-method extraction -- MultimediaPlaylistResource is the enclosing
# class (restored via context_shim.py), and the region reaches self.add /
# self.remove (inherited from rdflib.resource.Resource) and self.track (the
# enclosing class's own property). demo() builds a real
# MultimediaPlaylistResource over a fresh Graph and calls addTrack twice, so
# the second call exercises addTrack's own "remove the old numTracks, then
# re-add" logic against a graph that already has one. wrap_as_resource
# mirrors the two ways a caller passes `rsc` in the real repository (a bare
# URIRef, or -- the only real call site found, galacteek/ui/mediaplayer/
# __init__.py:1075, `self.model.rsc.addTrack(rsc)` where rsc is itself a
# Resource -- a Resource instance): rdflib.resource.Resource.add/remove
# transparently unwrap a Resource argument to its `.identifier` before
# writing the triple, so both call shapes are exercised here.
def demo(rsc1, rsc2, wrap_as_resource):
    subject = URIRef('ips://galacteek.ld/playlist/1')
    self = MultimediaPlaylistResource(Graph(), subject)
    if wrap_as_resource:
        rsc1 = MultimediaPlaylistResource(Graph(), rsc1)
        rsc2 = MultimediaPlaylistResource(Graph(), rsc2)
    addTrack(self, rsc1)
    addTrack(self, rsc2)
    return self.graph
