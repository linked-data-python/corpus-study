# Extracted from TeamWalabi/agriculture-image-metadata@d34fe77241 : agri_image_meta/utils/sparql_queries.py
# region: query_images_by_location_and_properties (lines 176-176, stratum sparql_literal)
# licence of the source repository: see meta.json
#
# Context restored (see meta.json): the extracted region is a single bare
# statement with no enclosing function and no visible bindings for `g` or
# `query` (the context lines were empty). Both are restored here, copied
# verbatim from the real function at the commit above, for the call path
# where none of its optional filter/location arguments are supplied
# (image_number=image_name=cameraID=field_id=platform_id=plot_id=
# base_xyz_min=base_xyz_max=None) -- the only call path where `query` is a
# plain literal string: with every optional argument absent, `filter_str`
# and `optional_str` both collapse to "", so the f-string that builds
# `query` produces fixed text with no runtime-dependent parts. See
# translation_notes for the general function's f-string-assembled FILTER/
# OPTIONAL fragments (sparql_interpolated territory, not term-position, and
# out of scope for this literal-query call site).
from rdflib import Graph

g = Graph().parse("fixture.ttl")
query = """
    PREFIX agimage: <https://w3id.org/agri-image/>
    PREFIX exif: <http://www.w3.org/2003/12/exif/ns#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?image ?imageName ?imageNumber ?baseX ?baseY ?baseZ
           ?serialNumber ?fieldID ?platformID ?plotID
    WHERE {
        ?image a agimage:Image ;
            <https://w3id.org/agri-image/imageName> ?imageName .

        OPTIONAL { ?image <https://w3id.org/agri-image/imageNumber> ?imageNumber . }
        OPTIONAL { ?image <http://www.w3.org/2003/12/exif/ns#SerialNumber> ?serialNumber . }
        OPTIONAL { ?image <https://w3id.org/agri-image/fieldID> ?fieldID . }
        OPTIONAL { ?image <https://w3id.org/agri-image/platformID> ?platformID . }
        OPTIONAL { ?image <https://w3id.org/agri-image/plotID> ?plotID . }

        OPTIONAL {
            ?image <https://w3id.org/agri-image/baseXYZ> ?baseXYZList .
            ?baseXYZList rdf:first ?baseX ;
                         rdf:rest ?rest1 .
            ?rest1 rdf:first ?baseY ;
                   rdf:rest ?rest2 .
            ?rest2 rdf:first ?baseZ .
        }
    }
    ORDER BY ?imageName
    """
results = g.query(query)
# Appended for the driver (see meta.json): a bare rdflib Result / lazy match
# is not something run_pair's module-state comparison can judge equal
# (rdfeval.harness._comparable), so both sides also materialise the rows
# actually produced. Identical on both sides.
rows = [tuple(r) for r in results]
