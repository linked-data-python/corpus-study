# Extracted from ktbs/ktbs@4f9f50c770 : lib/ktbs/engine/method.py
# region: Method.check_deletable (lines 182-194, stratum trav_one_step)
# licence of the source repository: see meta.json
from ..namespace import KTBS

def check_deletable(self, parameters):
    """I implement :meth:`~rdfrest.cores.local.ILocalCore.check_deletable`

    I refuse to be deleted if I am used by a trace.
    """
    diag = super(Method, self).check_deletable(parameters)
    for i in self.state.subjects(KTBS.hasMethod, self.uri):
        diag.append("<%s> is used (ktbs:hasMethod) by <%s>"
                    % (self.uri, i))
    for i in self.state.subjects(KTBS.hasParentMethod, self.uri):
        diag.append("<%s> is used (ktbs:hasParentMethod) by <%s>"
                    % (self.uri, i))
    return diag
