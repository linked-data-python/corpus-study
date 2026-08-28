# Context shim (see meta.json): what the region needs from
# RDFLib/pyLODE@0d0471fb99 that is not in the extracted context.
#
#   * LODE -- pylode/profiles/supermodel/namespace.py declares it as an
#     rdflib DefinedNamespace over https://w3id.org/lode/ns/pylode/ ; the
#     region only ever reads LODE.config, so a plain Namespace over the same
#     IRI is used here (the pylode package itself cannot be imported in the
#     evaluation venv: pylode/__init__.py pulls in dominate, httpx, kurra).
#
#   * fetch -- pylode/profiles/supermodel/loader.py fetches the remote
#     resource with an httpx GET.  It is replaced here by an offline
#     stand-in with the same signature and the same return contract
#     (text, content_type), reading from the canned document store carried
#     by the client object the driver supplies.  The content-type
#     negotiation over MEDIA_TYPES is kept.
#
# Used identically by original.py and translated.ldpy.
from rdflib import Namespace

LODE = Namespace("https://w3id.org/lode/ns/pylode/")

MEDIA_TYPES = {
    "text/turtle": "text/turtle",
    "application/n-triples": "application/n-triples",
    "application/n-quads": "application/n-quads",
}


def fetch(url: str, client, content_type: str = "text/turtle") -> tuple[str, str]:
    text, response_content_type = client.get(url, content_type)
    for media_type in MEDIA_TYPES:
        if media_type in response_content_type:
            content_type = media_type
    return text, content_type
