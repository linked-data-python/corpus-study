"""Validation driver for Nanopublication__nanopub-py__tests_test_fdo_nanopub.py__test_add_fdo_profile.

`test_add_fdo_profile` is a test: it returns nothing and changes nothing
when it passes, so a driver that only calls it with the two values of the
real `@pytest.mark.parametrize` shows nothing (a hollow green).  What the
region computes is its three ASSERTIONS, so the driver makes each of them
fail in turn and requires both sides to fail the same way.

The test builds a real `FdoNanopub` and calls the project's own
`add_fdo_profile`; the three asserts read what that method wrote (the
`dcterms:conformsTo` triple of the assertion graph, the `rdfs:label
"FdoProfile"` triple of the pubinfo graph, and the `npx:introduces` triple
of the pubinfo graph, checked by the helper).  Each call's factory runs in
the side's own process, just before the call, and installs a variant of
`FdoNanopub.add_fdo_profile` (identical on both sides; the class is the one
both modules import).  This departs from the original, which only ever runs
the project method, and the departure is justified by the fact that the
original shows nothing otherwise.

CALLS (the first two are the real parametrization, assertions pass;
a raise is compared by type and message, an AssertionError has none):
  0. the bare handle string                                    all pass
  1. the `hdl:` URIRef form                                    all pass
  2. add_fdo_profile writes nothing                            assert 1 fails
  3. conformsTo points at a neighbouring handle                assert 1 fails
  4. conformsTo is replaced by another dcterms predicate       assert 1 fails
  5. conformsTo is written on another subject                  assert 1 fails
  6. the label triple is missing                               assert 2 fails
  7. the label carries a language tag (not the plain literal)  assert 2 fails
  8. the label is on another handle                            assert 2 fails
  9. the label has another text                               assert 2 fails
 10. npx:introduces is missing from the pubinfo                assert 3 fails
 11. npx:introduces points at another object                   assert 3 fails
 12. the profile is a full http URL string (`to_hdl_uri` keeps it) and passes
"""
from rdflib import DCTERMS, Literal, RDFS, URIRef

from nanopub.constants import FDO_DATA_REF_HANDLE, FDO_PROFILE_HANDLE
from nanopub.fdo.fdo_nanopub import FdoNanopub, to_hdl_uri
from nanopub.namespaces import HDL, NPX
from rdfeval.harness import run_pair

FAKE_HANDLE = "21.T11966/test"
_GENUINE = FdoNanopub.add_fdo_profile


def _variant(mode):
    def add_fdo_profile(self, profile_uri):
        if mode == "nothing":
            return
        _GENUINE(self, profile_uri)
        uri = to_hdl_uri(profile_uri)
        label = (HDL[FDO_PROFILE_HANDLE], RDFS.label, Literal("FdoProfile"))
        intro = (self.metadata.np_uri, NPX.introduces, self.fdo_uri)
        conf = (self.fdo_uri, DCTERMS.conformsTo, uri)
        if mode == "neighbour_object":
            self.assertion.remove(conf)
            self.assertion.add((conf[0], conf[1], HDL["21.T11966/other"]))
        elif mode == "other_predicate":
            self.assertion.remove(conf)
            self.assertion.add((conf[0], DCTERMS.references, uri))
        elif mode == "other_subject":
            self.assertion.remove(conf)
            self.assertion.add((HDL["21.T11966/someone"], conf[1], uri))
        elif mode == "no_label":
            self.pubinfo.remove(label)
        elif mode == "lang_label":
            self.pubinfo.remove(label)
            self.pubinfo.add((label[0], label[1], Literal("FdoProfile", lang="en")))
        elif mode == "label_other_handle":
            self.pubinfo.remove(label)
            self.pubinfo.add((HDL[FDO_DATA_REF_HANDLE], label[1], label[2]))
        elif mode == "label_other_text":
            self.pubinfo.remove(label)
            self.pubinfo.add((label[0], label[1], Literal("Profile")))
        elif mode == "no_introduces":
            self.pubinfo.remove(intro)
        elif mode == "introduces_other":
            self.pubinfo.remove(intro)
            self.pubinfo.add((intro[0], intro[1], HDL["21.T11966/other"]))
    return add_fdo_profile


def _call(mode, profile):
    def make():
        FdoNanopub.add_fdo_profile = _GENUINE if mode is None else _variant(mode)
        return (profile,), {}
    return make


VERDICT = run_pair(
    __file__,
    entry='test_add_fdo_profile',
    calls=[
        _call(None, FAKE_HANDLE),
        _call(None, HDL[FAKE_HANDLE]),
        _call("nothing", FAKE_HANDLE),
        _call("neighbour_object", FAKE_HANDLE),
        _call("other_predicate", HDL[FAKE_HANDLE]),
        _call("other_subject", FAKE_HANDLE),
        _call("no_label", FAKE_HANDLE),
        _call("lang_label", HDL[FAKE_HANDLE]),
        _call("label_other_handle", FAKE_HANDLE),
        _call("label_other_text", FAKE_HANDLE),
        _call("no_introduces", FAKE_HANDLE),
        _call("introduces_other", HDL[FAKE_HANDLE]),
        _call(None, "https://example.org/profiles/p1"),
    ],
)
