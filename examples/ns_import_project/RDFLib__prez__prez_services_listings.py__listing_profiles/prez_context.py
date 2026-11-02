# Context shim (see meta.json): makes the imports of prez/services/listings.py
# resolve outside a running Prez. prez (RDFLib/prez@421ee0a9fe) is not
# installed in the study venv: its modules are imported from the pinned clone
# made by `rdfeval acquire` (corpus/repos/RDFLib__prez), i.e. the REAL
# prez.reference_data.prez_ns (PREZ, ALTREXT, OGCFEAT) and the REAL
# prez.services.curie_functions.get_curie_id_for_uri run, unmodified.
#
# What the clone cannot import without fastapi / pyoxigraph / aiocache /
# pydantic-settings is replaced by a module with only what is used:
#
#   * aiocache, prez.cache, prez.config: curie_functions imports a cache
#     registry (never called by get_curie_id_for_uri), the prefix graph
#     (prez/cache.py: `prefix_graph = Graph(bind_namespaces="none")`) and
#     `settings.curie_separator` (prez/config.py default: ":").
#   * prez.renderers.renderer: the region only awaits `return_from_graph`
#     and imports seven more names it never calls. The real renderer
#     serialises a response; this one hands back, as a dict, exactly what it
#     was given, so that the driver sees what the region passed on.
# If the real dependencies are installed, nothing is stubbed.
# Identical bindings for both representations.
import importlib
import sys
import types
from pathlib import Path

from rdflib import Graph

_CLONE = Path(__file__).resolve().parents[3] / "corpus" / "repos" / "RDFLib__prez"
if str(_CLONE) not in sys.path:
    sys.path.insert(0, str(_CLONE))


def _module(name, **names):
    mod = types.ModuleType(name)
    mod.__dict__.update(names)
    sys.modules[name] = mod
    return mod


try:
    importlib.import_module("aiocache")
    importlib.import_module("prez.cache")
    importlib.import_module("prez.config")
except ImportError:
    class _Caches:
        def get(self, name):
            raise NotImplementedError("the cache registry is not used by the region")

        def set_config(self, config):
            pass

    _module("aiocache", caches=_Caches())
    _module("prez.cache", prefix_graph=Graph(bind_namespaces="none"))
    _module("prez.config",
            settings=types.SimpleNamespace(curie_separator=":"))

try:
    importlib.import_module("prez.renderers.renderer")
except ImportError:
    async def return_from_graph(graph, mediatype, profile, profile_headers,
                                selected_class, repo, system_repo,
                                query_params=None, url=None):
        return {"graph": graph, "mediatype": mediatype, "profile": profile,
                "headers": profile_headers, "selected_class": selected_class,
                "repo": repo, "system_repo": system_repo,
                "query_params": query_params, "url": url}

    async def _unused(*args, **kwargs):
        raise NotImplementedError("not used by the region")

    _module("prez.renderers.renderer",
            return_from_graph=return_from_graph,
            return_annotated_rdf_for_oxigraph=_unused,
            generate_geojson_extras=_unused,
            handle_alt_profile=_unused,
            generate_queryables_from_shacl_definition=_unused,
            create_collections_json=_unused,
            generate_link_headers=_unused,
            get_geojson_int_count=_unused)
