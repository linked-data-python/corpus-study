# Extracted from SynBioDex/sbol_factory@5d01ec7f4c : sbol_factory/query.py
# region: Query.query_cardinality (lines 224-245, stratum sparql_interpolated)
# licence of the source repository: see meta.json
from math import inf

def query_cardinality(self, property_uri, class_uri):
    lower_bound = 0
    upper_bound = inf
    query = '''
        SELECT distinct ?cardinality
        WHERE 
        {{{{
            <{}> rdfs:subClassOf ?restriction .
            ?restriction rdf:type owl:Restriction .
            ?restriction owl:onProperty <{}> .
            ?restriction {{}} ?cardinality .
        }}}}
        '''.format(class_uri, property_uri)
    response = self.graph.query(query.format('owl:minCardinality'))
    response = [str(row[0]) for row in response]
    if len(response):
        lower_bound = int(response[0])
    response = self.graph.query(query.format('owl:maxCardinality'))
    response = [str(row[0]) for row in response]
    if len(response):
        upper_bound = int(response[0])
    return (lower_bound, upper_bound)
