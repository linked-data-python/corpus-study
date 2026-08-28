# Extracted from deepin-community/lv2@1240cf5811 : scripts/lv2_build_index.py
# region: index_row (lines 97-140, stratum trav_single_value)
# licence of the source repository: see meta.json
import rdflib
doap = rdflib.Namespace("http://usefulinc.com/ns/doap#")
lv2 = rdflib.Namespace("http://lv2plug.in/ns/lv2core#")
owl = rdflib.Namespace("http://www.w3.org/2002/07/owl#")

def index_row(model, spec, root_uri, online):
    "Return the row for a spec as an HTML string."

    # Get version
    minor = 0
    micro = 0
    try:
        minor = int(model.value(spec, lv2.minorVersion, None, any=False))
        micro = int(model.value(spec, lv2.microVersion, None, any=False))
    except rdflib.exceptions.UniquenessError:
        _warn(f"{spec} has no unique valid version")
        return ""

    row = "<tr>"

    # Specification and API
    row += _spec_link_columns(
        spec,
        root_uri,
        model.value(spec, doap.name, None).replace("LV2 ", ""),
        online,
    )

    # Description
    row += _spec_description_column(model, spec)

    # Version
    row += f"<td>{minor}.{micro}</td>"

    # Status
    deprecated = model.value(spec, owl.deprecated, None)
    deprecated = deprecated and str(deprecated) not in ["0", "false"]
    if minor == 0:
        row += '<td><span class="error">Experimental</span></td>'
    elif deprecated:
        row += '<td><span class="warning">Deprecated</span></td>'
    elif micro % 2 == 0:
        row += '<td><span class="success">Stable</span></td>'
    else:
        row += '<td><span class="warning">Development</span></td>'

    row += "</tr>"

    return row
