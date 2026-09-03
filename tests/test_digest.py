"""The review digest: what it reads out of a pair, and what it flags.

The digest decides nothing — it renders.  What has to hold is that it reads
the driver correctly (it parses the file rather than running it), that each
screen fires on the shape it claims and stays quiet otherwise, and that a
page comes out well formed with every pair in it.
"""

import json
from html.parser import HTMLParser

import pytest

from rdfeval import digest
from rdfeval.study import Study

VOID = {"meta", "br", "hr", "img", "input", "link", "area", "base", "col",
        "embed", "source", "track", "wbr"}

ORIGINAL = '''\
"""A docstring, so a multi-line token crosses the line numbering."""
from rdflib import Graph, Literal, Namespace

EX = Namespace("http://example.org/")


def build():
    g = Graph()
    g.add((EX.a, EX.p, Literal(1)))
    return g
'''

TRANSLATED = '''\
"""A docstring, so a multi-line token crosses the line numbering."""
@prefix ex: <http://example.org/> .


def build():
    @graph as g
    +{ ex:a ex:p 1 }
    return g
'''

DRIVER = '''\
"""Driver."""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry="build", calls=[((), {}), ((), {})])
'''

META = {
    "region_id": "owner__repo__mod.py__build",
    "repository": "owner/repo",
    "commit": "0123456789abcdef",
    "path": "mod.py",
    "qualname": "build",
    "lineno": 7,
    "end_lineno": 10,
    "stratum": "add_isolated",
    "kind": "function",
    "translation_status": "final",
    "classification": "directly-expressible",
    "constructions": ["@prefix", "@graph", "+{ }"],
    "translation_notes": ["a note the page must show"],
    "oracle": "isomorphism",
    "validation": {"status": "equivalent", "method": "entry:build",
                   "diffs": []},
}


@pytest.fixture
def study(tmp_path):
    """A one-pair study on disk, shaped exactly like the real one."""
    ex = tmp_path / "examples" / "add_isolated" / META["region_id"]
    ex.mkdir(parents=True)
    (ex / "original.py").write_text(ORIGINAL)
    (ex / "translated.ldpy").write_text(TRANSLATED)
    (ex / "driver.py").write_text(DRIVER)
    (ex / "meta.json").write_text(json.dumps(META))
    return Study(name="t", examples_dir=tmp_path / "examples",
                 group="stratum", suffix="")


def _dir(study):
    return next(iter(study.examples_dir.glob("*/*")))


def _flags(ex, meta=None, row=None):
    meta = dict(META, **(meta or {}))
    return digest._flags(ex, meta, row or {}, digest._files(ex))


def _labels(flags, level=None):
    return {label for lvl, label, _ in flags if level in (None, lvl)}


# ------------------------------------------------------------------ reading

def test_the_driver_is_parsed_not_executed(study):
    """A digest over three hundred drivers must never run one of them."""
    ex = _dir(study)
    (ex / "driver.py").write_text(DRIVER + "\nraise SystemExit('ran!')\n")
    facts = digest._driver_facts(ex / "driver.py")
    assert facts == {"entry": "build", "fixture": None, "calls": 2,
                     "parsed": True}


def test_an_unparsable_driver_is_a_danger_not_a_crash(study):
    ex = _dir(study)
    (ex / "driver.py").write_text("def (:\n")
    assert "driver unreadable" in _labels(_flags(ex), digest.DANGER)


def test_a_shim_is_anything_that_is_not_one_of_the_known_files(study):
    ex = _dir(study)
    (ex / "context_shim.py").write_text("X = 1\n")
    assert [p.name for p in digest._files(ex)["shims"]] == ["context_shim.py"]


# -------------------------------------------------------------------- flags

def test_a_clean_pair_raises_no_danger(study):
    assert not _labels(_flags(_dir(study)), digest.DANGER)


def test_a_reading_region_with_a_thin_fixture_is_flagged(study):
    ex = _dir(study)
    (ex / "fixture.ttl").write_text(
        "<http://e/a> <http://e/p> <http://e/b> .\n")
    assert "thin fixture" in _labels(
        _flags(ex, {"oracle": "values"}), digest.DANGER)


def test_a_fat_enough_fixture_is_not(study):
    ex = _dir(study)
    (ex / "fixture.ttl").write_text("".join(
        "<http://e/a> <http://e/p%d> <http://e/b> .\n" % i for i in range(10)))
    assert not _labels(_flags(ex, {"oracle": "values"}), digest.DANGER)


def test_demo_harnesses_that_differ_are_a_danger(study):
    """A harness appended to both sides is legitimate; one that differs
    between the sides can hide the difference the pair should expose."""
    ex = _dir(study)
    (ex / "original.py").write_text(ORIGINAL + "\ndef demo():\n    return 1\n")
    (ex / "translated.ldpy").write_text(
        TRANSLATED + "\ndef demo():\n    return 2\n")
    assert "demo() harnesses differ" in _labels(_flags(ex), digest.DANGER)


def test_identical_demo_harnesses_are_only_a_warning(study):
    ex = _dir(study)
    tail = "\ndef demo():\n    return build()\n"
    (ex / "original.py").write_text(ORIGINAL + tail)
    (ex / "translated.ldpy").write_text(TRANSLATED + tail)
    flags = _flags(ex)
    assert not _labels(flags, digest.DANGER)
    assert "demo() harness on both sides" in _labels(flags, digest.WARN)


def test_a_function_region_compared_as_module_state_is_flagged(study):
    """Both hollow greens found by hand in this corpus had this shape."""
    ex = _dir(study)
    (ex / "driver.py").write_text(
        "from rdfeval.harness import run_pair\nrun_pair(__file__)\n")
    assert "compared as module state" in _labels(_flags(ex), digest.WARN)


def test_a_translation_without_an_island_is_a_danger(study):
    assert "no island at all" in _labels(
        _flags(_dir(study), row={"ldpy_islands": "0"}), digest.DANGER)


def test_a_not_expressible_pair_is_not_scolded_for_being_long(study):
    """`not-expressible` is a RESULT: the ldpy file is then the Python file,
    declares no construction, and neither fact is a defect to report."""
    flags = _flags(_dir(study),
                   {"classification": "not-expressible", "constructions": []},
                   {"ratio_tokens": "1.4"})
    assert not _labels(flags, digest.DANGER)
    assert "the translation grew" not in _labels(flags)
    assert "no construction declared" not in _labels(flags)


def test_flags_come_out_worst_first(study):
    ex = _dir(study)
    (ex / "context_shim.py").write_text("X = 1\n")
    (ex / "driver.py").write_text("def (:\n")
    levels = [lvl for lvl, _, _ in _flags(ex)]
    assert levels == sorted(levels, key=[digest.DANGER, digest.WARN,
                                         digest.INFO].index)


# --------------------------------------------------------------------- page

class _Balance(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.bad = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        else:
            self.bad.append(tag)


def test_the_pages_are_well_formed_and_hold_every_pair(study, tmp_path):
    out = tmp_path / "review"
    digest.run({}, study, out_dir=out)
    for page in (out / "index.html", out / "add_isolated.html"):
        parser = _Balance()
        parser.feed(page.read_text())
        assert not parser.bad and not parser.stack, page.name
    page = (out / "add_isolated.html").read_text()
    assert page.count('<section class="pair"') == 1
    assert META["region_id"] in page
    assert "a note the page must show" in page
    assert "github.com/owner/repo/blob/0123456789abcdef/mod.py#L7-L10" in page


def test_the_page_escapes_what_a_pair_contains(study, tmp_path):
    ex = _dir(study)
    (ex / "original.py").write_text("x = '<script>alert(1)</script>'\n")
    digest.run({}, study, out_dir=tmp_path / "r")
    page = (tmp_path / "r" / "add_isolated.html").read_text()
    assert "<script>alert(1)</script>" not in page
    assert "&lt;script&gt;" in page


def test_asking_for_one_stratum_leaves_the_index_alone(study, tmp_path):
    out = tmp_path / "review"
    out.mkdir()
    (out / "index.html").write_text("older index")
    digest.run({}, study, stratum="add_isolated", out_dir=out)
    assert (out / "add_isolated.html").exists()
    assert (out / "index.html").read_text() == "older index"


def test_a_shim_in_a_package_directory_is_found(study):
    """A region whose own imports are relative needs its shim in a package;
    the digest must still show it."""
    ex = _dir(study)
    (ex / "lib").mkdir()
    (ex / "lib" / "__init__.py").write_text("")
    (ex / "lib" / "utils.py").write_text("NGSILD = 1\n")
    names = {str(p.relative_to(ex)) for p in digest._files(ex)["shims"]}
    assert names == {"lib/__init__.py", "lib/utils.py"}


def test_several_fixtures_are_counted_together(study):
    """One Turtle file per branch is a legitimate shape: the screen must
    weigh the evidence as a whole, not fire on each file's small count."""
    ex = _dir(study)
    for i in range(4):
        (ex / ("fixture_%d.ttl" % i)).write_text("".join(
            "<http://e/a%d> <http://e/p%d> <http://e/b> .\n" % (i, j)
            for j in range(3)))
    assert digest._fixture_size(digest._files(ex)["fixtures"]) == 12
    assert not _labels(_flags(ex, {"oracle": "values"}), digest.DANGER)


def test_pycache_is_not_mistaken_for_a_shim(study):
    ex = _dir(study)
    (ex / "__pycache__").mkdir()
    (ex / "__pycache__" / "original.cpython-312.py").write_text("x = 1\n")
    assert digest._files(ex)["shims"] == []


def test_data_that_is_not_turtle_is_still_shown(study, tmp_path):
    """A region that builds its graph from a CSV needs that CSV: it is as
    much part of the evidence as a Turtle fixture, and must not vanish."""
    ex = _dir(study)
    (ex / "vbis-brick.csv").write_text("a,b\n1,2\n")
    files = digest._files(ex)
    assert [p.name for p in files["data"]] == ["vbis-brick.csv"]
    assert files["fixtures"] == []
    digest.run({}, study, out_dir=tmp_path / "r")
    page = (tmp_path / "r" / "add_isolated.html").read_text()
    assert "vbis-brick.csv — pair data (2 lines)" in page


def test_pairs_follow_the_directory_listing(study, tmp_path):
    """A reader holds the page and `ls examples/<stratum>/` side by side.

    `iter_examples` sorts by code point, which puts every capital before
    every lowercase; a listing sorts case-insensitively. The page follows
    the listing.
    """
    import re
    stratum = study.examples_dir / "add_isolated"
    for name in ("Zebra__repo__m.py__z", "alpha__repo__m.py__a",
                 "Beta__repo__m.py__b"):
        ex = stratum / name
        ex.mkdir()
        (ex / "original.py").write_text(ORIGINAL)
        (ex / "translated.ldpy").write_text(TRANSLATED)
        (ex / "driver.py").write_text(DRIVER)
        (ex / "meta.json").write_text(json.dumps(dict(META, region_id=name)))
    digest.run({}, study, out_dir=tmp_path / "r")
    page = (tmp_path / "r" / "add_isolated.html").read_text()
    ids = re.findall(r'<section class="pair" id="([^"]+)"', page)
    assert ids == sorted(ids, key=str.lower)
    assert ids.index("alpha__repo__m.py__a") < ids.index("Beta__repo__m.py__b")
