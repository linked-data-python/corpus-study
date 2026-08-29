# Extracted from w3c-cg/sstim@39360a81b8 : scripts/sstim-core-profile-contract.py
# region: check_core_fixture (lines 303-317, stratum remove)
# licence of the source repository: see meta.json
for label, subject, predicate, replacement in mutations:
    candidate = Graph()
    candidate += fixture
    candidate.remove((subject, predicate, None))
    if replacement is not None:
        candidate.add((subject, predicate, replacement))
    mutation_conforms, _, _ = shacl_validate(
        data_graph=candidate,
        shacl_graph=shapes,
        ont_graph=ontology,
        inference="none",
        advanced=False,
    )
    if mutation_conforms:
        errors.append(f"Core shapes accepted negative mutation: {label}")
