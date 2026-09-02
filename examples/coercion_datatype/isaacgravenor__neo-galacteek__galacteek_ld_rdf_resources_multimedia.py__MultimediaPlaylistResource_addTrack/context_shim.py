# Context shim (see meta.json): restores bindings the extracted region reads
# but does not define, from isaacgravenor/neo-galacteek@e201b39d78 (verified
# against the source repository at that commit). The real `galacteek`
# package cannot be imported standalone (PyQt5/asyncio-IPFS application, not
# on PyPI as an importable library) -- everything below is copied VERBATIM
# from the pinned commit rather than installed.
from rdflib import URIRef
from rdflib.resource import Resource


# Copied VERBATIM from galacteek/ld/__init__.py:16-20 (only `ipsTermUri`,
# which this region calls; the module also defines ipsContextUri,
# uriTermExtract, ldContextsRootPath, ldRenderersRootPath, which pull in
# `yarl` and `galacteek.core` and are not read by addTrack).
def ipsTermUri(name: str, fragment: str = None, ips: str = "galacteek.ld") -> URIRef:
    if fragment:
        return URIRef(f"ips://{ips}/{name}#{fragment}")
    else:
        return URIRef(f"ips://{ips}/{name}")


# Copied VERBATIM from galacteek/ld/rdf/resources/__init__.py:1-7 -- the
# base class MultimediaPlaylistResource extends. addTrack itself never calls
# `.replace`, but the class chain is reproduced as-is rather than flattened.
class IPR(Resource):
    def replace(self, p, o):
        self.remove(p)
        self.add(p, o)


# Only the one property addTrack reads (`self.track`), copied VERBATIM from
# galacteek/ld/rdf/resources/multimedia.py:65-67. The class's other
# properties/methods (trackResource, name, removeTrack, findByPath) are not
# reached by addTrack and are left out.
class MultimediaPlaylistResource(IPR):
    @property
    def track(self):
        return list(self.objects(ipsTermUri("track")))
