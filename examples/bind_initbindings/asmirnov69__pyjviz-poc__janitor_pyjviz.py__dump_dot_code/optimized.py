# Extracted from asmirnov69/pyjviz-poc@3c1a20182b : janitor/pyjviz.py
# region: dump_dot_code (lines 14-77, stratum bind_initbindings)
# licence of the source repository: see meta.json
import html
from io import StringIO

def dump_dot_code(g):
    #ipdb.set_trace()
    out_fd = StringIO()

    print("""
    digraph G {
    rankdir = "LR"
    fontname="Helvetica,Arial,sans-serif"
    node [ 
      style=filled
      shape=rect
      pencolor="#00000044" // frames color
      fontname="Helvetica,Arial,sans-serif"
      shape=plaintext
    ]
    edge [fontname="Helvetica,Arial,sans-serif"]    
    """, file = out_fd)
    #print('rankdir = "TB"', file = out_fd)

    cmc_c = 0
    for cmc, cmc_label in g.query("select ?pp ?pl { ?pp rdf:type <pyj:CMC>; rdf:label ?pl }"):
        nodes = {}
        for s, s_shape, s_col in g.query("select ?s ?s_shape ?s_col { ?s rdf:type <pyj:DataFrame>; <pyj:df-shape> ?s_shape; <pyj:df-columns> ?s_col; <pyj:cmc> ?cmc}", initBindings = {'cmc': cmc}):
            if s not in nodes:
                nodes[s] = node_id = f'{cmc_c}_{len(nodes)}'
                cols = "\n".join(['<tr><td align="left"><FONT POINT-SIZE="8px">' + html.escape(x) + "</FONT></td></tr>" for x in s_col.toPython().split(",")])
                print(f"""node{node_id} [ 
                color="#88000022"
                shape = rect
                label = <<table border="0" cellborder="0" cellspacing="0" cellpadding="4">
                         <tr> <td> <b>{s.toPython()}</b><br/>shape: {s_shape.toPython()}</td> </tr>
                         <tr> <td align="left"><i>columns:</i><br align="left"/></td></tr>
                {cols}
                         </table>>
                ];""", file = out_fd)

        for s, mn in g.query("select ?s ?mn { ?s rdf:type <pyj:Method>; rdf:label ?mn; <pyj:cmc> ?cmc }", initBindings = {'cmc': cmc}):
            if s not in nodes:
                nodes[s] = node_id = f'{cmc_c}_{len(nodes)}'
                print(f'node{node_id} [ label = "{mn.toPython()}" ];', file = out_fd)

        #ipdb.set_trace()
        if cmc_label.toPython() != "none":
            print(f'subgraph cluster_{cmc_c} {{\nlabel = "{cmc_label.toPython()}";', file = out_fd)
            cmc_c += 1

        for df, method_call in g.query("select ?df ?m { ?df <pyj:method-call>|<pyj:method-call-arg> ?m. ?df <pyj:cmc> ?cmc. ?m <pyj:cmc> ?cmc }", initBindings = {'cmc': cmc}):
            print(f"node{nodes[df]} -> node{nodes[method_call]};", file = out_fd)

        for method_ret, df in g.query("select ?m ?df { ?m <pyj:method-return> ?df. ?df <pyj:cmc> ?cmc. ?m <pyj:cmc> ?cmc }", initBindings = {'cmc': cmc}):
            df, m = nodes[df], nodes[method_ret]
            print(f"node{m} -> node{df};", file = out_fd)

        if cmc_label.toPython() != "none":
            print("}", file = out_fd)

    print("}", file = out_fd)

    return out_fd.getvalue()
