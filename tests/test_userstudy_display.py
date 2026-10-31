"""What the user study shows of a pair: the region, without the scaffolding."""

from rdfeval.userstudy import display_source

PAIR = """\
# Extracted from owner/repo@abc123 : pkg/mod.py
# region: f (lines 10-20, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import Graph
from mod_context import helper  # context shim -- see meta.json

def f(g):
    # a comment of the region stays
    g.add(helper())


# Test harness only (see meta.json): demo() makes the region observable.
def demo():
    g = Graph()
    f(g)
    return g
"""


def test_header_harness_and_shim_remark_are_cut():
    assert display_source(PAIR) == (
        "from rdflib import Graph\n"
        "from mod_context import helper\n"
        "\n"
        "def f(g):\n"
        "    # a comment of the region stays\n"
        "    g.add(helper())\n")


def test_a_file_without_harness_keeps_its_body():
    text = "# Extracted from x\nimport rdflib\n\ndef f():\n    return 1\n"
    assert display_source(text) == "import rdflib\n\ndef f():\n    return 1\n"


def test_the_cut_is_the_same_on_both_sides():
    ldpy = PAIR.replace("g.add(helper())", "+{ {helper()} }(g)")
    shown_py = display_source(PAIR).splitlines()
    shown_ld = display_source(ldpy).splitlines()
    assert len(shown_py) == len(shown_ld)
    assert all("demo" not in line for line in shown_py + shown_ld)


def test_a_nested_demo_is_not_mistaken_for_the_harness():
    text = "def f():\n    def demo():\n        pass\n    return demo\n"
    assert display_source(text) == text
