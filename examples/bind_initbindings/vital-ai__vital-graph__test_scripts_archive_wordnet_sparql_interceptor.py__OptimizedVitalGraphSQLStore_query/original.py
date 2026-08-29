# Extracted from vital-ai/vital-graph@7fb3616c2d : test_scripts/archive/wordnet_sparql_interceptor.py
# region: OptimizedVitalGraphSQLStore.query (lines 106-139, stratum bind_initbindings)
# licence of the source repository: see meta.json
import time
import re
from rdflib import Graph, URIRef, Literal

def query(self, query_string, initNs=None, initBindings=None, queryGraph=None, DEBUG=False):
    """Override query method to intercept and optimize text searches"""
    self.query_optimizations['intercepted_queries'] += 1

    # Detect text search patterns
    text_search_info = self._detect_sparql_text_search(query_string)

    if text_search_info:
        print(f"🚀 INTERCEPTED TEXT SEARCH: {text_search_info}")
        self.query_optimizations['optimized_text_searches'] += 1

        # Extract LIMIT if present
        limit_match = re.search(r'LIMIT\s+(\d+)', query_string, re.IGNORECASE)
        limit = int(limit_match.group(1)) if limit_match else None

        # Execute optimized query
        start_time = time.time()
        results = self._execute_optimized_text_search(text_search_info, limit)
        elapsed = time.time() - start_time

        print(f"✅ OPTIMIZED QUERY: {len(results)} results in {elapsed:.3f} seconds")

        # Return results in SPARQL result format
        return self._format_sparql_results(results, text_search_info['variable'])

    else:
        print("⚪ NO TEXT SEARCH DETECTED - using standard SPARQL")
        self.query_optimizations['fallback_queries'] += 1
        # VitalGraphSQLStore doesn't have a query method, so we need to use a different approach
        # For now, let's create a basic Graph and use its query method
        from rdflib import Graph
        temp_graph = Graph()
        # This is a simplified fallback - in practice we'd need more sophisticated handling
        return temp_graph.query(query_string, initNs=initNs, initBindings=initBindings)
