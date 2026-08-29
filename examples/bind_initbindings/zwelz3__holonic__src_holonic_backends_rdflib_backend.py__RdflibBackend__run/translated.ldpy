# Extracted from zwelz3/holonic@d8d1758752 : src/holonic/backends/rdflib_backend.py
# region: RdflibBackend._run (lines 111-118, stratum bind_initbindings)
# licence of the source repository: see meta.json
from typing import Any, cast
from holonic.backends._bindings import as_init_bindings

def _run(self, sparql: str, bindings: dict[str, Any]) -> Any:
    """Prepare (cached) and execute a read query with rdflib bindings.

    Binding values follow the shared explicit-wrapper contract
    (``_bindings.as_init_bindings``): rdflib terms pass through, bare
    Python values become literals, so IRIs must arrive as ``URIRef``.
    """
    return self.ds.query(_prepare(sparql), initBindings=as_init_bindings(bindings))
