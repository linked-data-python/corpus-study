"""Validation driver for FAIRDataTeam__fdpneo-server__src_fdpneo_server_metadata_profiles_applier.py___repository_graph.

`_repository_graph` returns a plain `Graph`, so the oracle is a direct
isomorphism comparison of that return value -- no wrapper harness needed.

Three calls: `rights_iri=None` (the guarded third triple must be ABSENT --
this is the case the stratum's boundary matters: the first two triples share
`subject` and merge with `;`, but the third does not join them because it is
conditional, not because it has a different subject), `rights_iri` given (the
third triple present), and `search_enabled=False` (drops the search-API
triples inside `_service_advertisement`, exercised as a control since that
loop stays untouched rdflib in the translation -- see meta.json).
"""
from rdfeval.harness import run_pair


def case(**kwargs):
    defaults = dict(
        iri="https://fdp.example.org/",
        type_iri="https://w3id.org/fdp/o#FAIRDataPoint",
        member_relations=[
            "https://w3id.org/fdp/o#servesMetadata",
            "http://www.w3.org/ns/dcat#dataset",
        ],
        title="Example FAIR Data Point",
        rights_iri=None,
        search_enabled=True,
    )
    defaults.update(kwargs)
    return ((), defaults)


VERDICT = run_pair(
    __file__,
    entry="_repository_graph",
    calls=[
        case(),
        case(rights_iri="https://creativecommons.org/publicdomain/zero/1.0/"),
        case(rights_iri="https://creativecommons.org/publicdomain/zero/1.0/",
             search_enabled=False),
    ],
)
