"""Validation driver for calipho-sib__nextprot-scripts__src_polish-rdf_pylode_pyLODE-2.13.2_pylode_profiles_ontdoc.py__OntDoc__extract_metadata.

The region is the loop of a method: it fills `self.METADATA` from the
ontology's triples in `self.G`. Run as a function of `self`
(`extract_metadata_region`), it returns None, so what the harness compares is
what the call did to its argument -- the OntDoc stand-in of ontdoc_shim.py,
whose graph, `METADATA` (strings, sets of formatted agents) and the lines it
prints are compared after the call, as is an exception.

The `print(p, o)` of the repository's `_make_agent` prints blank-node
identifiers, which differ between the two sides' parses of a fixture: they
are masked, the only thing the filter drops.

Cases, and what each decides:

  rich_html     fixture.ttl, "html": every property the region reads, every
                kind of agent, two imports (one inside the default namespace),
                two repositories behind prov:wasGeneratedBy, markdown rendered
                for description and historyNote; a class and a blank node carry
                look-alike metadata that must not be read.
  rich_md       the same graph, "md": description and historyNote kept as is,
                agents rendered by the md template.
  rich_adoc     the same graph, "adoc": the first agent met raises
                TemplateNotFound (no agent.adoc in the repository) after the
                triples visited before it were written -- the partial
                METADATA tells the order of the reads apart.
  plain_adoc    fixture_plain.ttl, "adoc": strings kept as is, non-http source
                and license, a literal behind prov:wasGeneratedBy, no agent.
  plain_md      the same, "md".
  plain_html    the same, "html": rendered markdown, rights with all three
                replacements.
  generated     fixture_generated.ttl: prov:wasGeneratedBy and the
                doap:repository of the activity, with no sdo:codeRepository
                to overwrite it (in rich_* it does); a repository on another
                activity is not read.
  bare          fixture_minimal.ttl: no title -> the placeholder.
  bare_titled   the same, with a title already in METADATA: the placeholder
                must not replace it.
  two           fixture_two.ttl: two ontologies, the loop runs twice.
  none          fixture_none.ttl: no ontology; METADATA is left untouched.
"""
import re
from pathlib import Path

from rdflib import Graph

from rdfeval.harness import run_pair
from ontdoc_shim import OntDoc

HERE = Path(__file__).resolve().parent


def _case(fixture, outputformat, **metadata):
    def make():
        doc = OntDoc(Graph().parse(HERE / fixture, format="turtle"), outputformat)
        doc.METADATA.update(metadata)
        return (doc,), {}
    return make


CALLS = [
    _case("fixture.ttl", "html"),                          # rich_html
    _case("fixture.ttl", "md"),                            # rich_md
    _case("fixture.ttl", "adoc"),                          # rich_adoc
    _case("fixture_plain.ttl", "adoc"),                    # plain_adoc
    _case("fixture_plain.ttl", "md"),                      # plain_md
    _case("fixture_plain.ttl", "html"),                    # plain_html
    _case("fixture_generated.ttl", "html"),                # generated
    _case("fixture_minimal.ttl", "html"),                  # bare
    _case("fixture_minimal.ttl", "html", title="Preset"),  # bare_titled
    _case("fixture_two.ttl", "html"),                      # two
    _case("fixture_none.ttl", "html"),                     # none
]


def _mask_bnodes(text):
    return re.sub(r"\b[nN][0-9a-f]{20,}\b", "<bnode>", text)


VERDICT = run_pair(
    __file__,
    entry='extract_metadata_region',
    calls=CALLS,
    stdout_filter=_mask_bnodes,
)
