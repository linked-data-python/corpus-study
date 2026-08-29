# Extracted from stevereiner/flexible-graphrag@7d885d5379 : flexible-graphrag/rdf/ontology_manager.py
# region: OntologyManager.get_xsd_type_map (lines 389-443, stratum sparql_literal)
# licence of the source repository: see meta.json
from typing import Dict, List, Set, Literal, Optional

def get_xsd_type_map(self) -> Dict[str, str]:
    """Return a prop_name -> XSD datatype URI dict for all datatype properties.

    Used by KGToRDFConverter._make_literal() / _turtle_literal() to emit
    correctly typed literals (e.g. "2008-09-10"^^xsd:date) instead of
    always falling back to xsd:string.

    Keys are the uppercased local names of OWL DatatypeProperties.
    Values are full XSD datatype URI strings.

    Example:
        {
          "SALARY":     "http://www.w3.org/2001/XMLSchema#decimal",
          "HIRE_DATE":  "http://www.w3.org/2001/XMLSchema#date",
          "AGE":        "http://www.w3.org/2001/XMLSchema#integer",
          "IS_ACTIVE":  "http://www.w3.org/2001/XMLSchema#boolean",
        }
    """
    _PY_TO_XSD = {
        "float":   "http://www.w3.org/2001/XMLSchema#decimal",
        "int":     "http://www.w3.org/2001/XMLSchema#integer",
        "bool":    "http://www.w3.org/2001/XMLSchema#boolean",
        "string":  "http://www.w3.org/2001/XMLSchema#string",
        "str":     "http://www.w3.org/2001/XMLSchema#string",
    }
    xsd_map: Dict[str, str] = {}
    # Primary source: rdfs:range declared on owl:DatatypeProperty in the ontology graph.
    # This is authoritative and covers relation-property annotations (e.g. assignment_percentage)
    # that are not inside any entity/relation .properties dict.
    if self.graph is not None:
        datatype_range_query = """
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT DISTINCT ?prop ?range WHERE {
            ?prop a owl:DatatypeProperty .
            OPTIONAL { ?prop rdfs:range ?range . }
        }
        """
        for row in self.graph.query(datatype_range_query):
            name = self._uri_to_name(row.prop)
            if name:
                range_uri = str(row.range) if row.range else "http://www.w3.org/2001/XMLSchema#string"
                xsd_map[name] = range_uri
    # Fallback / override: YAML-style entity/relation .properties dicts (Python type names).
    for entity in self.entities.values():
        for prop_name, prop_type in (entity.properties or {}).items():
            key = prop_name.upper()
            if key not in xsd_map:
                xsd_map[key] = _PY_TO_XSD.get(prop_type, "http://www.w3.org/2001/XMLSchema#string")
    for relation in self.relations.values():
        for prop_name, prop_type in (relation.properties or {}).items():
            key = prop_name.upper()
            if key not in xsd_map:
                xsd_map[key] = _PY_TO_XSD.get(prop_type, "http://www.w3.org/2001/XMLSchema#string")
    return xsd_map
