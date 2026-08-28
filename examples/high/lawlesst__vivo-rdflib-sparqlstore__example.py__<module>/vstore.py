# Context shim (see meta.json): stand-in for the ``vstore`` package of
# lawlesst/vivo-rdflib-sparqlstore@9e3a3d8efb (vstore/vstore.py).  The real
# VIVOStore / VIVOUpdateStore are rdflib SPARQLStore / SPARQLUpdateStore
# subclasses that inject VIVO's e-mail+password parameters into every request
# against a live VIVO endpoint.  The evaluation has no such endpoint, so the
# shim keeps the same constructor and ``open((query, update))`` contract but
# backs the store with rdflib's in-memory store; every graph operation in the
# region (+=, -=, subjects, value, remove, Resource.set) then behaves as it
# would against the remote store, without the network.
# Used IDENTICALLY by original.py and translated.ldpy.
from rdflib.plugins.stores.memory import Memory


class VIVOStore(Memory):
    def __init__(self, email=None, password=None, **kwargs):
        self.email = email
        self.password = password
        super().__init__(**kwargs)

    def open(self, configuration, create=False):
        self.query_endpoint, self.update_endpoint = configuration
        return 1  # rdflib's VALID_STORE


class VIVOUpdateStore(VIVOStore):
    def __init__(self, email, password, **kwargs):
        super().__init__(email=email, password=password, **kwargs)
