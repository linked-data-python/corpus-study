# Extracted from isaacgravenor/neo-galacteek@e201b39d78 : galacteek/dweb/channels/graphs.py
# region: SparQLResultsModel._prepareQuery (lines 243-254, stratum bind_initbindings)
# licence of the source repository: see meta.json
import traceback
from rdflib.plugins.sparql import prepareQuery
from galacteek import log

def _prepareQuery(self, name, query):
    try:
        ns = self._pStdPrefixes.copy()
        ns.update(self._pPrefixes)
        q = prepareQuery(query, initNs=ns)
    except Exception as err:
        traceback.print_exc()
        log.debug(str(err))
        return False
    else:
        self._qprepared[name] = q
        return True
