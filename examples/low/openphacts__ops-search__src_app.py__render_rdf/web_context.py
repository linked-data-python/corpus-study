# Context shim (see meta.json): stand-ins for the bottle bindings that
# src/app.py imports in openphacts/ops-search@170caa5881.  bottle is not a
# dependency of the evaluation environment and the region only reads
# ``request.url`` (used as the JSON-LD publicID).
# Used IDENTICALLY by original.py and translated.ldpy.


class _Request:
    """Minimal bottle.request stand-in: the region reads only ``url``."""
    url = "http://example.org/search?q=aspirin"


request = _Request()


def hook(*a, **k):          # decorator factories, unused by the region
    return lambda f: f


def route(*a, **k):
    return lambda f: f


def get(*a, **k):
    return lambda f: f


def post(*a, **k):
    return lambda f: f


def run(*a, **k):
    raise NotImplementedError("bottle.run is not exercised by this region")


def static_file(*a, **k):
    raise NotImplementedError


def url(*a, **k):
    raise NotImplementedError


class Bottle:
    pass


class _Response:
    content_type = None


response = _Response()
