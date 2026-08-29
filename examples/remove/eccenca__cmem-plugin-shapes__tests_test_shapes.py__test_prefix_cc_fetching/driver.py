"""Validation driver for eccenca__cmem-plugin-shapes__tests_test_shapes.py__test_prefix_cc_fetching.

UNRESOLVABLE BY CONSTRUCTION -- kept so the pipeline records why.

The region is an integration test of the cmem-plugin-shapes workflow plugin.
Executing it needs, all at once:

  * ``cmem_client``, ``cmem_plugin_base`` and ``cmem_plugin_shapes``, none of
    which is installed here (``cmem_client`` is what fails first);
  * a live eccenca Corporate Memory deployment: the ``graph_setup`` pytest
    fixture skips the whole module unless ``CMEM_BASE_URI`` is set, then
    shells out to ``cmemc`` to export the store, import two fixture graphs at
    http://docker.localhost/… and create a project; ``plugin.execute`` writes
    the generated shapes graph into that store and ``get_graph_content``
    (a helper of the test module, outside the extracted region) reads it back;
  * the network: this test is precisely the one that sets ``prefix_cc=True``,
    so the plugin fetches the prefix list from https://prefix.cc.

Everything the final ``isomorphic`` assertion observes is produced by the
server; a fixture graph could only stand in for it by re-implementing the
plugin, which would validate the double instead of the region.  The
translation was therefore verified by transpilation only -- see meta.json.

Run anyway: the verdict below carries the exact import error.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry="test_prefix_cc_fetching", calls=[])
