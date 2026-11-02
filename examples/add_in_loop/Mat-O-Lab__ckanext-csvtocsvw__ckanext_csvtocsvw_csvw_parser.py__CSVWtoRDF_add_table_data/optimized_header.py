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
        row_uri = data["about_url"] or "table-{TABLE}-gid-{GID}".format(table)
        columns = list(data["columns"].values())
        for index, row in enumerate(data["lines"]):
            # print(index, row)
            row_node = BNode()
            values_node = URIRef(row_uri.format(GID=index))
            row_num = index + data["dialect"][CSVW.skipRows] + data["dialect"][CSVW.headerRowCount]
            g += [(table, CSVW.row, row_node),
                  (row_node, RDF.type, CSVW.Row),
                  (row_node, CSVW.describes, values_node),
                  (row_node, CSVW.url, URIRef(f"{self.csv_url}/row={row_num}"))]
            for cell_index, cell in enumerate(row):
                # print(self.columns[cell_index])
                column_data = columns[cell_index]
                if column_data[CSVW.name] == Literal("GID"):
                    continue
                format = column_data.get(CSVW.format, XSD.string)
                unit = column_data.get(QUDT.unit)
                if format == XSD.double and isinstance(cell, str):
                    cell = cell.replace(".", "")[::-1].replace(",", ".", 1)[::-1]

                value_node = BNode()
                if format in XSD_NUMERIC:
                    g += [(value_node, RDF.type, QUDT.QuantityValue),
                          (value_node, QUDT.value, Literal(cell))]
                    if unit:
                        g.add((value_node, QUDT.unit, unit))
                elif format == XSD.anyURI:
                    Collection(g, value_node, list(map(URIRef, cell.split(" "))))
                else:
                    body_node = BNode()
                    g += [(value_node, RDF.type, OA.Annotation),
                          (value_node, OA.hasBody, body_node),
                          (body_node, RDF.type, OA.TextualBody),
                          (body_node, OA["format"], Literal("text/plain")),
                          (body_node, OA.value, Literal(cell, datatype=format))]

                # if isinstance(column,URIRef) and str(self.meta_root)!='file:///src/': #has proper uri
                #     g.add((value_node, column, Literal(cell)))

                if CSVW.aboutUrl in column_data:
                    predicate = URIRef(column_data[CSVW.aboutUrl].format(GID=index))
                else:
                    predicate = URIRef(column_data[CSVW.name])
                g.add((values_node, predicate, value_node))
    return g
