# Extracted from ktbs/ktbs@4f9f50c770 : lib/ktbs/api/base.py
# region: <module> (lines 414-419, stratum sparql_literal)
# licence of the source repository: see meta.json
from rdflib.plugins.sparql.processor import prepareQuery

_ITER_CONTAINED_QUERY = prepareQuery("""
    PREFIX k: <http://liris.cnrs.fr/silex/2009/ktbs#>
    SELECT DISTINCT ?s ?t
      $base # selected solely to please Virtuoso
    WHERE { $base k:contains ?s . ?s a ?t . }
""")
