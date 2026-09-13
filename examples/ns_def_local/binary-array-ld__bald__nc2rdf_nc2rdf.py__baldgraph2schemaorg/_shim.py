# Context shim (see meta.json): subset of nc2rdf/nc2rdf.py from
# binary-array-ld/bald@ca59666abe, so the region executes outside the
# package. Identical bindings for both representations.
#
# `bald.schemaOrg().distribution(container, schema_g, baseuri)` as called by
# the region does not match the shape of `bald.schemaOrg` in this same
# checkout (lib/bald/__init__.py:1463 takes `graph` in `__init__` and has no
# public `distribution` method taking three arguments) -- a pre-existing
# mismatch in the source repository, not something this translation study
# introduces. The stand-in below only needs to behave identically on both
# sides of the comparison, so it returns the graph it is given unchanged.
import os
from urllib.parse import urlparse


def isUrl(url):
    try:
        result = urlparse(url)
        if all([result.scheme, result.netloc, result.path]) and (
            result.scheme == "https" or result.scheme == "http"
        ):
            return True
    except Exception:
        return False


def getBasename(urlstr):
    return os.path.basename(urlstr)


class schemaOrg:
    def distribution(self, container, graph, baseuri):
        return graph
