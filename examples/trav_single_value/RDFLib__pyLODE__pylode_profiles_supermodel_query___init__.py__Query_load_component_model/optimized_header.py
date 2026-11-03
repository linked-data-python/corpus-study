# Extracted from RDFLib/pyLODE@0d0471fb99 : pylode/profiles/supermodel/query/__init__.py
# region: Query.load_component_model (lines 701-750, stratum trav_single_value)
# licence of the source repository: see meta.json
from collections import defaultdict
from rdflib import OWL, SH, Dataset, URIRef
from pylode.profiles.supermodel.model import CodedProperty, ComponentModel, SimpleCodedProperty
from pylode.profiles.supermodel.query.common import get_descriptions, get_name
# Context: module-level helpers the region calls, defined next to it in the
# same module (query/__init__.py); from the real package (pylode 3.2.3).
from pylode.profiles.supermodel.query import (
    get_component_model_ignored_classes,
    get_examples,
    get_rdf_properties,
    get_top_level_component_classes,
)

def load_component_model(self, iri: URIRef, db: Dataset) -> ComponentModel:
    name = get_name(iri, db)
    descriptions = get_descriptions(iri, db)
    ignored_classes = get_component_model_ignored_classes(iri, db)
    profile_graph = db.get_graph(iri)
    classes = self.get_component_model_classes(profile_graph, ignored_classes)
    order = db.value(iri, SH.order)

    coded_properties = defaultdict(list)
    for cls in classes:
        for properties in cls.properties.values():
            for prop in properties:
                if isinstance(prop, CodedProperty):
                    # Always get the base name, that's why we use properties[-1].name.
                    _prop = SimpleCodedProperty(
                        prop.iri, properties[-1].name, prop.description, prop.codelist
                    )
                    if _prop.codelist and _prop not in coded_properties[prop.iri]:
                        coded_properties[prop.iri].append(_prop)

    return ComponentModel(
        iri,
        name,
        coded_properties,
        descriptions,
        classes,
        get_top_level_component_classes(classes),
        get_examples(iri, db),
        int(order) if order is not None else None,
        ignored_classes,
        get_rdf_properties(OWL.AnnotationProperty, profile_graph, db),
        get_rdf_properties(OWL.DatatypeProperty, profile_graph, db),
        get_rdf_properties(OWL.ObjectProperty, profile_graph, db),
        get_rdf_properties(OWL.OntologyProperty, profile_graph, db),
    )
