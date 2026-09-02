#!/usr/bin/env python3
"""enrichment_n_v6_0_0.py — relationship-completeness fix and syntactic/
semantic/behavioral relation typing, commissioned 2026-08-06.

Verbatim copy (see this region's meta.json / context_predecl.py) of the file
altunelyusuf/SemanticTechnologies@bad0fa7c46's build_core_v6_3_0.py loads via
`en = load("enrichment_n", "v6_0_0")`. Only NEW_RELATIONS is read by this
region; REL_TYPE is kept too since it is part of the same source file and
costs nothing to keep verbatim.
"""

NEW_RELATIONS = [
 ("T6C4", "stewardedBy", "T10C5"),   # LLM-assisted ontology engineering research is stewarded by academic venues
 ("T3C3", "buildsOn", "T1C6"),       # data fabric / metadata activation builds on semantic virtualization
 ("T3C5", "buildsOn", "T3C3"),       # master data / PIM semantics builds on data-fabric metadata activation
 ("T4C4", "buildsOn", "T4C1"),       # retail/fashion adoption builds on broader tech-sector adoption precedent
 ("T4C3", "informs", "T4C2"),        # manufacturing compliance adoption informs finance/life-sciences adoption
 ("T5C3", "buildsOn", "T5C5"),       # semantic layer platforms build on (often acquire) emerging-vendor innovation
 ("T3C1", "informs", "T6C3"),        # enterprise knowledge graph practice informs design-pattern catalogs
 ("T6C2", "implementedBy", "T9C3"),  # QA techniques are implemented via visualization/documentation tooling
]

REL_TYPE = {
 "standardizedBy": "syntactic",
 "buildsOn": "semantic", "governedBy": "semantic", "informs": "semantic",
 "implementedBy": "behavioral", "stewardedBy": "behavioral",
}
