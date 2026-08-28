"""Context shim for this example, imported identically by both sides.

The region's ``from tests.conftest import ...`` cannot run offline: the real
conftest imports ``nanopub_testsuite_connector`` and downloads the nanopub
test suite to obtain a signing key.  This shim rebuilds the three bindings the
region actually uses, with a signing key generated locally at import time (one
module instance is shared by original.py and translated.ldpy, so both sides
sign with the same key).

  * ``profile_test`` / ``default_conf``
        copied from Nanopublication/nanopub-py@05022dc4bc tests/conftest.py
        (same NanopubConf flags, same agent id and name)
  * ``_minimal_valid_nanopub``
        copied verbatim from tests/test_nanopub.py lines 763-773
"""
from base64 import b64encode

from Crypto.PublicKey import RSA
from rdflib import URIRef, Literal, DC, PROV

from nanopub import Nanopub, NanopubConf, namespaces
from nanopub.profile import Profile

_key = RSA.generate(2048)

profile_test = Profile(
    agent_id="https://orcid.org/0000-0000-0000-0000",
    name="Python Tests",
    private_key=b64encode(_key.export_key("DER")).decode(),
    public_key=b64encode(_key.publickey().export_key("DER")).decode(),
    introduction_nanopub_uri=None,
)

default_conf = NanopubConf(
    profile=profile_test,
    use_test_server=True,
    add_prov_generated_time=False,
    add_pubinfo_generated_time=False,
    attribute_assertion_to_profile=True,
    attribute_publication_to_profile=True,
    assertion_attributed_to=None,
    publication_attributed_to=None,
    derived_from=None,
)


def _minimal_valid_nanopub(conf=None) -> Nanopub:
    """A nanopub with the bare minimum needed to pass ``is_valid``."""
    np = Nanopub(conf=conf if conf is not None else NanopubConf())
    np.assertion.add(
        (URIRef("http://test"), namespaces.HYCL.claims, Literal("test claim"))
    )
    np.provenance.add(
        (np.assertion.identifier, PROV.wasAttributedTo, URIRef("http://someone"))
    )
    np.pubinfo.add((np._metadata.namespace[""], DC.creator, Literal("tester")))
    return np
