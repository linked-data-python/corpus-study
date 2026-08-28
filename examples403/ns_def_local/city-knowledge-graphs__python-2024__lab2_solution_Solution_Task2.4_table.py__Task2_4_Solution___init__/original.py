# Extracted from city-knowledge-graphs/python-2024@81a87ded33 : lab2/solution/Solution_Task2.4_table.py
# region: Task2_4_Solution.__init__ (lines 14-33, stratum ns_def_local)
# licence of the source repository: see meta.json
from rdflib import Graph
from rdflib import Namespace
import pandas as pd

def __init__(self):

     #1. GRAPH INITIALIZATION

    #Empty graph
    self.g = Graph()

    #Example namespace for this lab
    self.lab2_ns_str= "http://www.semanticweb.org/ernesto/in3067-inm713/lab2/"

    #Special namspaces class to create directly URIRefs in python.           
    self.lab2 = Namespace(self.lab2_ns_str)

    #Prefixes for the serialization
    self.g.bind("lab2", self.lab2)


    #Load data in dataframe  
    self.file="../data/lab2_companies_file.csv"
    self.data_frame = pd.read_csv(self.file, sep=',', quotechar='"',escapechar="\\")
