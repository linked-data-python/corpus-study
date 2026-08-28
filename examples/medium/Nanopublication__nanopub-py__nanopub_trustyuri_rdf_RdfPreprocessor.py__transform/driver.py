"""Validation driver for Nanopublication__nanopub-py__..._RdfPreprocessor.py__transform.

`transform` maps one RDF term of a nanopublication onto its trusty-URI form.
It is a pure function, so the pair is compared by calling it on fixtures that
cover every branch: the None short-circuit, the two baseuri-is-None paths
(bytes-decodable and not), and the get_trustyuri path for a URIRef inside the
nanopub namespace, for a URIRef outside it, and for blank nodes (which also
exercises the mutation of the shared `bnodemap`, compared as an argument).

The region's imports are left exactly as upstream; `nanopub` is made importable
by putting the corpus checkout of the pinned commit on sys.path (see meta.json).
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
_REPO = (Path(__file__).resolve().parents[3]
         / "corpus" / "repos" / "Nanopublication__nanopub-py")
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from rdflib.term import BNode, URIRef  # noqa: E402

from rdfeval.harness import run_pair  # noqa: E402

ARTIFACT = "RAiCTuRUZTGB2E0j3RaTQ2ZCEP8HUOKF3f5YFHz2eEgQ"
DUMMY_NS = "http://purl.org/nanopub/temp/mynanopub#"


def no_uri():
    return ((None, ARTIFACT, DUMMY_NS, {}), {})


def no_baseuri_no_hash():
    return ((URIRef("http://example.org/np#assertion"), None, None, {}), {})


def no_baseuri_with_hash():
    return ((URIRef("http://example.org/np#" + ARTIFACT), ARTIFACT, None, {}), {})


def uri_in_namespace():
    return ((URIRef(DUMMY_NS + "assertion"), ARTIFACT, DUMMY_NS, {}), {})


def uri_outside_namespace():
    return ((URIRef("http://example.org/concept/1"), ARTIFACT, DUMMY_NS, {}), {})


def rdflib_bnodes():
    # two auto-generated bnodes numbered through the shared bnodemap
    return ((BNode("N2b80343001e94f48bdee0901be566ebb"), ARTIFACT, DUMMY_NS, {}), {})


def named_bnode():
    return ((BNode("myBlankNode"), ARTIFACT, DUMMY_NS, {}), {})


VERDICT = run_pair(__file__, entry="transform",
                   calls=[no_uri, no_baseuri_no_hash, no_baseuri_with_hash,
                          uri_in_namespace, uri_outside_namespace,
                          rdflib_bnodes, named_bnode])
