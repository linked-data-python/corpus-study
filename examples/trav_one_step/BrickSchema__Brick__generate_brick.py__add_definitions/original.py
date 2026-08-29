# Extracted from BrickSchema/Brick@c12949f236 : generate_brick.py
# region: add_definitions (lines 687-764, stratum trav_one_step)
# licence of the source repository: see meta.json
import logging
from pathlib import Path
import csv
from rdflib import Graph, Literal, BNode, URIRef
from bricksrc.namespaces import (
    BRICK,
    BSH,
    REC,
    RDF,
    OWL,
    RDFS,
    TAG,
    SOSA,
    SKOS,
    QUDT,
    VCARD,
    SH,
    REF,
)
logger = logging.getLogger(__name__)
G = brickschema.Graph()

def add_definitions(graph=G):
    """
    Adds definitions for Brick subclasses through SKOS.definitions.

    This parses the definitions from ./bricksrc/definitions.csv and
    adds it to the graph. If available, adds the source information of
    through RDFS.seeAlso.
    """
    with open(Path("./bricksrc/definitions.csv"), encoding="utf-8") as dictionary_file:
        dictionary = csv.reader(dictionary_file)

        header = next(dictionary)

        # add definitions, citations to the graph
        for definition in dictionary:
            term = URIRef(definition[0])
            if len(definition) > len(header):
                raise ValueError(
                    f"The term '{term}' has more elements than expected. Please check the format."
                )
            if len(definition[1]):
                graph.add((term, SKOS.definition, Literal(definition[1], lang="en")))
            if len(definition) > 2 and definition[2]:
                # add seeAlso only if provided
                graph.add((term, RDFS.seeAlso, URIRef(definition[2])))

    qstr = """
    select ?param where {
      ?param rdfs:subClassOf* brick:Limit.
    }
    """
    limit_def_template = "A parameter that places {direction} bound on the range of permitted values of a {setpoint}."
    params = [row["param"] for row in graph.query(qstr)]
    for param in params:
        words = param.split("#")[-1].split("_")
        prefix = words[0]

        # define "direction" component of Limit definition
        if prefix == "Min":
            direction = "a lower"
        elif prefix == "Max":
            direction = "an upper"
        else:
            prefix = None
            direction = "a lower or upper"

        # define the "setpoint" component of a Limit definition
        if param.split("#")[-1] in ["Max_Limit", "Min_Limit", "Limit"]:
            setpoint = "Setpoint"
        else:
            if prefix:
                setpoint = "_".join(words[1:-1])
            else:
                setpoint = "_".join(words[:-1])

        if setpoint.split("_")[-1] != "Setpoint":
            # While Limits are a boundary of a Setpoint, the associated
            # Setpoint names are not explicit in class's names. Thus needs
            # to be explicily added for the definition text.
            setpoint = setpoint + "_Setpoint"
            logger.info(f"Inferred setpoint: {setpoint}")
        limit_def = limit_def_template.format(direction=direction, setpoint=setpoint)
        is_alias = list(graph.objects(subject=param, predicate=BRICK.aliasOf))
        if (
            param != BRICK.Limit and len(is_alias) == 0
        ):  # definition already exists for Limit
            graph.add((param, SKOS.definition, Literal(limit_def, lang="en")))
        class_exists = graph.query(
            f"""select ?class where {{
            BIND(brick:{setpoint} as ?class)
            ?class rdfs:subClassOf* brick:Class.
        }}
        """  # noqa
        ).bindings
        if not class_exists:
            logging.warning(
                f"WARNING: {setpoint} does not exist in Brick for {param}."  # noqa
            )
