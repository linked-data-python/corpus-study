# -*- coding: utf-8 -*-
# Stand-in for landscape/07-tooling/taxonomy_v1_0_0.py of
# altunelyusuf/SemanticTechnologies@bad0fa7c46: the real module holds the
# 59-node taxonomy TAX (plus the citation registry C); this one keeps its
# shape -- a list of top nodes, each with "id", "label" and "children" -- for
# six nodes, enough for the region's reads.
C = {}
TAX = [
 {"id": "T1", "label": "Semantic Technology Foundations", "children": [
   {"id": "T1C1", "label": "Knowledge Representation Models", "children": []},
   {"id": "T1C2", "label": "Ontology and Schema Languages", "children": []}]},
 {"id": "T2", "label": "Standards Chapter", "children": [
   {"id": "T2C1", "label": "W3C Standards", "children": []}]},
 {"id": "T3", "label": "Ecosystem", "children": []},
]
