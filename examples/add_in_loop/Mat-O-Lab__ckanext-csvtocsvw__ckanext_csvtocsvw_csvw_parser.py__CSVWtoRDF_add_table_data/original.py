# Extracted from Mat-O-Lab/ckanext-csvtocsvw@a8856596aa : ckanext/csvtocsvw/csvw_parser.py
# region: CSVWtoRDF.add_table_data (lines 287-373, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.namespace import CSVW, RDF, XSD
QUDT = Namespace("http://qudt.org/schema/qudt/")
OA = Namespace("http://www.w3.org/ns/oa#")
XSD_NUMERIC = [XSD.float, XSD.decimal, XSD.integer, XSD.double]

def add_table_data(self, g: Graph) -> Graph:
    """_summary_

    Args:
        g (Graph): Grapg to add the table data tripells to

    Returns:
        Graph: Input Graph return with triples of table added
    """
    for table, data in self.tables.items():
        print("table: {}, about_url: {}".format(table, data["about_url"]))
        # g.add((table_group,CSVW.table, table))
        g.add((table, RDF.type, CSVW.Table))
        if data["about_url"]:
            row_uri = data["about_url"]
        else:
            row_uri = "table-{TABLE}-gid-{GID}".format(table)
        columns = list(data["columns"].items())
        for index, row in enumerate(data["lines"]):
            # print(index, row)
            row_node = BNode()
            values_node = URIRef(row_uri.format(GID=index))
            g.add((table, CSVW.row, row_node))
            g.add((row_node, RDF.type, CSVW.Row))
            g.add((row_node, CSVW.describes, values_node))
            row_num = (
                index
                + data["dialect"][CSVW.skipRows]
                + data["dialect"][CSVW.headerRowCount]
            )
            g.add(
                (
                    row_node,
                    CSVW.url,
                    URIRef("{}/row={}".format(self.csv_url, row_num)),
                )
            )
            for cell_index, cell in enumerate(row):
                # print(self.columns[cell_index])
                column_data = columns[cell_index][1]
                if column_data[CSVW.name] == Literal("GID"):
                    continue
                format = column_data.get(CSVW.format, XSD.string)
                unit = column_data.get(QUDT.unit, None)
                if format == XSD.double and isinstance(cell, str):
                    cell = cell.replace(".", "")
                    cell = cell[::-1].replace(",", ".", 1)[::-1]

                if format in XSD_NUMERIC:
                    value_node = BNode()
                    g.add((value_node, RDF.type, QUDT.QuantityValue))
                    g.add((value_node, QUDT.value, Literal(cell)))
                    if unit:
                        g.add((value_node, QUDT.unit, unit))
                elif format == XSD.anyURI:
                    # see if its a list of uris
                    if len(cell.split(" ")) >= 1:
                        value_node = BNode()
                        uris = list(map(URIRef, cell.split(" ")))
                        Collection(g, value_node, uris)
                    else:
                        value_node = URIRef(cell)
                else:
                    value_node = BNode()
                    body_node = BNode()
                    g.add((value_node, RDF.type, OA.Annotation))
                    g.add((value_node, OA.hasBody, body_node))
                    g.add((body_node, RDF.type, OA.TextualBody))
                    g.add((body_node, OA["format"], Literal("text/plain")))
                    g.add((body_node, OA.value, Literal(cell, datatype=format)))

                # if isinstance(column,URIRef) and str(self.meta_root)!='file:///src/': #has proper uri
                #     g.add((value_node, column, Literal(cell)))

                if CSVW.aboutUrl in column_data.keys():
                    aboutUrl = column_data[CSVW.aboutUrl]
                    g.add(
                        (
                            values_node,
                            URIRef(aboutUrl.format(GID=index)),
                            value_node,
                        )
                    )
                else:
                    name = column_data[CSVW.name]
                    g.add((values_node, URIRef(name), value_node))
    return g
