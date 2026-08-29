# Extracted from SynBioDex/sbol_factory@5d01ec7f4c : sbol_factory/query.py
# region: Query.query_datatype_properties (lines 196-222, stratum sparql_literal)
# licence of the source repository: see meta.json
def query_datatype_properties(self, class_uri):
    query =     '''
        SELECT distinct ?property_uri
        WHERE 
        {{
            ?property_uri rdf:type owl:DatatypeProperty .
            ?property_uri rdfs:domain/(owl:unionOf/rdf:rest*/rdf:first)* <{}>.
        }}
        '''.format(class_uri)
    response = self.graph.query(query)
    response = [str(row[0]) for row in response]
    property_types = response

    # The type of inherited properties are sometimes overridden 
    query = '''
        SELECT distinct ?property_uri
        WHERE 
        {{
            ?property_uri rdf:type owl:DatatypeProperty .
            <{}> rdfs:subClassOf ?restriction .
            ?restriction owl:onProperty ?property_uri .
        }}
        '''.format(class_uri) 
    response = self.graph.query(query)
    response = [str(row[0]) for row in response]
    property_types.extend(response)
    return list(set(property_types))
