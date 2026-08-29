"""Validation driver for eccenca__cmem-plugin-shapes__tests_test_shapes.py__test_workflow_execution.

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
  * a real clock and a real provenance stamp: the region asserts that the
    server wrote exactly one ``dcterms:created`` whose lexical form matches
    ``DATETIME_PATTERN``, then removes it before comparing.

The graph the region reads is therefore an OUTPUT of the deployment, not an
input a fixture could supply: ``fixture.ttl`` is kept only to say so.  The
translation was verified by transpilation only -- see meta.json.

Run anyway: the verdict below carries the exact import error.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry="test_workflow_execution", calls=[])
