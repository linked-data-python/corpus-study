# Context shim (see meta.json): rdfrest is not vendored in this workspace and
# has no published release to pin against (not on PyPI; its GitHub mirror
# holds no source at the pinned tag), so coerce_to_node/coerce_to_uri/
# parent_uri below are a best-effort reconstruction from their call sites in
# lib/ktbs/api/base.py, not an extract of the real rdfrest.util. KTBS and
# SKOS are the real namespaces from ktbs/ktbs@4f9f50c770's lib/ktbs/namespace.py
# and lib/ktbs/utils.py. Identical bindings for both representations.
from urllib.parse import urljoin

from rdflib import BNode, Namespace, URIRef

KTBS = Namespace("http://liris.cnrs.fr/silex/2009/ktbs#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")


class InvalidDataError(Exception):
    """Raised when a supplied graph/argument is not valid for the resource."""


def coerce_to_uri(value, base=None):
    """Coerce a URIRef/str to an absolute URIRef, resolved against base."""
    if isinstance(value, URIRef):
        return value
    return URIRef(urljoin(str(base) if base is not None else "", str(value)))


def coerce_to_node(value, base=None):
    """Like coerce_to_uri, but None becomes a fresh BNode (new resource)."""
    if value is None:
        return BNode()
    if isinstance(value, (URIRef, BNode)):
        return value
    return URIRef(urljoin(str(base) if base is not None else "", str(value)))


def parent_uri(uri):
    """The URI of the collection containing the resource at uri."""
    text = str(uri)
    return URIRef(text.rsplit("/", 2)[0] + "/") if text.endswith("/") \
        else URIRef(text.rsplit("/", 1)[0] + "/")


def extend_api(*_args, **_kwargs):
    """No-op stand-in for ktbs.utils.extend_api (a class-decorator factory)."""
    def decorator(cls):
        return cls
    return decorator
