# Extracted from isaacgravenor/neo-galacteek@e201b39d78 : galacteek/ld/rdf/resources/multimedia.py
# region: MultimediaPlaylistResource.addTrack (lines 77-80, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import Literal
from galacteek.ld import ipsTermUri as term

def addTrack(self, rsc):
    self.add(term('track'), rsc)
    self.remove(term('numTracks'), None)
    self.add(term('numTracks'), Literal(len(self.track)))
