# Context shim (see meta.json): pandas, collections.OrderedDict and repl(),
# restored from dice-group/COVID19DS@7842845de5
# decaData_product_purchasing/toRdf.py, lines 8, 9 and 128-129 -- defined
# elsewhere in the same source file (repl is defined AFTER handleFile in the
# real file, at module scope, so it is already bound by the time
# handleFile() is called at the bottom of that file; here it is imported
# explicitly instead). repl() is copied verbatim. pandas and OrderedDict are
# re-exported so `pd.read_csv(...)` and `into=OrderedDict` in original.py /
# translated.ldpy resolve exactly as in the real module.
# Identical for both representations.
import pandas as pd
from collections import OrderedDict


def repl(m):
	return m.group(1).upper()
