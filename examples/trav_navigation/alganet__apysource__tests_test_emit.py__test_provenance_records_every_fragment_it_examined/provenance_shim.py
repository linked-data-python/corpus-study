# Context shim (see meta.json): `_Fetcher` and `_run_with_provenance` of
# tests/test_emit.py from alganet/apysource@f800ec97c1, so the region executes
# outside the test module. apysource itself is the real installed package
# (0.10.0); only the test module's own helpers are reproduced.
#
# One difference, stated: the original reads tests/fixtures/un_charter.html
# (150 kB) from the repository; here BODY is a few lines of HTML holding the
# first sentence of that page, which is all the two fragments look for. The
# driver rebinds BODY to run the region against runs whose verdicts differ
# (identical bindings for both representations). Nothing else is changed.
from apysource.api import check_graph
from apysource.repos import RepoRegistry
from apysource.yaml_input import graph_from_data

BODY = (
    "<html><head><title>Charter of the United Nations</title></head><body>"
    "<h1>Preamble</h1>"
    "<p>We the peoples of the United Nations determined to save succeeding "
    "generations from the scourge of war, which twice in our lifetime has "
    "brought untold sorrow to mankind, and to reaffirm faith in fundamental "
    "human rights, in the dignity and worth of the human person.</p>"
    "</body></html>"
)


class _Fetcher:
    def __init__(self, body):
        self.body = body

    def get(self, url, force=False):
        return self.body


def _run_with_provenance():
    body = BODY
    g = graph_from_data({"sources": [{
        "label": "UN Charter", "url": "https://un.org/x", "type": "text/html",
        "fragments": [
            {"label": "Preamble",
             "snippet": "to save succeeding generations from the scourge of war"},
            {"label": "Absent",
             "snippet": "this sentence appears nowhere in the charter at all"},
        ],
    }]})
    results, prov = check_graph(g, registry=RepoRegistry([]),
                                fetcher=_Fetcher(body), emit_provenance=True)
    return g, prov
