# Extracted from isaacgravenor/neo-galacteek@e201b39d78 : galacteek/ld/rdf/guardian.py
# region: GraphGuardian.mergeReplace.mergeReplaceRun (lines 330-354, stratum remove)
# licence of the source repository: see meta.json
import traceback
import time
from rdflib import Graph
from rdflib import BNode
from galacteek import log

def mergeReplaceRun(gsrc: Graph, gdst: Graph) -> bool:
    try:
        for s, p, o in gsrc:
            # No BNodes allowed by default
            if isinstance(s, BNode) and not bnodes:
                gsrc.remove((s, p, o))
            elif isinstance(o, BNode) and not bnodes:
                gsrc.remove((s, p, o))

            gdst.remove((s, p, None))
            time.sleep(0.05)

        # Should lock here
        gdst += gsrc
    except Exception:
        log.warning(f'mergeReplace failure ! {traceback.format_exc()}')
        return False
    else:
        # Hub notification

        if notify:
            dst.publishUpdateEvent(gsrc)

        log.debug(f'mergeReplace success: {len(graph)} triples')
        return True
