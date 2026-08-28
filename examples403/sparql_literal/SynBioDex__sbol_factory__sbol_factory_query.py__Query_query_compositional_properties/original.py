# Extracted from SynBioDex/sbol_factory@5d01ec7f4c : sbol_factory/query.py
# region: Query.query_compositional_properties (lines 165-194, stratum sparql_literal)
# licence of the source repository: see meta.json
def query_compositional_properties(self, class_uri):
    query = '''
        SELECT distinct ?property_uri
        WHERE 
        {{
            ?property_uri rdf:type owl:ObjectProperty .
            ?property_uri rdfs:subPropertyOf sbol:directlyComprises .
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
            ?property_uri rdf:type owl:ObjectProperty .
            ?property_uri rdfs:subPropertyOf sbol:directlyComprises .
            <{}> rdfs:subClassOf ?restriction .
            ?restriction owl:onProperty ?property_uri .
        }}
        '''.format(class_uri)
    response = self.graph.query(query)
    response = [str(row[0]) for row in response]
    property_types.extend(response) 
    return list(set(property_types))
