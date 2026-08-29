# Extracted from fair-workflows/fairworkflows@363a759032 : fairworkflows/rdf_wrapper.py
# region: RdfWrapper._uri_is_subject_in_rdf (lines 219-234, stratum trav_existence)
# licence of the source repository: see meta.json
import warnings
import rdflib

@staticmethod
def _uri_is_subject_in_rdf(uri: str, rdf: rdflib.Graph, force: bool):
    """Check whether uri is a subject in the rdf.

    Args:
        rdf: The RDF graph
        uri: Uri of the object
        force: Toggle raising an error (force=False) or just a warning (force=True)
    """
    if rdflib.URIRef(uri) not in rdf.subjects():
        message = (f"Provided URI '{uri}' does not "
                   f"match any subject in provided rdf graph.")
        if force:
            warnings.warn(message, UserWarning)
        else:
            raise ValueError(message + " Use force=True to suppress this error")
