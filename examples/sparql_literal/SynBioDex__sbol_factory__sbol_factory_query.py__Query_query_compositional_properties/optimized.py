# Extracted from SynBioDex/sbol_factory@5d01ec7f4c : sbol_factory/query.py
# region: Query.query_compositional_properties (lines 165-194, stratum sparql_literal)
# licence of the source repository: see meta.json
def query_compositional_properties(self, class_uri):
    # The type of inherited properties are sometimes overridden
    response = self.graph.query('''
        SELECT ?property_uri
        WHERE {{
            ?property_uri rdf:type owl:ObjectProperty ;
                rdfs:subPropertyOf sbol:directlyComprises .
            {{ ?property_uri rdfs:domain/(owl:unionOf/rdf:rest*/rdf:first)* <{0}> }}
            UNION {{ <{0}> rdfs:subClassOf/owl:onProperty ?property_uri }}
        }}
        '''.format(class_uri))
    return list({str(row[0]) for row in response})
