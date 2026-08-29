# Extracted from city-knowledge-graphs/python-2023@eadf6f94a9 : lab5/solution/lab5_solution.py
# region: Lab5Solution.SimpleUniqueMapping (lines 70-144, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import URIRef, BNode, Literal
from rdflib.namespace import OWL, RDF, RDFS, FOAF, XSD

def SimpleUniqueMapping(self):
    #This mapping creates an several transformations (i.e., triples) in one go.
    #Unlike the modular approach (see ConvertCSVToRDF) this solution is less flexible to adaptations  

    #Format:
    #0        1             2    3        4        5        6        7            8         9
    #city     city_ascii    lat  lng    country    iso2    iso3    admin_name    capital    population                        
    for row in self.data_frame.itertuples(index=False):
        #print(row[0])

        #we avoid NaN values, one could add more safety filters. This case is problematic in this dataset                            
        if (self.is_nan(row[1]) or self.is_nan(row[4])): 
            continue

        entity_city_uri = self.lab5_ns_str + row[1].lower().replace(" ", "_").replace("(", "").replace(")", "")
        entity_country_uri = self.lab5_ns_str + row[4].lower().replace(" ", "_").replace("(", "").replace(")", "")

        #Types triples
        #Using self.lab5.City is equivalent to using URIRef(self.lab5_ns_str = "City")
        self.g.add((URIRef(entity_city_uri), RDF.type, self.lab5.City))     #e.g. lab5:london rdf:type lab5:City
        self.g.add((URIRef(entity_country_uri), RDF.type, self.lab5.Country))  #e.g. lab5united_kingdom rdf:type lab5:Country

        #City Names triples            
        self.g.add((URIRef(entity_city_uri), self.lab5.name_ascii, Literal(row[1], datatype=XSD.string)))
        if (not self.is_nan(row[0])):
            self.g.add((URIRef(entity_city_uri), self.lab5.name, Literal(row[0], datatype=XSD.string)))
        if (not self.is_nan(row[7])):
            self.g.add((URIRef(entity_city_uri), self.lab5.admin_name, Literal(row[7], datatype=XSD.string)))


        #Lat & long
        if (not self.is_nan(row[2])):
            self.g.add((URIRef(entity_city_uri), self.lab5.latitude, Literal(row[2], datatype=XSD.float)))
        if (not self.is_nan(row[3])):
            self.g.add((URIRef(entity_city_uri), self.lab5.longitude, Literal(row[3], datatype=XSD.float)))

        #population
        if (not self.is_nan(row[9])):
            self.g.add((URIRef(entity_city_uri), self.lab5.population, Literal(row[9], datatype=XSD.long)))


        #Country name triple            
        self.g.add((URIRef(entity_country_uri), self.lab5.name, Literal(row[4], datatype=XSD.string)))


        #iso codes
        if (not self.is_nan(row[5])):
            self.g.add((URIRef(entity_country_uri), self.lab5.iso2code, Literal(row[5], datatype=XSD.string)))
        if (not self.is_nan(row[6])):
            self.g.add((URIRef(entity_country_uri), self.lab5.iso3code, Literal(row[6], datatype=XSD.string)))



        #Connection between cities and countries

        #Basic connection ignoring column "capital":                        
        #self.g.add((URIRef(entity_city_uri), self.lab5.cityIsLocatedIn, URIRef(entity_country_uri)))


        #Exploiting 'capital' column (it can be empty)            

        #(default) if value is empty or not expected
        predicate = self.lab5.cityIsLocatedIn

        if row[8]=="admin":                      
            predicate = self.lab5.isFirstLevelAdminCapitalOf
        elif row[8]=="primary":
            predicate = self.lab5.isCapitalOf                        
        elif row[8]=="minor":
            predicate = self.lab5.isSecondLevelAdminCapitalOf


        #Note that the ontology in lab5.ttl contains a hierarchy of properties, range and domain axioms and inverses
        #Via reasoning this triple will lead to several entailments
        self.g.add((URIRef(entity_city_uri), predicate, URIRef(entity_country_uri)))
