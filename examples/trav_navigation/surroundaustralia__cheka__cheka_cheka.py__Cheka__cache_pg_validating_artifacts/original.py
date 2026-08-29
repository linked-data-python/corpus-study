# Extracted from surroundaustralia/cheka@31505e6804 : cheka/cheka.py
# region: Cheka._cache_pg_validating_artifacts (lines 148-226, stratum trav_navigation)
# licence of the source repository: see meta.json
import logging
from pathlib import Path
from rdflib import Graph, URIRef, Namespace
from rdflib.namespace import DCTERMS, PROF, RDF, SH
import uuid
import json
import pickle
from urllib.request import urlopen, Request

def _cache_pg_validating_artifacts(self, pg: Graph):
    # for each profile,
    #   get all its RDs with role 'validation' and conforms to SHACL,
    #       get all their artifacts' content
    #           lump them into a single validator graph for that Profile
    # store the validator per-profile in cache
    with open(self.VALIDATORS_MAP_FILE, "r") as f:
        map = json.load(f)

    for profile in pg.subjects(predicate=RDF.type, object=PROF.Profile):
        logging.debug("profile {}".format(profile))
        # if we already have a validator for this profile, do nothing
        if str(profile) in map.keys():
            logging.info("Using cached validators for Profile {}".format(profile))
        else:
            logging.info("Storing Profile {} in cache".format(profile))
            validator_graph = Graph()
            for rd in pg.objects(subject=profile, predicate=PROF.hasResource):
                if (rd, PROF.hasRole, self.ROLE.validation) in pg \
                   and (rd, DCTERMS.conformsTo, URIRef("https://www.w3.org/TR/shacl/")) in pg:
                    for artifact_uri in pg.objects(subject=rd, predicate=PROF.hasArtifact):
                        # artifacts are either local file URIs or HTTP/HTTPS URIs
                        # either way, RDFlib's parse() can handle it
                        logging.debug("Seen artifact URI {}".format(artifact_uri))
                        try:
                            if str(artifact_uri).startswith("http"):
                                logging.debug("Attempting to parse remote artifact {}".format(artifact_uri))
                                rdf_request_headers = {
                                    "Accept": "text/turtle,application/x-turtle, "
                                              "application/rdf+xml, "
                                              "application/ld+json"
                                }
                                req = Request(str(artifact_uri), None, rdf_request_headers)
                                with urlopen(req) as f:
                                    data = f.read().decode('utf-8')
                                validator_graph.parse(data=data)
                            elif str(artifact_uri).startswith("file"):
                                artifact_path = Path(str(artifact_uri).replace("file://", ""))
                                logging.debug("Attempting to parse local artifact {}".format(artifact_path))
                                if Path.is_file(artifact_path):
                                    logging.debug("Found file at location {}".format(artifact_path))
                                    validator_graph.parse(artifact_path)
                                else:
                                    artifact_path = Path(__file__).parent.parent / "tests" / "validators" / artifact_path
                                    if Path.is_file(artifact_path):
                                        logging.debug("Found file in tests validators dir {}".format(artifact_path))
                                        validator_graph.parse(artifact_path)
                                    else:
                                        raise ValueError("Validator local file indicated at {} but not found"
                                                         .format(artifact_path))
                            else:
                                raise ValueError("Validator not indicated as wither a web resource ('http...') or "
                                                 "a local file ('file:///...') in its URI so it cannot be found")
                        except Exception as e:
                            # do nothing, can't parse RDF
                            print(e)
                            logging.info(
                                "Attempted to dereference Artifact {} but got an error: {}"
                                    .format(artifact_uri, str(e))
                            )

            if len(validator_graph) > 0:
                # make up a file name for the validator
                fn = str(uuid.uuid4())
                # write to map
                map[str(profile)] = fn
                with open(self.VALIDATORS_MAP_FILE, "w") as f:
                    f.write(json.dumps(map, indent=4))
                # write validator content
                # validator_graph.serialize(destination=str(Path(self.VALIDATORS_DIR / (fn + ".ttl"))), format="turtle")
                with open(str(Path(self.VALIDATORS_DIR / (fn + ".p"))), "wb") as f:
                    pickle.dump(validator_graph, f)

    # warn about Profiles with no validators
    with open(self.VALIDATORS_MAP_FILE, "r") as f:
        map = json.load(f)
    for profile in pg.subjects(predicate=RDF.type, object=PROF.Profile):
        if str(profile) not in map.keys():
            logging.info("No validators are recorded for Profile {}".format(profile))
