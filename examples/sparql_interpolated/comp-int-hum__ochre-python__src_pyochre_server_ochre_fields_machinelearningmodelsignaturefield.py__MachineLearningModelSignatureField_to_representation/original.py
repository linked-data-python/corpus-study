# Extracted from comp-int-hum/ochre-python@8392c11405 : src/pyochre/server/ochre/fields/machinelearningmodelsignaturefield.py
# region: MachineLearningModelSignatureField.to_representation (lines 43-94, stratum sparql_interpolated)
# licence of the source repository: see meta.json
# Context shim: django.conf.settings, django.urls.reverse and
# importlib.resources.files("pyochre") are not available outside the project.
from ochre_context import settings, reverse, files
from rdflib.namespace import RDF, RDFS, Namespace
OCHRE = Namespace(settings.OCHRE_NAMESPACE)

def to_representation(self, object, *argv, **argd):
    sig = object.signature
    in_field, out_field = None, None
    in_widget = None
    mvq_string = files("pyochre").joinpath(
        "data/model_visualization_query.sparql"
    ).read_text()
    for s, p, o in sig.triples((None, OCHRE["simpleFormat"], None)):
        if s == OCHRE["Input"]:
            in_widget = input_widget_map[o]
        elif s == OCHRE["Output"]:
            out_widget = output_widget_map[o]
    tabs = {}
    self.style["endpoint_url"] = reverse("api:machinelearningmodel-apply", args=(object.id,))
    for result in sig.query("PREFIX ochre: <{}>\n".format(settings.OCHRE_NAMESPACE) + mvq_string):
        s = result["s"]
        p = result["p"]
        o = result["o"]
        tabs[s] = tabs.get(s, {})
        tabs[s][p] = tabs[s].get(p, [])
        tabs[s][p].append(o)
    tab_list = []
    for tab in tabs.values():
        props = {"endpoint" : self.style["endpoint_url"]}
        for prop, val in tab.items():
            props[prop] = props.get(prop, []) + val
        widget_type = tab[OCHRE["instanceOf"]][0]
        widget_label = tab[OCHRE["hasDescription"]][0]
        widget_class = tab.get(OCHRE["hasLabel"], ["Unknown"])[0]
        # if widget_type in widget_map:
        #     tab_list.append(
        #         {
        #             "title" : widget_label,
        #             "html" : widget_map.get(widget_type)(props=props).render(
        #                 props[OCHRE["hasDescription"]][0],
        #                 object
        #             )
        #         }
        #     )
    if len(tab_list) == 0:
        self.style["base_template"] = "interaction.html"
        self.style["rendered_widget"] = {"html" : "There does not seem to be anything to show about this model."}
    elif len(tab_list) == 1:
        self.style["base_template"] = "interaction.html"
        self.style["rendered_widget"] = tab_list[0]
    else:
        self.style["base_template"] = "tabs_interaction.html"
        self.style["tabs"] = tab_list
    self.style["hide_label"] = True
    self.style["interactive"] = True
    self.style["object"] = object
    return str(object)
