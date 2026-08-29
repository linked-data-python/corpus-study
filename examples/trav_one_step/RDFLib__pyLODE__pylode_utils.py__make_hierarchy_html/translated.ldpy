# Extracted from RDFLib/pyLODE@0d0471fb99 : pylode/utils.py
# region: make_hierarchy_html (lines 966-1025, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, URIRef

def make_hierarchy_html(
    ont: Graph, obj_class: URIRef, parent_indicator: URIRef, fids: dict
):
    if (None, RDF.type, obj_class) in ont:
        items = []
        for s in ont.subjects(RDF.type, obj_class):
            if not isinstance(s, BNode):
                name = ont.value(s, DCTERMS.title | SDO.name | SKOS.prefLabel)
                if name is None:
                    name = make_title_from_iri(s)
                c = {
                    "iri": str(s),
                    "name": str(
                        name
                    ),  # need 2 x for OntPub (title) and VocPub (prefLabel) profiles
                }
                for o2 in ont.objects(s, parent_indicator):
                    if not isinstance(o2, BNode):
                        c["parent"] = str(o2)
                items.append(c)

        def build_html_tree(items):
            # Index items by id
            by_id = {item["iri"]: dict(item, children=[]) for item in items}

            roots = []

            # Build tree structure
            for item in by_id.values():
                parent = item.get("parent")
                if parent and parent in by_id:
                    by_id[parent]["children"].append(item)
                else:
                    roots.append(item)

            # Recursive renderer
            def render_nodes(nodes):
                container = ul(_class="hierarchy")
                for node in sorted(
                    nodes,
                    key=lambda node: (
                        node["name"].casefold(),
                        node["name"],
                        node["iri"],
                    ),
                ):
                    node_li = li(
                        a(
                            node["name"],
                            href="#" + generate_fid(None, node["iri"], fids),
                        )
                    )
                    if node["children"]:
                        node_li.add(render_nodes(node["children"]))
                    container.add(node_li)
                return container

            return render_nodes(roots)

        return div(build_html_tree(items), _class="hierarchy")
