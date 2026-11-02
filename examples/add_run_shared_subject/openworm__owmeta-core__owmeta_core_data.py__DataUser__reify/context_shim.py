# Context shim (see meta.json): what DataUser._reify reads of `self`, from
# openworm/owmeta-core@cd69d77ad0 (owmeta_core/data.py), so the method can
# be called outside the package. Identical bindings for both
# representations; only the driver imports it.
#
# In the repository `self.conf` is a Data configuration object and
# conf['new_graph_uri'] a function that mints the IRI of the graph
# (statement) a triple is reified into. Here it derives a stable IRI from
# the triple, which is all the region needs of it.
import hashlib

from rdflib import URIRef


def new_graph_uri(triple):
    digest = hashlib.sha1("|".join(str(t) for t in triple).encode()).hexdigest()
    return URIRef("http://example.org/statement/" + digest[:12])


class DataUser:
    def __init__(self):
        self.conf = {"new_graph_uri": new_graph_uri}
