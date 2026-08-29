# Context shim (see meta.json): the two namespaces this region imports from
# fdpneo_server.shared.namespaces, from FAIRDataTeam/fdpneo-server@3e72e119ae
# (src/fdpneo_server/shared/namespaces.py, lines 28-29) — the package is not
# installed and pulls in the rest of the server (FastAPI app, config,
# settings). Copied verbatim; both are also rdflib's own well-known
# namespaces (rdflib.namespace.DCAT / DCTERMS) at the same IRIs.
# Identical bindings for both representations.
from rdflib import Namespace

DCAT = Namespace("http://www.w3.org/ns/dcat#")
DCT = Namespace("http://purl.org/dc/terms/")
