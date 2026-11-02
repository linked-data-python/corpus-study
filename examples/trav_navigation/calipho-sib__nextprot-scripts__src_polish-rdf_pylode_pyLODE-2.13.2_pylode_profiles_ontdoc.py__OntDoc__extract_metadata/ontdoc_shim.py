# Context shim (see meta.json): the part of pyLODE 2.13.2's OntDoc that the
# region calls, from calipho-sib/nextprot-scripts@f03504ce5e
# (src/polish-rdf/pylode/pyLODE-2.13.2/pylode/profiles/base.py and ontdoc.py),
# so the region executes outside that vendored copy (pylode 2.13.2 is not
# installed, and the installed pylode 3.x has no such class). Method bodies are
# verbatim; only what the region never reaches is left out. Identical
# bindings for both representations.
#
#   * __init__ sets what BaseProfile.__init__ / OntDoc.__init__ and the first
#     lines of OntDoc._extract_metadata set before the region runs (the
#     METADATA sets that the region adds to, a default namespace, CLASSES).
#   * the Jinja templates agent.html / agent.md / orcid.md are the repository's
#     own files, inlined (orcid.html is reduced to its link: the SVG logo is
#     left out); agent.adoc and orcid.adoc do not exist
#     in the repository (as there), so an agent in "adoc" output raises
#     TemplateNotFound, as the original does.
import collections

from jinja2 import DictLoader, Environment
from rdflib import FOAF, SDO, Literal, URIRef

_TEMPLATES = {
    "agent.html": """{%- if url is not none %}
    <a href="{{url}}">{{name}}</a>
{%- else %}
    {{name}}
{%- endif %}
{%- if orcid %}
    {{orcid}}
{%- endif %}
{%- if email is not none %}
    (<a href="mailto:{{email}}">{{email}}</a>)
{%- endif %}
""",
    "agent.md": """{%- if url is not none -%}
    [{{ name }}]({{ url }})
{%- else -%}
    {{ name }}
{%- endif %}
{%- if orcid %}
    {{ orcid }}
{%- endif %}
{%- if email is not none %}
    [{{ email }}]({{ email }})
{%- endif %}
""",
    "orcid.html": """<a href="{{ orid_url }}">orcid</a>""",
    "orcid.md": """[[{{ orcid_id }}]({{ orcid_url }})]""",
}


class BaseProfile:
    def __init__(self, g, outputformat="html"):
        self.outputformat = outputformat
        self.G = g
        self.NAMESPACES = collections.OrderedDict()
        self.METADATA = {}

    def _load_template(self, template_file):
        return Environment(loader=DictLoader(_TEMPLATES)).get_template(template_file)

    def _get_namespace_from_uri(self, uri):
        # split on hash
        segments = uri.split("#")
        if len(segments) == 2:
            return segments[0] + "#"
        else:
            segments = uri.split("/")
            if len(segments) > 1:
                return "/".join(segments[0:-1]) + "/"
            else:
                return None

    def _get_uri_id(self, uri):
        # split on hash
        segments = uri.split("#")
        if len(segments) == 2:
            return segments[1]
        else:
            return uri.split("/")[-1]  # could return None if URI ends in /

    def _make_formatted_uri_basic(self, uri):
        curie = self._get_curie(uri)

        links = {
            "md": f"[{curie}]({uri})",
            "adoc": f"link:{uri}[{curie}]",
            "html": f'<a href="{uri}">{curie}</a>'
        }

        return links[self.outputformat]

    def _make_fragment_uri(self, uri):
        """This function should be overriden with profile-specific implementations
        """
        return self._make_formatted_uri_basic(uri)

    def _make_formatted_uri(self, uri):
        if uri.startswith(self.METADATA.get("default_namespace")):
            return self._make_fragment_uri(uri)
        else:
            # URI isn't in the default namespace, so use an absolut URI
            return self._make_formatted_uri_basic(uri)

    def _get_curie(self, uri):
        n = self._get_namespace_from_uri(str(uri))
        for k, v in self.NAMESPACES.items():
            if v == n or v.strip("/#") == n:
                if k == ":":
                    return "{}".format(self._get_uri_id(uri))
                else:
                    return "{}:{}".format(k, self._get_uri_id(uri))

        # if no match, return the original URI
        return uri

    def _make_agent_link(self, name, url=None, email=None, affiliation=None):
        if self.outputformat == "md":
            orcid = None
            if url is not None:
                if "orcid.org" in url:
                    orcid = BaseProfile._load_template(self, "orcid.md").render(
                        orcid_url=url,
                        orcid_id=url.replace("http://orcid.org/", "").replace("https://orcid.org/", "").strip("/")
                    )

            return BaseProfile._load_template(self, "agent.md").render(
                url=url,
                name=name,
                orcid=orcid,
                email=email.replace("mailto:", "") if email is not None else None,
                affiliation=affiliation
            )
        elif self.outputformat == "adoc":
            orcid = None
            if url is not None:
                if "orcid.org" in url:
                    orcid = BaseProfile._load_template(self, "orcid.adoc").render(
                        orcid_url=url,
                        orcid_id=url.replace("http://orcid.org/", "").replace("https://orcid.org/", "").strip("/")
                    )

            return BaseProfile._load_template(self, "agent.adoc").render(
                url=url,
                name=name,
                orcid=orcid,
                email=email.replace("mailto:", "") if email is not None else None,
                affiliation=affiliation
            )
        else:  # self.outputformat == "html":
            orcid = None
            if url is not None:
                if "orcid.org" in url:
                    orcid = BaseProfile._load_template(self, "orcid.html").render(
                        orcid_url=url,
                    )

            return BaseProfile._load_template(self, "agent.html").render(
                url=url,
                name=name,
                orcid=orcid,
                email=email.replace("mailto:", "") if email is not None else None,
                affiliation=affiliation
            )

    def _make_agent(self, agent_node):
        # we understand foaf:name, foaf:homepage & sdo:name & sdo:identifier & sdo:email (as a URI)
        # TODO: cater for other Agent representations

        name = None
        url = None
        email = None
        org_name = None
        org_url = None
        org_email = None
        for p, o in self.G.predicate_objects(subject=agent_node):
            print(p, o)
            if p in [FOAF.homepage, SDO.identifier]:
                url = str(o)
            elif p in [FOAF.name, SDO.name]:
                name = str(o)
            elif p in [FOAF.mbox, SDO.email]:
                email = str(o).split("/")[-1].split("#")[-1]  # remove base URI leaving only email address
            elif p in [SDO.memberOf, SDO.affiliation]:
                for p2, o2 in self.G.predicate_objects(subject=o):
                    if p2 in [FOAF.homepage, SDO.identifier, SDO.url]:  # TODO: split homepage form IDs, cater for rdfs:seeAlso
                        org_url = str(o2)
                    elif p2 in [FOAF.name, SDO.name]:
                        org_name = str(o2)
                    elif p in [FOAF.mbox, SDO.email]:
                        org_email = str(o2).split("/")[-1].split("#")[-1]  # remove base URI leaving only email address

        # use the URI of the Agent for its URL if no FOAF.homepage or SDO.identifier has been set
        if url is None and type(agent_node) == URIRef:
            url = str(agent_node)

        if name is None:
            if type(agent_node) == Literal:
                name = agent_node
            if type(agent_node) == URIRef:
                name = agent_node.split("/")[-1].split("#")[-1]
        agent = self._make_agent_link(name, url=url, email=email)

        if org_name is not None:
            org = self._make_agent_link(org_name, url=org_url, email=org_email)
            agent += " of " + org

        return agent


class OntDoc(BaseProfile):
    def __init__(self, g, outputformat="html"):
        super().__init__(g, outputformat=outputformat)
        self.CLASSES = collections.OrderedDict()
        self.PROPERTIES = collections.OrderedDict()
        self.NAMED_INDIVIDUALS = collections.OrderedDict()
        # BaseProfile._get_default_namespace (METADATA["default_namespace"]) and
        # the lines of OntDoc._extract_metadata that precede the region.
        self.METADATA["default_namespace"] = "http://example.org/onto#"
        self.METADATA["imports"] = set()
        self.METADATA["creators"] = set()
        self.METADATA["contributors"] = set()
        self.METADATA["publishers"] = set()
        self.METADATA["editors"] = set()
        self.METADATA["funders"] = set()
        self.METADATA["translators"] = set()

    def _make_fragment_uri(self, uri):
        """OntDoc Profile allows fragment URIs for Classes & Properties"""
        if self.PROPERTIES.get(uri) or self.CLASSES.get(uri):
            if self.PROPERTIES.get(uri):
                title = self.PROPERTIES[uri]["title"] \
                    if self.PROPERTIES[uri].get("title") is not None else self.PROPERTIES[uri]["fid"]
                uri = self.PROPERTIES[uri]["fid"]
            elif self.CLASSES.get(uri):
                title = self.CLASSES[uri]["title"] \
                    if self.CLASSES[uri].get("title") is not None else self.CLASSES[uri]["fid"]
                uri = self.CLASSES[uri]["fid"]

            links = {
                "md": f"[{title}](#{uri})",
                "adoc": f"link:#{uri}[{title}]",
                "html": f'<a href="#{uri}">{title}</a>'
            }

            return links[self.outputformat]
        else:
            return self._make_formatted_uri_basic(uri)

    def _make_formatted_uri(self, uri, type=None):
        link = super()._make_formatted_uri(uri)

        types = {
            "c": "class",
            "op": "object property",
            "fp": "functional property",
            "dp": "datatype property",
            "ap": "annotation property",
            "ni": "named individual"
        }

        if type not in types.keys():
            return link

        suffixes = {
            "md": f' ({type})',
            "adoc": f' ^{type}^',
            "html": f'<sup class="sup-{type}" title="{types[type]}">{type}</sup>'  # {}
        }

        return link + suffixes[self.outputformat]
