# Extracted from realfagstermer/realfagstermer@58180037de : dodo.py
# region: task_stats.stats_from_graph (lines 518-566, stratum sparql_interpolated)
# licence of the source repository: see meta.json
for facetName, facet in facets.items():

    vals = g.query(u"""PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX ubo: <http://data.ub.uio.no/onto#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>

    SELECT (COUNT(DISTINCT ?s) AS ?c)
    WHERE {
      ?s a ubo:%s .
      FILTER NOT EXISTS { ?s owl:deprecated true } .
    }""" % (facetName)).bindings[0].values()
    facets[facetName]['concepts'] = int(list(vals)[0].value)

    sumConceptsWithStrings += facets[facetName]['concepts']

    if facetName != 'ComplexConcept' and facetName != 'VirtualComplexConcept':
        sumConcepts += facets[facetName]['concepts']

    facets[facetName]['terms'] = 0

    for langName in facet['prefLabels'].keys():

        vals = g.query(u"""PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX ubo: <http://data.ub.uio.no/onto#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>

        SELECT (COUNT(DISTINCT ?o) AS ?c)
        WHERE {
          ?s a ubo:%s .
          ?s skos:prefLabel ?o .
          FILTER(langMatches(lang(?o), "%s"))
          FILTER NOT EXISTS { ?s owl:deprecated true } .
        }""" % (facetName, langName)).bindings[0].values()
        facets[facetName]['prefLabels'][langName] = int(list(vals)[0].value)

        vals = g.query(u"""PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX ubo: <http://data.ub.uio.no/onto#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>

        SELECT (COUNT(DISTINCT ?o) AS ?c)
        WHERE {
          ?s a ubo:%s .
          ?s skos:altLabel ?o .
          FILTER(langMatches(lang(?o), "%s"))
          FILTER NOT EXISTS { ?s owl:deprecated true } .
        }""" % (facetName, langName)).bindings[0].values()
        facets[facetName]['altLabels'][langName] = int(list(vals)[0].value)

        facets[facetName]['terms'] += facets[facetName]['prefLabels'][langName] + facets[facetName]['altLabels'][langName]
