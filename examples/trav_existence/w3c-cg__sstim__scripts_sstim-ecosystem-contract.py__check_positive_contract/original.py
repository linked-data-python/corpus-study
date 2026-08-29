# Extracted from w3c-cg/sstim@39360a81b8 : scripts/sstim-ecosystem-contract.py
# region: check_positive_contract (lines 1136-1138, stratum trav_existence)
# licence of the source repository: see meta.json
PRIVATE_PREDICATES = {
    ECO.notificationChannel,
    ECO.responseNote,
    URIRef("http://xmlns.com/foaf/0.1/mbox"),
    SCHEMA.email,
    SCHEMA.telephone,
    SCHEMA.contactPoint,
    SCHEMA.identifier,
}

for predicate in PRIVATE_PREDICATES:
    require(not any(fixture.triples((None, predicate, None))),
            f"public fixture contains forbidden private predicate {predicate}", errors)
