# Extracted from RDFLib/pyLDAPI@c9be295b4e : pyldapi/renderer_container.py
# region: ContainerRenderer._generate_mem_profile_rdf (lines 260-316, stratum ns_def_local)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS

def _generate_mem_profile_rdf(self):
    g = Graph()

    LDP = Namespace('http://www.w3.org/ns/ldp#')
    g.bind('ldp', LDP)

    XHV = Namespace('https://www.w3.org/1999/xhtml/vocab#')
    g.bind('xhv', XHV)

    u = URIRef(self.instance_uri)
    g += [(u, RDF.type, RDF.Bag), (u, RDFS.label, Literal(self.label)),
          (u, RDFS.comment, Literal(self.comment, lang='en'))]
    for member in self.members:
        if "uri" in member:
            member_uri = URIRef(member["uri"])
            g.add((member_uri, RDFS.label, Literal(member["title"])))
        elif isinstance(member, tuple):
            member_uri = URIRef(member[0])
            g.add((member_uri, RDFS.label, Literal(member[1])))
        else:
            member_uri = URIRef(member)
        g.add((u, RDFS.member, member_uri))

    # other Query String Arguments
    other_qsas_str = "".join(x + "=" + v + "&" for x, v in self.request.query_params.items()
                             if x not in ["page", "per_page"])

    page_uri_str_nonum = "{}?{}per_page={}&page=".format(self.instance_uri, other_qsas_str, self.per_page)
    page_uri = URIRef(page_uri_str_nonum + str(self.page))

    # pagination
    # this page
    g += [(page_uri, RDF.type, LDP.Page), (page_uri, LDP.pageOf, u),
          # links to other pages
          (page_uri, XHV.first, URIRef(page_uri_str_nonum + '1')),
          (page_uri, XHV.last, URIRef(page_uri_str_nonum + str(self.last_page)))]

    if self.page != 1:
        g.add((page_uri, XHV.prev, URIRef(page_uri_str_nonum + str(self.page - 1))))

    if self.page != self.last_page:
        g.add((page_uri, XHV.next, URIRef(page_uri_str_nonum + str(self.page + 1))))

    if self.parent_container_uri is not None:
        parent_uri = URIRef(self.parent_container_uri)
        g += [(parent_uri, RDF.Bag, u), (parent_uri, RDFS.member, u)]
        if self.parent_container_label is not None:
            g.add((parent_uri, RDFS.label, Literal(self.parent_container_label)))
    return g
