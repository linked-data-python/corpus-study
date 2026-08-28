"""Validation driver for MKLab-ITI__prophet__rdflib_plugins_sparql_sparql.py__Prologue_absolutize.

`Prologue.absolutize` is the SPARQL engine's own runtime term resolver: it turns
parse values into RDF terms using the query's BASE and PREFIX declarations.  The
region was extracted as a module-level function, so it is called directly with a
stand-in Prologue copied from the same source file (lines 341-359).  Fixtures
cover the four branches: a pname, a literal with a language tag, a literal whose
datatype is itself a pname (the recursive call), a relative IRI resolved against
the base, and two values returned untouched.
"""
import sys

sys.dont_write_bytecode = True  # the shim next to this driver is imported

import inspect

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import NamespaceManager

from rdfeval.harness import run_pair

from parserutils import CompValue


class Prologue:
    """Copied from MKLab-ITI/prophet@eee2ab51de rdflib/plugins/sparql/sparql.py
    lines 341-359: the class the region is a method of."""

    def __init__(self):
        self.base = None
        self.namespace_manager = NamespaceManager(Graph())

    def resolvePName(self, prefix, localname):
        ns = self.namespace_manager.store.namespace(prefix or "")
        if ns is None:
            raise Exception('Unknown namespace prefix : %s' % prefix)
        return URIRef(ns + (localname or ""))

    def bind(self, prefix, uri):
        self.namespace_manager.bind(prefix, uri, replace=True)

    def absolutize(self, iri):
        """The literal branch recurses through ``self.absolutize``.  The region
        was extracted as a module-level function, so re-enter the very module
        that is calling us -- original.py or translated.ldpy -- instead of
        re-implementing it here (which would make the recursive step untested).
        """
        caller = inspect.currentframe().f_back
        return caller.f_globals["absolutize"](self, iri)


# one shared instance: the two fixture invocations must yield equal arguments
PROLOGUE = Prologue()
PROLOGUE.base = "http://example.org/data/"
PROLOGUE.bind("ex", "http://example.org/ns#")
PROLOGUE.bind("xsd", "http://www.w3.org/2001/XMLSchema#")

PNAME = CompValue("pname", prefix="ex", localname="thing")
LANG_LITERAL = CompValue("literal", string="bonjour", lang="fr")
TYPED_LITERAL = CompValue(
    "literal", string="42",
    datatype=CompValue("pname", prefix="xsd", localname="integer"))
PLAIN_IRI = URIRef("http://example.org/absolute")
RELATIVE_IRI = URIRef("relative/path")
UNTOUCHED = Literal("already a term")


def _call(v):
    def fixture():
        return ((PROLOGUE, v), {})
    return fixture


VERDICT = run_pair(__file__, entry="absolutize",
                   calls=[_call(PNAME), _call(LANG_LITERAL),
                          _call(TYPED_LITERAL), _call(PLAIN_IRI),
                          _call(RELATIVE_IRI), _call(UNTOUCHED)])
