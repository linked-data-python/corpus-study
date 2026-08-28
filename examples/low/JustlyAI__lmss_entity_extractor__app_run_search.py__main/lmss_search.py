# Context shim (see meta.json): reduced stand-in for app/lmss_search.py of
# JustlyAI/lmss_entity_extractor@6acc4d8389.
#
# Copied as-is: LMSSSearch.__init__ (which is where the rdflib work happens --
# it parses the turtle graph), _load_json, _filter_entities, _get_subclasses,
# and the shape of search().
# Reduced: the pydantic models become plain classes, and the
# sentence-transformers / fuzzywuzzy / numpy blend in _compute_score becomes a
# deterministic substring score, so the region runs with no ML dependency and
# no model download.  The reduction is in the *scoring*, which contains no RDF
# operation; it is used identically by both representations.
import json
from typing import Dict, List, Optional, Set

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDFS


class Entity:
    def __init__(self, rdf_about: str, rdfs_label: str, **rest):
        self.rdf_about = rdf_about
        self.rdfs_label = rdfs_label


class TopClass:
    def __init__(self, iri: str, label: str, entities_count: int):
        self.iri = iri
        self.label = label
        self.entities_count = entities_count


class LMSSSearch:
    def __init__(self, index_path: str, graph_path: str, top_classes_path: str):
        self.index = self._load_json(index_path, is_entity=True)
        self.graph = Graph()
        self.graph.parse(graph_path, format="turtle")
        self.top_classes = self._load_json(top_classes_path, is_entity=False)
        self.LMSS = Namespace("http://lmss.sali.org/")

    def _load_json(self, path: str, is_entity: bool) -> List:
        with open(path, "r") as f:
            data = json.load(f)
            if is_entity:
                return [Entity(**entity) for entity in data]
            else:
                return [TopClass(**top_class) for top_class in data]

    def _filter_entities(self, selected_branches: List[str]) -> Set[str]:
        filtered_entities = set()
        for branch in selected_branches:
            filtered_entities.add(branch)
            filtered_entities.update(self._get_subclasses(URIRef(branch)))
        return filtered_entities

    def _get_subclasses(self, class_iri: URIRef) -> Set[str]:
        subclasses = set()
        for s, p, o in self.graph.triples((None, RDFS.subClassOf, class_iri)):
            subclasses.add(str(s))
            subclasses.update(self._get_subclasses(s))
        return subclasses

    def search(self, query: str,
               selected_branches: Optional[List[str]] = None) -> List[Dict]:
        results = []

        if selected_branches:
            filtered_entities = self._filter_entities(selected_branches)
        else:
            filtered_entities = set(entity.rdf_about for entity in self.index)

        for entity in self.index:
            if entity.rdf_about not in filtered_entities:
                continue

            label = entity.rdfs_label
            score = self._compute_score(query, label)

            if score > 0:
                results.append(
                    {"iri": entity.rdf_about, "label": label, "score": score}
                )

        return sorted(results, key=lambda x: x["score"], reverse=True)[:10]

    @staticmethod
    def _compute_score(query: str, label: str) -> float:
        # stand-in for the regex/fuzzy/embedding blend of the upstream class
        q, lbl = query.lower(), label.lower()
        if q == lbl:
            return 1.0
        return 0.5 if q in lbl else 0.0

    def get_top_classes(self) -> List[TopClass]:
        return self.top_classes
