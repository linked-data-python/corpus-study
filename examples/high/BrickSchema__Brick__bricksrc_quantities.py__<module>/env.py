# Context shim (see meta.json): stand-in for bricksrc/env.py, which is
#     from ontoenv import OntoEnv
#     env = OntoEnv(search_directories=[...], strict=False, offline=True, ...)
# ontoenv is not installable here and env.import_graph() would pull the QUDT
# 3.3.0 unit and quantitykind vocabularies over the network.  The region only
# uses `g` through get_units()/all_units(), which it never calls, so a no-op
# import keeps module execution faithful.  Identical for both representations.


class _Env:
    def import_graph(self, graph, uri):
        """No-op stand-in for ontoenv.OntoEnv.import_graph."""
        return graph


env = _Env()
