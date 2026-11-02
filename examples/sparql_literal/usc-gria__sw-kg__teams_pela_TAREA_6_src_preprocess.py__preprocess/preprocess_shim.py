# Context shim (see meta.json): the module-level context of
# teams/pela/TAREA_6/src/preprocess.py from usc-gria/sw-kg@08db325932, so the
# region executes outside the repository. Identical bindings for both
# representations.
#
# Two deliberate departures, both about WHERE files live, not about logic:
#  * the repository computes SRC_DIR / TAREA_6_DIR / REPO_DIR from __file__
#    and reads TAREA_4/kg/output.nt, writes TAREA_6/data/processed/*.csv. Here
#    the knowledge graph is `fixture.ttl` of the example directory (it holds
#    N-Triples, which the region parses with format='nt') and the CSV files
#    are written in the example directory itself, where the harness compares
#    and removes them. KG_PATH and DATA_DIR keep their names and roles.
#  * get_wikidata_info is the repository's, line for line; it talks to
#    query.wikidata.org through `requests`, which the driver replaces by a
#    local stand-in (the network is not part of what is being proved).
import os
import time

import requests

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = SRC_DIR
KG_PATH = os.path.join(SRC_DIR, 'fixture.ttl')


def get_wikidata_info(wd_uris, query_template):
    #
    endpoint_url = 'https://query.wikidata.org/sparql'
    results_map = {}

    uris = list({u for u in wd_uris if u})
    if not uris:
        return results_map

    headers = {'User-Agent': 'SportsKGExplorer/1.0 (mateo@example.org)', 'Accept': 'application/sparql-results+json'}

    # Consultas por lotes para no enviar un VALUES demasiado grande.
    batch_size = 10
    for i in range(0, len(uris), batch_size):
        values = " ".join(f"<{uri}>" for uri in uris[i:i + batch_size])
        query = query_template.replace("{{VALUES}}", values)

        for attempt in range(3):
            try:
                response = requests.get(
                    endpoint_url,
                    params={'query': query, 'format': 'json'},
                    headers=headers,
                    timeout=20,
                )
                if response.status_code == 200:
                    bindings = response.json().get('results', {}).get('bindings', [])
                    for result in bindings:
                        item_uri = result.get('item', {}).get('value')
                        if item_uri:
                            results_map[item_uri] = {
                                k: v.get('value')
                                for k, v in result.items()
                                if k != 'item'
                            }
                    break

                print(f"Wikidata error {response.status_code}, retrying...")
            except Exception as e:
                print(f"Attempt {attempt} failed: {e}")

            time.sleep(2)

    return results_map
