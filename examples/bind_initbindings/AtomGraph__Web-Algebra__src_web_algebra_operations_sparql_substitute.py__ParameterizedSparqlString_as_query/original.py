# Extracted from AtomGraph/Web-Algebra@128e184aa8 : src/web_algebra/operations/sparql/substitute.py
# region: ParameterizedSparqlString.as_query (lines 225-227, stratum bind_initbindings)
# licence of the source repository: see meta.json
from rdflib.plugins.sparql import prepareQuery

def as_query(self):
    """Parses the SPARQL string into a prepared query."""
    return prepareQuery(self.to_string(), initNs=self.prefixes)
