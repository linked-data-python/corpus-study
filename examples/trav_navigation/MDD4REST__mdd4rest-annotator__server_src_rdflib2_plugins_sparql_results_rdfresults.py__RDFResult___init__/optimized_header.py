# Extracted from MDD4REST/mdd4rest-annotator@c46839aa3d : server/src/rdflib2/plugins/sparql/results/rdfresults.py
# region: RDFResult.__init__ (lines 15-61, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, RDF, Variable
from rdflib.query import Result
RS = Namespace('http://www.w3.org/2001/sw/DataAccess/tests/result-set#')

def __init__(self, source, **kwargs):

    graph = source
    if not isinstance(source, Graph):
        graph = Graph()
        graph.load(source, **kwargs)

    rs = graph.value(predicate=RDF.type, object=RS.ResultSet)
                     # there better be only one :)

    if rs is None:
        Result.__init__(self, 'CONSTRUCT')
        # use a new graph
        self.graph = Graph()
        self.graph += graph
        return

    askAnswer = graph.value(rs, RS.boolean)

    if askAnswer is not None:
        Result.__init__(self, 'ASK')
        self.askAnswer = askAnswer.value
        if askAnswer.value == None:
            raise Exception('Malformed boolean in ask answer!')
        return

    Result.__init__(self, 'SELECT')
    self.vars = [Variable(v) for v in graph.objects(rs, RS.resultVariable)]
    self.bindings = []
    for s in graph.objects(rs, RS.solution):
        self.bindings.append({Variable(graph.value(b, RS.variable)): graph.value(b, RS.value)
                              for b in graph.objects(s, RS.binding)})

# Demo harness (identical on both sides, see meta.json): the region is a
# bare `__init__(self, source, **kwargs)` body, not a class -- there is no
# RDFResult to instantiate. `run` supplies a throwaway namespace object as
# `self`, calls the region on it, and returns a plain dict of the
# interesting attributes, since the harness's structural comparison (dict /
# list / set) is what actually walks into a result and ignores solution
# order and blank-node identity; comparing two SimpleNamespace instances
# directly would not (SimpleNamespace equality is exact-order attribute
# equality, and there is no such thing as an ordered solution set here).
def run(source):
    from types import SimpleNamespace
    self = SimpleNamespace()
    __init__(self, source)
    return {
        "type": self.type,
        "vars": self.vars,
        "bindings": getattr(self, "bindings", None),
        "askAnswer": self.askAnswer,
        "graph": self.graph,
    }
