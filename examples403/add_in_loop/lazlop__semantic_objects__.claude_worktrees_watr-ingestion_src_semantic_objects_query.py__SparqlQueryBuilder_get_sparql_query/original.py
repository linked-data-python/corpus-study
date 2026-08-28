# Extracted from lazlop/semantic_objects@243c5efd8c : .claude/worktrees/watr-ingestion/src/semantic_objects/query.py
# region: SparqlQueryBuilder.get_sparql_query (lines 107-206, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, Literal, RDF
from typing import Type, get_origin, get_args
from dataclasses import _MISSING_TYPE, field

def get_sparql_query(self, ontology=None):
    """
    Generate a SPARQL query from the resource class definition.

    Args:
        ontology: Optional ontology identifier (e.g., 's223') for special handling

    Returns:
        A SPARQL query string that can be used to query for instances of this class
    """
    seen_fields = set()
    exact_value_constraints = []  # Track fields with exact_values metadata

    for base in self.resource_class.__mro__:
        if hasattr(base, '__dataclass_fields__'):
            for field_name, field_obj in base.__dataclass_fields__.items():
                # Skip fields with init=False and templatize=False
                if (field_obj.init == False and 
                    field_obj.metadata.get('templatize', True) == False):
                    continue
                if field_name in seen_fields:
                    continue
                seen_fields.add(field_name)

                relation = self.resource_class._infer_relation_for_field(field_name, field_obj)

                # Check for exact_values metadata
                exact_values = field_obj.metadata.get('exact_values')
                if exact_values is not None:
                    # Store for later processing
                    exact_value_constraints.append((field_name, relation, exact_values))
                    continue  # Don't add regular triple for exact_values fields

                fixed_value = self.resource_class._resolve_fixed_default(field_obj)
                if not isinstance(fixed_value, _MISSING_TYPE) and fixed_value is not None:
                    self.graph.add((PARAM['name'], relation._get_iri(), fixed_value._get_iri()))
                elif isinstance(fixed_value, _MISSING_TYPE):
                    self.graph.add((PARAM['name'], relation._get_iri(), PARAM[field_name]))

                    # Add type triple for Resource subclass dependencies
                    field_type = field_obj.type
                    # Handle Optional, List, etc. - extract the actual type
                    origin = get_origin(field_type)
                    if origin is not None:
                        args = get_args(field_type)
                        if args:
                            field_type = args[0]

                    # Check if the field type is a subclass of Resource
                    if (hasattr(field_type, '__mro__') and 
                        any(base.__name__ == 'Resource' for base in field_type.__mro__)):
                        # Check if this class has a _semantic_type attribute
                        # This allows classes to specify which parent type should be used in the semantic model
                        if hasattr(field_type, '_semantic_type') and field_type._semantic_type is not None:
                            semantic_type = field_type._semantic_type
                            # Use the semantic type for the RDF type triple
                            self.graph.add((PARAM[field_name], RDF.type, semantic_type._get_iri()))

                            # Add triples for any class-level fields (fields with init=False and a fixed value)
                            if hasattr(field_type, '__dataclass_fields__'):
                                for class_field_name, class_field_obj in field_type.__dataclass_fields__.items():
                                    # Check if this is a class-level field (init=False with a fixed value)
                                    if class_field_obj.init:
                                        continue
                                    class_field_value = field_type._resolve_fixed_default(class_field_obj)
                                    if isinstance(class_field_value, _MISSING_TYPE) or class_field_value is None:
                                        continue
                                    # Infer the relation for this class-level field
                                    try:
                                        class_field_relation = field_type._infer_relation_for_field(class_field_name, class_field_obj)
                                        # Add triple for this class-level constraint
                                        if hasattr(class_field_value, '_get_iri'):
                                            self.graph.add((PARAM[field_name], class_field_relation._get_iri(), class_field_value._get_iri()))
                                    except (ValueError, AttributeError):
                                        # If we can't infer the relation or get the value, skip it
                                        pass
                        else:
                            # Add type triple for this dependency using the field type itself
                            self.graph.add((PARAM[field_name], RDF.type, field_type._get_iri()))

    # Now bind the prefixes we need by calling convert_to_prefixed on each URI
    # This will cause RDFLib to automatically bind the necessary namespaces
    for s, p, o in self.graph.triples((None, None, None)):
        for node in [s, p, o]:
            if isinstance(node, URIRef):
                # This call will bind the namespace if needed
                try:
                    self.graph.compute_qname(node)
                except:
                    pass

    # Generate the base query
    query = self._get_query(self.graph, ontology)

    # Add exact_values constraints if any
    if exact_value_constraints:
        # Parse the query to insert the exact value filters
        query = self._add_exact_values_to_query(query, exact_value_constraints)

    return query
