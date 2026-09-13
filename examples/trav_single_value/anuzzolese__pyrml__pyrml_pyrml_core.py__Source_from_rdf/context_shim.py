# Context shim (see meta.json): subset of pyrml/rml_vocab.py from
# anuzzolese/pyrml@d18fe2edfc (namespace IRIs), plus minimal stand-ins for
# the sibling classes `Source` and `SQLSource` that pyrml_core.py defines
# elsewhere in the same module -- the region only calls `Source.__build`
# (its own private constructor) and `SQLSource.from_rdf` (a different
# branch, not exercised by the fixture: no rdf:type d2rq:Database triple).
# Identical bindings for both representations.
from rdflib import Namespace


class rml_vocab:
    RML_NS = Namespace("http://semweb.mmlab.be/ns/rml#")
    CSVW_NS = Namespace("http://www.w3.org/ns/csvw#")
    SD_NS = Namespace("http://www.w3.org/ns/sparql-service-description#")
    D2RQ_NS = Namespace("http://www.wiwiss.fu-berlin.de/suhl/bizer/D2RQ/0.1#")


class Source:
    pass


def _source_build_stub(g, parent, source, sourcetype):
    # Minimal stand-in for Source.__build: pyrml's real constructor builds a
    # TermMap subclass instance from (g, parent, source, sourcetype); this
    # shim only needs to produce a value the two representations agree on.
    return (source, sourcetype)


# Assigned outside the class body so the name is NOT mangled (a `def
# __build` written inside `class Source:` would become `_Source__build`,
# which is not what the extracted region's literal `Source.__build` call
# resolves to once it lives outside the class it came from).
Source.__build = staticmethod(_source_build_stub)


class SQLSource:
    @staticmethod
    def from_rdf(g, db):
        return None
