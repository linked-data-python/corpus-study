"""Validation driver for ktbs__ktbs__lib_ktbs_engine_trace.py__StoredTrace_post_graph.

EXCLUDED (see meta.json): this region cannot be executed standalone.
`from rdfrest.exceptions import InvalidDataError` alone already fails with
`ModuleNotFoundError: No module named 'rdfrest'` -- `rdfrest` is ktbs's own
REST-resource framework (not on PyPI, not vendored here), not a leaf
dependency a context shim could stand in for without reimplementing it.
Past that import, `post_graph` is a method on `StoredTrace`, itself a
`rdfrest` resource class: `self.get_base()`, `self.obsel_collection.edit()`,
`super(StoredTrace, self).post_graph`, `self.trace_statistics` are all
`rdfrest`/ktbs engine behaviour, not data a fixture could supply. Faithfully
executing this region means standing up ktbs's resource store, which is
exactly the "invent logic" the batch protocol rules out for a context shim.
Left unfilled per AGENT_BATCH.md `Quand ca ne passe pas`, case 1: the
translation is believed correct, but the driver cannot prove it.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='post_graph',
    calls=[]  # cannot be filled: see EXCLUDED note above.
)
