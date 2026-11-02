# Extracted from openworm/owmeta-core@cd69d77ad0 : owmeta_core/data.py
# region: DataUser._reify (lines 309-318, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib.namespace import RDF, NamespaceManager

def _reify(self, g, s):
    """
    Add a statement object to g that binds to s
    """
    n = self.conf['new_graph_uri'](s)
    g.add((n, RDF['type'], RDF['Statement']))
    g.add((n, RDF['subject'], s[0]))
    g.add((n, RDF['predicate'], s[1]))
    g.add((n, RDF['object'], s[2]))
    return n
