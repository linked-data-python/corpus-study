# Extracted from RDFLib/VocPrez@ce3c0ea42f : vocprez/source/file.py
# region: File.get_top_concepts (lines 386-461, stratum sparql_literal)
# licence of the source repository: see meta.json
#
# `g.VOCABS[self.vocab_id]` reads Flask's per-request `g` proxy (the real
# app populates VOCABS once at start-up; `g` has been bound to the
# *application* context, not the request, since Flask 0.10). driver.py
# pushes one minimal Flask app's context before calling this function, so
# `g.VOCABS[...]` resolves the same way without a real HTTP request --
# no change needed here, this file is otherwise unmodified from the source.
from flask import g, url_for

def get_top_concepts(self):
    # same as parent query, only running against rdflib in-memory graph, not SPARQL endpoint
    vocab = g.VOCABS[self.vocab_id]
    q = """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT DISTINCT ?tc ?pl
        WHERE {{
            {{
                <{concept_scheme_uri}> skos:hasTopConcept ?tc .                
            }}
            UNION 
            {{
                ?tc skos:topConceptOf <{concept_scheme_uri}> .
            }}
            {{ ?tc skos:prefLabel ?pl .
                FILTER(lang(?pl) = "{language}" || lang(?pl) = "")
            }}
        }}
        ORDER BY ?pl
        """.format(
        concept_scheme_uri=vocab.uri, language=self.language
    )
    top_concepts = self.gr.query(q)

    if top_concepts is not None:
        # cache prefLabels and do not add duplicates. This prevents Concepts with sameAs properties appearing twice
        pl_cache = []
        tcs = []
        for tc in top_concepts:
            if tc[1] not in pl_cache:  # only add if not already in cache
                tcs.append((tc[0], tc[1]))
                pl_cache.append(tc[1])

        if len(tcs) == 0:
            q = """
                PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                SELECT DISTINCT ?tc ?pl
                WHERE {{
                    {{ GRAPH ?g {{
                        {{
                            <{concept_scheme_uri}> skos:hasTopConcept ?tc .                
                        }}
                        UNION 
                        {{
                            ?tc skos:inScheme <{concept_scheme_uri}> .
                        }}
                        {{ ?tc skos:prefLabel ?pl .
                            FILTER(lang(?pl) = "{language}" || lang(?pl) = "") 
                        }}
                    }} }}
                    UNION
                    {{
                        {{
                            <{concept_scheme_uri}> skos:hasTopConcept ?tc .                
                        }}
                        UNION 
                        {{
                            ?tc skos:inScheme <{concept_scheme_uri}> .
                        }}
                        {{ ?tc skos:prefLabel ?pl .
                            FILTER(lang(?pl) = "{language}" || lang(?pl) = "")
                        }}
                    }}
                }}
                ORDER BY ?pl
                """.format(
                concept_scheme_uri=vocab.uri, language=self.language
            )
            for tc in self.gr.query(q):
                if tc[1] not in pl_cache:  # only add if not already in cache
                    tcs.append((tc[0], tc[1]))
                    pl_cache.append(tc[1])

        return tcs
    else:
        return None
