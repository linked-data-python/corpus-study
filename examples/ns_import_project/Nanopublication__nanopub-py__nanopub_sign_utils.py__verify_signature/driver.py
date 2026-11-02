"""Validation driver for Nanopublication__nanopub-py__nanopub_sign_utils.py__verify_signature.

This region READS a graph, so the oracle is the equality of the values both
versions produce from the same input -- here a raise is as much a value as
a return, and the harness compares it by type and message.  The input is a
Dataset, which `fixture=` (a Turtle file parsed into a Graph) cannot give:
`fixture.trig` is a real signed nanopublication (made once with
nanopub's own `add_signature`, RSA-2048, key discarded) and each call parses
it into a fresh Dataset, then breaks it in one way:

  * untouched                         -> True (a real RSA key and signature)
  * a source URI nobody targets       -> "No Signature targeting ..." raised
  * the signature triple removed      -> "No Signature found ..." raised
  * the source URI of a decoy         -> its algorithm is "DSA": logged, True
  * the source URI of another decoy   -> algorithm "ECDSA": raised
  * decoys with no algorithm / no signature -> IndexError / "No Signature found"
  * the algorithm "dsa" / "rsa" of the nanopub -> case-insensitive branches
  * a public key that is not a key    -> ValueError, raised OUTSIDE the try
  * a signature that is not base64    -> MalformedNanopubError (inside the try)
  * the signed assertion altered      -> still True: the original ignores the
    boolean PKCS1_v1_5.verify returns, and only an undecodable signature or
    key makes it fail.  Kept as a call because it is what the original does.

The decoys of the fixture carry the very same npx:has* predicates and
target OTHER nanopublications: a read on the wrong predicate, on the wrong
subject, or ignoring the target, gives a different outcome on at least one
call.  The Dataset is the default `Dataset()` (not `default_union`) as
nanopub builds it, with everything in named graphs.
"""
from pathlib import Path

from rdflib import Dataset, Literal, Namespace, URIRef

from rdfeval.harness import run_pair

HERE = Path(__file__).resolve().parent
NPX = Namespace("http://purl.org/nanopub/x/")
NP = "https://w3id.org/np/RA_dolDZ74j-ElpKlO72TF7xOEBRjUmxS4iREudSfrJk0"
EX = Namespace("http://example.org/")


def _ds():
    ds = Dataset()
    ds.parse(str(HERE / "fixture.trig"), format="trig")
    return ds


def _case(source_uri=NP, edit=None):
    def build():
        ds = _ds()
        if edit:
            edit(ds)
        return (ds, source_uri, Namespace(NP + "#")), {}
    return build


def _drop_signature(ds):
    for s, p, o, c in list(ds.quads((None, NPX.hasSignature, None, None))):
        if str(s).startswith(NP):
            ds.remove((s, p, o, c))


def _alter_assertion(ds):
    for s, p, o, c in list(ds.quads((EX.sensor1, EX.reads, None, None))):
        ds.remove((s, p, o, c))
        ds.add((s, p, Literal("99.9"), c))


def _drop_algorithm_of_main(ds):
    for s, p, o, c in list(ds.quads((None, NPX.hasAlgorithm, None, None))):
        if str(s).startswith(NP):
            ds.remove((s, p, o, c))


def _set_literal(predicate, value):
    def edit(ds):
        for s, p, o, c in list(ds.quads((None, predicate, None, None))):
            if str(s).startswith(NP):
                ds.remove((s, p, o, c))
                ds.add((s, p, Literal(value), c))
    return edit


def _set_algorithm(value):
    def edit(ds):
        for s, p, o, c in list(ds.quads((None, NPX.hasAlgorithm, None, None))):
            if str(s).startswith(NP):
                ds.remove((s, p, o, c))
                ds.add((s, p, Literal(value), c))
    return edit


VERDICT = run_pair(
    __file__,
    entry="verify_signature",
    calls=[
        _case(),                                             # valid signature
        _case("http://purl.org/nanopub/temp/nobody#"),       # no target
        _case(edit=_drop_signature),                         # no signature
        _case("http://purl.org/nanopub/temp/other#"),        # decoy: DSA
        _case("http://purl.org/nanopub/temp/other2#"),       # decoy: ECDSA
        _case("http://purl.org/nanopub/temp/other3#"),       # decoy: no algorithm
        _case("http://purl.org/nanopub/temp/other4#"),       # decoy: no signature
        _case(edit=_alter_assertion),                        # tampered
        _case(edit=_drop_algorithm_of_main),                 # IndexError
        _case(edit=_set_algorithm("dsa")),                   # case-insensitive DSA
        _case(edit=_set_algorithm("rsa")),                   # case-insensitive RSA
        _case(edit=_set_literal(NPX.hasPublicKey, "bm90LWEta2V5")),  # ValueError
        _case(edit=_set_literal(NPX.hasSignature, "QUJDRA=")),   # undecodable signature
    ],
)
