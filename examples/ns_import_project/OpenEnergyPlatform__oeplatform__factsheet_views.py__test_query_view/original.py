# Extracted from OpenEnergyPlatform/oeplatform@ff28ef6390 : factsheet/views.py
# region: test_query_view (lines 1403-1412, stratum ns_import_project)
# licence of the source repository: see meta.json
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.utils.cache import patch_response_headers
from rdflib import RDF, Graph, Literal, URIRef
from factsheet.oekg.connection import oekg, oeo, oeo_owl
from factsheet.oekg.namespaces import DC, OBO, OEKG, OEO, RDFS, XSD

def test_query_view(request, *args, **kwargs):
    scenario_region = URIRef(
        "https://openenergyplatform.org/ontology/oekg/region/UnitedKingdomOfGreatBritainAndNorthernIreland"  # noqa: E501
    )
    for s, p, o in oekg.triples((scenario_region, RDFS.label, None)):
        if str(o) == "None":
            oekg.remove((s, p, o))
    response = JsonResponse("Done!", safe=False, content_type="application/json")
    patch_response_headers(response, cache_timeout=1)
    return response
