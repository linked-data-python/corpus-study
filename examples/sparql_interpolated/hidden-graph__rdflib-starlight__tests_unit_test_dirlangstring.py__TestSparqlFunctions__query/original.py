# Extracted from hidden-graph/rdflib-starlight@b7973da2b5 : tests/unit/test_dirlangstring.py
# region: TestSparqlFunctions._query (lines 272-274, stratum sparql_interpolated)
# licence of the source repository: see meta.json
EX = 'http://example.org/'

def _query(self, g, expr):
    r = g.query(f'SELECT ?s ({expr} AS ?v) WHERE {{ ?s <{EX}title> ?t }}')
    return {row[r.vars[0]]: row[r.vars[1]] for row in r.bindings}
