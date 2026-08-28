# Extracted from Nanopublication/nanopub-py@05022dc4bc : nanopub/templates/nanopub_claim.py
# region: NanopubClaim.__init__ (lines 22-44, band high)
# licence of the source repository: see meta.json
from copy import deepcopy
from rdflib import RDF, RDFS, Literal, URIRef
from nanopub_context import HYCL
from nanopub_context import NanopubConf
from nanopub_context import ProfileError
from nanopub_context import super

def __init__(
    self,
    claim: str,
    conf: NanopubConf,
) -> None:
    conf = deepcopy(conf)
    conf.add_prov_generated_time = True
    conf.add_pubinfo_generated_time = True
    conf.attribute_publication_to_profile = True
    super().__init__(
        conf=conf,
    )

    if not self.profile:
        raise ProfileError("No profile provided, cannot generate a Nanopub Claim")

    this_statement = self._metadata.namespace.claim
    # this_statement = BNode("mystatement")
    self.assertion.add((this_statement, RDF.type, HYCL.Statement))
    self.assertion.add((this_statement, RDFS.label, Literal(claim)))

    orcid_id_uri = URIRef(self.profile.agent_id)
    self.provenance.add((orcid_id_uri, HYCL.claims, this_statement))
