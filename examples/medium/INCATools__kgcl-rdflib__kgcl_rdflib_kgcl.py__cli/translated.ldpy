# Extracted from INCATools/kgcl-rdflib@7af638bbd7 : kgcl_rdflib/kgcl.py
# region: cli (lines 16-53, band medium)
# licence of the source repository: see meta.json
import logging
import sys
import click
import rdflib
from kgcl_schema.grammar import parser
from rdflib.util import guess_format
from kgcl_rdflib.apply import graph_transformer

@click.command()
@click.option("-i", "--graph", type=click.Path(), required=True)
@click.option("--kgcl-file", type=click.File("r"))
@click.option("--output", "-o", type=click.File(mode="wb"), default=sys.stdout)
@click.option("-v", "--verbose", count=True)
@click.argument("patch")
def cli(patch, verbose: int, graph, kgcl_file, output):
    """
    Modify graph based on KGCL commands.
    """
    if verbose >= 2:
        logging.basicConfig(level=logging.DEBUG)
    elif verbose == 1:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)
    # read kgcl commands from file
    if kgcl_file:
        kgcl_patch = kgcl_file.read()
    elif patch:
        kgcl_patch = patch
    else:
        raise ValueError(f"Must pass EITHER kgcl-file OR kgcl")

    # parser kgcl commands
    parsed_patch = parser.parse(kgcl_patch)
    logging.info(f"Patch: {patch}")

    # apply kgcl commands as SPARQL UPDATE queries to graph
    g = rdflib.Graph()
    # g.load(graph, format=guess_format(graph))
    g.parse(
        graph, format=guess_format(graph)
    )  # , format="nt") #TODO: this doesn't always work
    graph_transformer.apply_patch(parsed_patch, g)

    # save updated graph
    g.serialize(destination=output, format="ttl")


# --- demo harness (not part of the extracted region; added IDENTICALLY to
# original.py and translated.ldpy so the driver has an observable) ----------
# The region is a click Command, which cannot be called with plain arguments;
# the harness invokes it exactly as the console script does and reads back the
# Turtle it wrote.
import os

_DIR = os.path.dirname(os.path.abspath(__file__))
cli.main(
    args=[
        "-i", os.path.join(_DIR, "input.ttl"),
        "-o", os.path.join(_DIR, "patched.ttl"),
        "rename <http://example.org/x> from 'old' to 'new'",
    ],
    standalone_mode=False,
)
DEMO_GRAPH = rdflib.Graph()
DEMO_GRAPH.parse(os.path.join(_DIR, "patched.ttl"), format="ttl")
print(sorted(DEMO_GRAPH.serialize(format="nt").strip().splitlines()))
