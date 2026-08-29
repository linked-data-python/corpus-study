# Extracted from MDD4REST/mdd4rest-annotator@c46839aa3d : server/src/rdflib2/plugins/sparql/results/rdfresults.py
# region: RDFResult.__init__ (lines 15-61, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, RDF, Variable
from rdflib.query import Result, ResultParser
RS = Namespace('http://www.w3.org/2001/sw/DataAccess/tests/result-set#')

def __init__(self, source, **kwargs):

    if not isinstance(source, Graph):
        graph = Graph()
        graph.load(source, **kwargs)
    else:
        graph = source

    rs = graph.value(predicate=RDF.type, object=RS.ResultSet)
                     # there better be only one :)

    if rs is None:
        type_ = 'CONSTRUCT'

        # use a new graph
        g = Graph()
        g += graph

    else:

        askAnswer = graph.value(rs, RS.boolean)

        if askAnswer is not None:
            type_ = 'ASK'
        else:
            type_ = 'SELECT'

    Result.__init__(self, type_)

    if type_ == 'SELECT':
        self.vars = [Variable(v) for v in graph.objects(rs,
                                                        RS.resultVariable)]

        self.bindings = []

        for s in graph.objects(rs, RS.solution):
            sol = {}
            for b in graph.objects(s, RS.binding):
                sol[Variable(graph.value(
                    b, RS.variable))] = graph.value(b, RS.value)
            self.bindings.append(sol)
    elif type_ == 'ASK':
        self.askAnswer = askAnswer.value
        if askAnswer.value == None:
            raise Exception('Malformed boolean in ask answer!')
    elif type_ == 'CONSTRUCT':
        self.graph = g

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
