# Context shim (see meta.json): the names the region takes from its package,
# from ktbs/ktbs@4f9f50c770, so it executes outside lib/ktbs. Identical
# bindings for both representations.
#
#  - KTBS_NS_URI / KTBS      lib/ktbs/namespace.py
#  - KTBS_NS_STATS           lib/ktbs/engine/trace_stats.py (NS)
#  - CONTEXT_URI             lib/ktbs/serpar/jsonld_parser.py
#  - load_document           same module: serves the JSON-LD context; unused by
#                            the stand-in `compact` below
#  - ValueConverter          lib/ktbs/serpar/jsonld_serializers.py: reduced to
#                            the conversions the fixture needs (URIRef ->
#                            {'@id'}, numeric Literal -> number, other Literal
#                            -> its lexical form)
#  - compact                 pyld.jsonld.compact. pyld is not installed in the
#                            study venv; this stand-in only contracts the keys
#                            that start with a namespace declared in the
#                            context to `prefix:local` (all the region needs
#                            to find 'stats:minTime' in its result). It never
#                            touches the RDF reads, which are what is compared.
from rdflib import Literal, Namespace, URIRef
from rdflib.namespace import XSD

KTBS_NS_URI = "http://liris.cnrs.fr/silex/2009/ktbs#"
KTBS = Namespace(KTBS_NS_URI)
KTBS_NS_STATS = Namespace("http://tbs-platform.org/2016/trace-stats#")
CONTEXT_URI = "http://liris.cnrs.fr/silex/2011/ktbs-jsonld-context"


def load_document(url, options=None):
    raise NotImplementedError("the stand-in compact() never loads a context")


class ValueConverter(object):
    def __init__(self, base_uri):
        self.base_uri = str(base_uri)

    def uri(self, uri):
        uri = str(uri)
        if uri.startswith(self.base_uri):
            return uri[len(self.base_uri):] or "."
        return uri

    def val2jsonobj(self, val):
        if isinstance(val, URIRef):
            return {"@id": self.uri(val)}
        if isinstance(val, Literal):
            if val.datatype in (XSD.integer, XSD.decimal, XSD.double,
                                XSD.float, XSD.long, XSD.int):
                return val.toPython()
            return str(val)
        return str(val)


def compact(doc, ctx, options=None):
    prefixes = {}
    for entry in ctx["@context"]:
        if isinstance(entry, dict):
            prefixes.update({p: str(ns) for p, ns in entry.items()
                             if isinstance(ns, (str, Namespace))
                             and not p.startswith("stats:") and p != "m"})
    out = {}
    for key, value in doc.items():
        for prefix, ns in prefixes.items():
            if isinstance(key, str) and key.startswith(ns):
                key = prefix + ":" + key[len(ns):]
                break
        out[key] = value
    return out
