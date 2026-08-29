# Extracted from sap218/jabberwocky@de486df812 : 01_converter/gimble.py
# region: <module> (lines 162-274, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib import RDF, RDFS, OWL, DCTERMS
import pandas as pd
import re
cols_for_metadata = list(defined_annotations)
domains = xls.sheet_names
uri = Namespace(namespace+"#")
o = Graph()

for superclass in domains:


    #
    # start tab here
    #


    superclass = superclass.strip().lower()
    #print("\n%s" % superclass)


    superclass_iri = get_next_iri()
    superclass_defined = uri[superclass_iri]
    o.add((superclass_defined, RDF.type, OWL.Class))
    o.add((superclass_defined, RDFS.label, Literal(superclass, lang="en")))



    df = pd.read_excel(xls, superclass)

    classes = list(set(df["class"]))

    for classs in classes:

        class_iri = get_next_iri()
        class_defined = uri[class_iri]
        o.add((class_defined, RDF.type, OWL.Class))
        o.add((class_defined, RDFS.label, Literal(classs, lang="en")))
        o.add((class_defined, RDFS.subClassOf, superclass_defined))

        df_filtered = df[df["class"] == classs]

        if len(df_filtered) == 1: # for classes only

            if "subclass" in list(df_filtered): # if class exists but no subclass

                if pd.isna(list(df_filtered["subclass"])[0]): # for only classes

                    for col in cols_for_metadata:
                        if pd.isna(list(df_filtered[col])[0]):
                            pass
                        else:
                            if ";" in list(df_filtered[col])[0]:
                                items = re.split(r'[;,/]', list(df_filtered[col])[0])
                                items = [x.strip().lower() for x in items]
                                for item in items:
                                    o.add((class_defined, defined_annotations[col], Literal(item) ))
                            else:
                                o.add((class_defined, defined_annotations[col], Literal(list(df_filtered[col])[0]) ))

                else:
                    subclass_iri = get_next_iri()
                    subclass_defined = uri[subclass_iri]
                    o.add((subclass_defined, RDF.type, OWL.Class))
                    o.add((subclass_defined, RDFS.label, Literal(list(df_filtered["subclass"])[0], lang="en")))
                    o.add((subclass_defined, RDFS.subClassOf, class_defined))

                    for col in cols_for_metadata:
                        if pd.isna(list(df_filtered[col])[0]):
                            pass
                        else:
                            if ";" in list(df_filtered[col])[0]:
                                items = re.split(r'[;,/]', list(df_filtered[col])[0] )
                                items = [x.strip().lower() for x in items]
                                for item in items:
                                    o.add((subclass_defined, defined_annotations[col], Literal(item) ))
                            else:
                                o.add((class_defined, defined_annotations[col], Literal(list(df_filtered[col])[0]) ))


            else: # for tabs with only class 

                for col in cols_for_metadata:
                    if pd.isna(list(df_filtered[col])[0]):
                        pass
                    else:
                        if ";" in list(df_filtered[col])[0]:
                            items = re.split(r'[;,/]', list(df_filtered[col])[0])
                            items = [x.strip().lower() for x in items]
                            for item in items:
                                o.add((class_defined, defined_annotations[col], Literal(item) ))
                        else:
                            o.add((class_defined, defined_annotations[col], Literal(list(df_filtered[col])[0]) ))


        else: # for multiple subclasses per class

            for index, row in df_filtered.iterrows():
                row = dict(row)

                #print(classs, class_iri)
                subclasss = row["subclass"]

                subclass_iri = get_next_iri()
                #print(subclasss, subclass_iri)
                subclass_defined = uri[subclass_iri]
                o.add((subclass_defined, RDF.type, OWL.Class))
                #o.add((subclass_defined, RDFS.label, Literal(row["subclass"], lang="en")))
                o.add((subclass_defined, RDFS.label, Literal(subclasss, lang="en")))
                o.add((subclass_defined, RDFS.subClassOf, class_defined))

                for col in cols_for_metadata:
                    if pd.isna(row[col]):
                        pass
                    else:
                        if ";" in row[col]:
                            items = re.split(r'[;,/]',  row[col])
                            items = [x.strip().lower() for x in items]
                            for item in items:
                                o.add((subclass_defined, defined_annotations[col], Literal(item) ))
                        else:
                            o.add((subclass_defined, defined_annotations[col], Literal(row[col]) ))
