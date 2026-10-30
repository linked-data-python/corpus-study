"""Validation driver for calipho-sib__nextprot-scripts__src_polish-rdf_pylode_pyLODE-2.13.2_pylode_profiles_base.py__BaseProfile__make_schemaorg_metadata.

Establishes semantic equivalence of original.py and translated.ldpy.

The region builds a local graph and returns its JSON-LD serialisation: the
returned TEXT is what the harness compares (exactly), along with what each
call raises (type and message) and the `self` it was given (METADATA and
outputformat, by value).  The graph itself never leaves the function, so a
raise discards it on both sides: `+{ }`'s evaluate-then-write (record
ldpy/014) cannot be observed here.

What the repository really passes (pyLODE-2.13.2, profiles/ontdoc.py:345-431
and the vocpub/nmpf/prof equivalents): METADATA holds "uri", "title"
(defaulted to "{no title found}"), "description", "created" / "modified" /
"issued" (dcterms dates, as str), "license" and "repository" FORMATTED for
the output format by _make_formatted_uri_basic (profiles/base.py:72-81:
html `<a href="URI">curie</a>`, md `[curie](URI)`, adoc `link:URI[curie]`;
a license that does not start with http stays a bare string), "rights".
outputformat is "html", "md" or "adoc".  The keys "date_created",
"date_modified" and "copyright_year" that guard three of the islands are
never set by the repository: those islands are dead there, but the
translation must still be equivalent when they run, so the calls below set
those keys too.

Calls, and what each one decides:

  0 full_other -- the first fixture, unchanged: outputformat "other" (the
    else branches), every key but "date_modified".
  1 minimal_html -- METADATA as the repository leaves it for an ontology with
    a URI and nothing else ("{no title found}"): every guard false, license
    None; only the first island runs.
  2 full_html -- real html formatting for license and repository, real
    dates, plus the three never-set guard keys: the ONLY call where the
    `sdo:dateModified` island runs (with "modified" set), and every other
    island too.
  3 full_adoc -- adoc formatting (`link:URI[curie]`) for license and
    repository: the adoc branches of both.
  4 md_repository -- md formatting: license takes the md branch; the
    repository's md branch is then overwritten by the else of the following
    `if ... == "adoc"` (an `if`, not an `elif`, in the repository), whose
    split('"')[1] raises IndexError: both sides must raise the same.
  5 modified_unbound -- "date_modified" set without "modified": the
    dateModified island reads an unbound local, UnboundLocalError on both
    sides (dateCreated has already been added to a graph that is dropped).
  6 falsy_values -- description "" and rights "" (the repository writes
    `str(o)` for both, so an empty literal is reachable): guarded by `is not
    None`, so both are added as empty literals; a translation that tested
    truth would drop them.  The license is a bare non-http string, kept as
    is by the repository, so html's split('"')[1] raises IndexError -- the
    second half of this case is therefore in call 7.
  7 falsy_no_license -- call 6 without the license: the empty description
    and rights reach the graph.

No warning is emitted by any call (checked by hand with
warnings.simplefilter("error") over the eight calls, both sides).
"""
from rdfeval.harness import run_pair


class _Fake:
    """Minimal stand-in for BaseProfile: only the two attributes the
    region reads (METADATA, outputformat)."""

    def __init__(self, outputformat="other", metadata=None):
        self.outputformat = outputformat
        self.METADATA = {
            "uri": "http://ex.org/doc",
            "title": "Test Doc",
            "created": "2020-01-01",
            "date_created": "yes",
            "modified": "2020-02-02",
            "description": "A description",
            "license": '"http://license.org/lic"',
            "rights": "Some rights",
            "copyright_year": "yes",
            "repository": '"http://ex.org/repo"',
        } if metadata is None else metadata

    def __eq__(self, other):
        return (isinstance(other, _Fake)
                and self.outputformat == other.outputformat
                and self.METADATA == other.METADATA)


def _fixture():
    return ((_Fake(),), {})


ONT = "http://example.org/def/onto"
LIC = "https://creativecommons.org/licenses/by/4.0/"
REPO = "https://github.com/example/onto"


def _case(outputformat, metadata):
    return lambda: ((_Fake(outputformat, dict(metadata)),), {})


VERDICT = run_pair(
    __file__,
    entry='_make_schemaorg_metadata',
    calls=[
        _fixture,
        _case("html", {"uri": ONT, "title": "{no title found}"}),
        _case("html", {
            "uri": ONT, "title": "Onto",
            "description": "<p>An ontology.</p>",
            "created": "2018-09-10", "modified": "2019-05-31",
            "license": f'<a href="{LIC}">cc:by</a>',
            "rights": "&copy; 2019 Example",
            "repository": f'<a href="{REPO}">{REPO}</a>',
            "date_created": "set", "date_modified": "set",
            "copyright_year": "set",
        }),
        _case("adoc", {
            "uri": ONT, "title": "Onto", "description": "An ontology.",
            "created": "2018-09-10", "modified": "2019-05-31",
            "license": f"link:{LIC}[cc:by]",
            "rights": "&copy; 2019 Example",
            "repository": f"link:{REPO}[{REPO}]",
            "date_created": "set", "date_modified": "set",
            "copyright_year": "set",
        }),
        _case("md", {
            "uri": ONT, "title": "Onto", "description": "An ontology.",
            "created": "2018-09-10",
            "license": f"[cc:by]({LIC})",
            "repository": f"[{REPO}]({REPO})",
        }),
        _case("html", {
            "uri": ONT, "title": "Onto", "created": "2018-09-10",
            "date_created": "set", "date_modified": "set",
        }),
        _case("html", {
            "uri": ONT, "title": "Onto", "description": "", "rights": "",
            "license": "All rights reserved",
        }),
        _case("html", {
            "uri": ONT, "title": "Onto", "description": "", "rights": "",
        }),
    ],
)
