# Extracted from vital-ai/vital-graph@7fb3616c2d : vitalgraph/kg_impl/kg_backend_utils.py
# region: FusekiPostgreSQLBackendAdapter._sparql_results_to_objects (lines 481-560, stratum coercion_datatype)
# licence of the source repository: see meta.json
from typing import List, Dict, Any, Optional, Tuple, Union, cast
from vital_ai_vitalsigns.model.GraphObject import GraphObject

async def _sparql_results_to_objects(self, sparql_result: List[Dict], single_uri: Optional[str] = None) -> List[GraphObject]:
    """Convert SPARQL query results (SPARQL JSON bindings) back to VitalSigns objects."""
    try:
        from vital_ai_vitalsigns.vitalsigns import VitalSigns

        if not sparql_result:
            return []

        # Use VitalSigns to convert SPARQL results directly
        vs = VitalSigns()

        # Convert SPARQL results to RDF triples format for VitalSigns
        from rdflib import URIRef, Literal

        triples = []
        for binding in sparql_result:
            # Handle SPARQL JSON binding format
            if 's' in binding:  # Graph query with subject
                subject = str(binding['s'].get('value'))  # Cast to string to handle CombinedProperty
                predicate = str(binding['p'].get('value'))  # Cast to string to handle CombinedProperty
                obj_data = binding['o']
            else:  # Single entity query
                subject = str(single_uri) if single_uri else None  # Cast to string to handle CombinedProperty
                predicate = str(binding['p'].get('value'))  # Cast to string to handle CombinedProperty
                obj_data = binding['o']

            if not subject:
                continue

            # Create RDF triple tuple using rdflib types (as VitalSigns expects)
            subject_ref = URIRef(subject)
            predicate_ref = URIRef(predicate)

            # Handle object based on type
            if obj_data.get('type') == 'uri':
                object_ref = URIRef(str(obj_data.get('value')))  # Cast to string to handle CombinedProperty
            else:
                # Literal value
                object_ref = Literal(str(obj_data.get('value')))  # Cast to string to handle CombinedProperty

            triple = (subject_ref, predicate_ref, object_ref)
            triples.append(triple)

        if not triples:
            return []

        # Group triples by subject URI to create separate objects
        from collections import defaultdict
        subject_triples = defaultdict(list)

        for triple in triples:
            subject_uri = str(triple[0])  # Convert URIRef to string
            subject_triples[subject_uri].append(triple)

        # Convert each subject's triples to a VitalSigns object
        objects = []
        for subject_uri, subject_triple_list in subject_triples.items():
            try:
                def triple_generator():
                    for triple in subject_triple_list:
                        yield triple

                # VitalSigns from_triples returns a single object
                obj = vs.from_triples(triple_generator())
                if obj:
                    objects.append(obj)

            except Exception as e:
                self.logger.warning(f"Failed to convert triples for subject {subject_uri}: {e}")
                continue

        self.logger.debug(f"🔍 Converted {len(triples)} triples into {len(objects)} VitalSigns objects")
        return objects

    except Exception as e:
        import traceback
        self.logger.error(f"Error converting SPARQL results to objects: {e}")
        self.logger.error("FULL TRACEBACK WITH LINE NUMBERS:")
        self.logger.error(traceback.format_exc())
        return []
