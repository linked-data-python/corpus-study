# Extracted from RDFLib/prez@421ee0a9fe : prez/services/listings.py
# region: listing_profiles (lines 81-137, stratum ns_import_project)
# licence of the source repository: see meta.json
import prez_context
from rdflib import Literal, Namespace
from rdflib.namespace import GEO, RDF, PROF
from prez.reference_data.prez_ns import ALTREXT, OGCFEAT, PREZ
from prez.renderers.renderer import (
    return_annotated_rdf_for_oxigraph,
    return_from_graph,
    generate_geojson_extras,
    handle_alt_profile,
    generate_queryables_from_shacl_definition,
    create_collections_json,
    generate_link_headers,
    get_geojson_int_count,
)
from prez.services.curie_functions import get_curie_id_for_uri

async def listing_profiles(
    data_repo,
    system_repo,
    query_params,
    pmts,
):
    """
    Optimized listing function specifically for profiles.
    Uses DESCRIBE for data fetching and a separate query for counting.
    """
    limit = query_params.limit
    offset = limit * (int(query_params.page) - 1)

    # Query to get the profiles within the limit/offset using DESCRIBE on selected nodes
    describe_query = """
        DESCRIBE ?focus_node
        WHERE {{
            {{
                SELECT DISTINCT ?focus_node
                WHERE {{
                    ?focus_node a <{profile_class}> .
                }}
                LIMIT {limit} OFFSET {offset}
            }}
        }}
    """.format(profile_class=PROF.Profile, limit=limit, offset=offset)

    count_query = """
        CONSTRUCT {{ [] <https://prez.dev/count> ?count }}
        {{
            SELECT (COUNT(DISTINCT ?profile) as ?count)
            WHERE {{
                ?profile a <{profile_class}> .
            }}
        }}
    """.format(profile_class=PROF.Profile)
    profiles_g, _ = await system_repo.send_queries([describe_query, count_query], [])
    for profile_uri in profiles_g.subjects(RDF.type, PROF.Profile):
        curie = get_curie_id_for_uri(profile_uri)
        profiles_g += [
            (profile_uri, RDF.type, PREZ.FocusNode),
            (profile_uri, PREZ.link, Literal(f"/profiles/{curie}")),
        ]

    return await return_from_graph(
        profiles_g,
        pmts.selected["mediatype"],
        pmts.selected["profile"],
        pmts.generate_response_headers(),
        PROF.Profile,
        data_repo,
        system_repo,
        query_params,
    )
