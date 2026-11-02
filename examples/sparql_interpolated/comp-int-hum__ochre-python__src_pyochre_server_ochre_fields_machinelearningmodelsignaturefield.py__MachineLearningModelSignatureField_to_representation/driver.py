"""Validation driver for comp-int-hum__ochre-python__src_pyochre_server_ochre_fields_machinelearningmodelsignaturefield.py__MachineLearningModelSignatureField_to_representation.

IDENTITY translation of the stratum's site (see meta.json): the query is
`"PREFIX ochre: <{}>\\n".format(settings.OCHRE_NAMESPACE) + mvq_string`, where
`mvq_string` is read at run time from a package file.  Text spliced as syntax
(a PREFIX header whose IRI comes from a string, a whole query from a file) has
no form in `s{ }`; the region keeps `sig.query(...)`.  The one read that has a
pattern written in the code, `sig.triples((None, OCHRE["simpleFormat"], None))`,
is `m{ ?s {OCHRE["simpleFormat"]} ?o }` in the translation.

What the region makes visible is thin: `tab_list` is never filled (its
`append` is commented out in the source), so the method always returns
`str(object)` and sets the same six keys of `self.style`.  The rows the query
returns reach nothing but the lookups `tab[OCHRE["instanceOf"]][0]` and
`tab[OCHRE["hasDescription"]][0]`, which RAISE when a returned subject lacks
one.  The driver therefore makes the query itself observable: the signature
graph is a `RecordingGraph` whose `query` appends (query text, sorted rows) to
a list that the model object carries, so the text sent (header + file) and the
rows received are part of the state the harness compares after the call.

Calls (fixture.ttl is parsed into a RecordingGraph; `fixture=` alone would pass
a plain graph):

  1. the fixture: four widgets returned, three neighbours not, two
     simpleFormat triples on subjects that are neither Input nor Output.
  2. a signature with no widget at all: zero rows, same style.
  3. a widget with an instanceOf and no hasDescription: KeyError on the missing
     key (the returned row decides the outcome).
  4. `ochre:Input ochre:simpleFormat ...`: the first loop reaches
     `input_widget_map[o]`, a name the extracted module never defines
     (NameError, compared as the outcome; the query is never sent).
  5. `ochre:Output ochre:simpleFormat ...` next to a neutral subject: the
     `elif` branch reaches `output_widget_map[o]`, the same missing-name error
     with the other name.

"""
from pathlib import Path

from rdflib import Graph

from rdfeval.harness import run_pair

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.ttl"

HEADER = """@prefix ochre: <https://cdh.jhu.edu/> .
@prefix ex: <http://example.org/> .
"""


class RecordingGraph(Graph):
    """A graph that keeps what `.query()` was given and what it answered."""

    def __init__(self, log):
        super().__init__()
        self._log = log

    def query(self, query_object, *args, **kwargs):
        rows = list(super().query(query_object, *args, **kwargs))
        self._log.append((str(query_object),
                          sorted((tuple(r) for r in rows), key=repr)))
        return rows


class Field:
    """The serializer field the method hangs on: a `style` dict."""

    def __init__(self):
        self.style = {}


class Model:
    """The `object` argument: a signature graph, an id, the query log."""

    def __init__(self, turtle=None, path=None):
        self.id = 7
        self.queries = []
        self.signature = RecordingGraph(self.queries)
        if path is not None:
            self.signature.parse(str(path), format="turtle")
        if turtle is not None:
            self.signature.parse(data=HEADER + turtle, format="turtle")

    def __str__(self):
        return "model #{}".format(self.id)


def call(**kw):
    return lambda: ((Field(), Model(**kw)), {})


VERDICT = run_pair(
    __file__,
    entry="to_representation",
    fixture="fixture.ttl",
    calls=[
        call(path=FIXTURE),
        call(turtle="ex:a ex:p ex:b ."),
        call(turtle='ex:w ochre:instanceOf ochre:VegaVisualization .'),
        call(turtle='ochre:Input ochre:simpleFormat ochre:Text .'),
        call(turtle='ex:f ochre:simpleFormat ochre:Text . ochre:Output ochre:simpleFormat ochre:Image .'),
    ],
)
