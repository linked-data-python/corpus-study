# Extracted from city-knowledge-graphs/python@aa759f7438 : lab6/lab6_solution.py
# region: Lab6Solution.SimpleUniqueMapping (lines 68-142, stratum coercion_datatype)
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

        entity_city_uri = URIRef(self.lab6_ns_str + row[1].lower().replace(" ", "_"))
        entity_country_uri = URIRef(self.lab6_ns_str + row[4].lower().replace(" ", "_"))

        #Types triples
        #Using self.lab6.City is equivalent to using URIRef(self.lab6_ns_str = "City")
        self.g += [
            (entity_city_uri, RDF.type, self.lab6.City),     #e.g. lab6:london rdf:type lab6:City
            (entity_country_uri, RDF.type, self.lab6.Country),  #e.g. lab6united_kingdom rdf:type lab6:Country
        ]

        for entity, prop, column, datatype in [
            #City Names triples
            (entity_city_uri, self.lab6.name_ascii, 1, XSD.string),
            (entity_city_uri, self.lab6.name, 0, XSD.string),
            (entity_city_uri, self.lab6.admin_name, 7, XSD.string),
            #Lat & long
            (entity_city_uri, self.lab6.latitude, 2, XSD.float),
            (entity_city_uri, self.lab6.longitude, 3, XSD.float),
            #population
            (entity_city_uri, self.lab6.population, 9, XSD.long),
            #Country name triple
            (entity_country_uri, self.lab6.name, 4, XSD.string),
            #iso codes
            (entity_country_uri, self.lab6.iso2code, 5, XSD.string),
            (entity_country_uri, self.lab6.iso3code, 6, XSD.string),
        ]:
            if (not self.is_nan(row[column])):
                self.g.add((entity, prop, Literal(row[column], datatype=datatype)))


        #Connection between cities and countries

        #Basic connection ignoring column "capital":                        
        #self.g.add((URIRef(entity_city_uri), self.lab6.cityIsLocatedIn, URIRef(entity_country_uri)))


        #Exploiting 'capital' column (it can be empty)            

        #(default) if value is empty or not expected
        predicate = {
            "admin": self.lab6.isFirstLevelAdminCapitalOf,
            "primary": self.lab6.isCapitalOf,
            "minor": self.lab6.isSecondLevelAdminCapitalOf,
        }.get(row[8], self.lab6.cityIsLocatedIn)


        #Note that the ontology in lab6.ttl contains a hierarchy of properties, range and domain axioms and inverses
        #Via reasoning this triple will lead to several entailments
        self.g.add((entity_city_uri, predicate, entity_country_uri))
