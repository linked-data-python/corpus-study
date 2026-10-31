"""What a participant is given besides the code: the call the answers come
from, and the graph it receives — and answers that count only what the
region changed in that graph."""

from rdfeval.userstudy import _inputs, _observables, _py, _shown_graph

ORIGINAL = """\
from rdflib import Graph, URIRef
P = URIRef("http://e/p")

def add(d, g):
    for k in d:
        g.add((URIRef("http://e/" + k), P, URIRef("http://e/o")))

def drop(g):
    g.remove((URIRef("http://e/x"), None, None))

def read(path, label):
    return len(Graph().parse(path))

def opaque(store):
    return None
"""

DRIVER = """\
from pathlib import Path
from rdflib import Graph, URIRef
from rdfeval.harness import run_pair

def _g():
    g = Graph()
    g.add((URIRef("http://e/x"), URIRef("http://e/p"), URIRef("http://e/o")))
    return g

run_pair(__file__, entry={entry!r}, calls=[lambda: ({args}, {{}})])
"""


def _example(tmp_path, entry, args):
    ex = tmp_path / "ex"
    ex.mkdir()
    (ex / "original.py").write_text(ORIGINAL)
    (ex / "driver.py").write_text(DRIVER.format(entry=entry, args=args))
    (ex / "data.ttl").write_text(
        "# designed so that the neighbour must be skipped\n"
        "<http://e/x> <http://e/p> <http://e/o> .\n")
    return ex


def test_the_call_and_the_input_graph_are_shown(tmp_path):
    ex = _example(tmp_path, "add", "({'a': 1, 'b': 2}, _g())")
    shown = _inputs(ex)
    assert shown["inputs_shown"] == "complete"
    assert shown["call"] == ("# g is the input graph shown above\n"
                             "add(d={'a': 1, 'b': 2}, g=g)\n")
    assert "<http://e/x>" in shown["input_graph"] or "x" in shown["input_graph"]


def test_answers_count_only_the_triples_the_region_added(tmp_path):
    ex = _example(tmp_path, "add", "({'a': 1, 'b': 2}, _g())")
    triples, value, removed = _observables(ex, {})
    assert len(triples) == 2            # not 3: x was already there
    assert all("x" not in t[0] for t in triples)


def test_a_region_that_only_deletes_is_asked_about_the_deletion(tmp_path):
    ex = _example(tmp_path, "drop", "(_g(),)")
    triples, value, removed = _observables(ex, {})
    assert triples is None and len(removed) == 1


def test_a_data_file_is_shown_by_name_without_its_comments(tmp_path):
    ex = _example(tmp_path, "read",
                  "(str(Path(__file__).parent / 'data.ttl'), 'x')")
    shown = _inputs(ex)
    assert shown["inputs_shown"] == "complete"
    assert "read(path='data.ttl', label='x')" in shown["call"]
    assert str(tmp_path) not in shown["call"]
    assert "neighbour" not in shown["input_graph"]
    assert "<http://e/x>" in shown["input_graph"]


def test_an_argument_without_source_form_is_left_to_the_reviewer(tmp_path):
    ex = _example(tmp_path, "opaque", "(object(),)")
    shown = _inputs(ex)
    assert shown["inputs_shown"] == "none" and shown["call"] is None
    assert "object" in shown["inputs_missing"]


def test_long_values_break_one_item_per_line():
    text = _py({"key-%d" % i: "value-%d" % i for i in range(6)})
    assert text.startswith("{\n    'key-0': 'value-0',\n")
    assert _py({"a": 1}) == "{'a': 1}"
    assert _py({3, 1, 2}) == "{1, 2, 3}"


def test_fixture_comments_are_not_shown():
    assert _shown_graph("# the answer is 2\n\n<a> <b> <c> .\n") == "<a> <b> <c> .\n"
