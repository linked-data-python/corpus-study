# Extracted from eliozo/worksheet-generation-with-llms@c065efff55 : scripts/rdfgen/csv_to_nested_table.py
# region: addToRdfGraph (lines 54-96, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, URIRef, Literal, RDF, XSD
import rdflib
eliozo_ns = "http://www.dudajevagatve.lv/eliozo#"
RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

def addToRdfGraph(g, problem_id, youtube_id, video_title, bookmarks):
    global eliozo_ns
    global SKOS_NS
    global RDF_NS
    problem_node = rdflib.URIRef(eliozo_ns + problem_id)
    problem_video_property = rdflib.URIRef(eliozo_ns + 'hasVideo')
    video_resource = rdflib.BNode()

    rdf_type_property = rdflib.URIRef(RDF_NS + "type")
    rdf_type_value = rdflib.URIRef(eliozo_ns + "Video")

    youtube_id_property = rdflib.URIRef(eliozo_ns+'videoYoutube')
    youtube_id_value = rdflib.term.Literal(youtube_id)

    video_title_property = rdflib.URIRef(eliozo_ns + "videoTitle")
    video_title_value = rdflib.term.Literal(video_title)


    g.add((problem_node, problem_video_property, video_resource))
    g.add((video_resource, rdf_type_property, rdf_type_value))
    g.add((video_resource, youtube_id_property, youtube_id_value))
    g.add((video_resource, video_title_property, video_title_value))

    video_bookmark_property = rdflib.URIRef(eliozo_ns + "videoBookmarks")

    video_bookmarks = rdflib.BNode()
    g.add((video_resource, video_bookmark_property, video_bookmarks))

    bookmarks_type_property = rdflib.URIRef(RDF_NS + "Seq")
    g.add((video_bookmarks, rdf_type_property, bookmarks_type_property))

    count = 1
    for (tstamp, bmtext) in bookmarks:
        seq_property = rdflib.URIRef(RDF_NS + "_{}".format(count))
        current_bookmark = rdflib.BNode()
        g.add((video_bookmarks, seq_property, current_bookmark))
        current_bookmark_tstamp_property = rdflib.URIRef(eliozo_ns + "videoBookmarkTstamp")
        g.add((current_bookmark, current_bookmark_tstamp_property, rdflib.term.Literal(tstamp, datatype=XSD.integer)))
        current_bookmark_text_property = rdflib.URIRef(eliozo_ns + "videoBookmarkText")
        g.add((current_bookmark, current_bookmark_text_property, rdflib.term.Literal(bmtext)))
        current_bookmark_rdf_type_property = rdflib.URIRef(RDF_NS + "type")
        g.add((current_bookmark, current_bookmark_rdf_type_property, rdflib.URIRef(eliozo_ns + "VideoBookmark")))
        count += 1
