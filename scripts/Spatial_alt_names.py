#This code extracts the alternative labels of the spatial names 
#13/05/2020

import rdflib
from rdflib import Namespace, URIRef, Graph , Literal
from SPARQLWrapper import SPARQLWrapper2, XML , RDF , JSON
from rdflib.namespace import RDF, FOAF , SKOS ,RDFS
import os
import json
import io
import urllib
from urllib import request , parse
import re
import time
import glob


os.chdir('C:\\Users\\Maral\\Desktop\\Revised')

foaf = Namespace("http://xmlns.com/foaf/0.1/")
rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
jl = Namespace("http://data.judaicalink.org/ontology/")
gndo = Namespace("http://d-nb.info/standards/elementset/gnd#")
owl = Namespace("http://www.w3.org/2002/07/owl#")
edm = Namespace("http://www.europeana.eu/schemas/edm/")
skos=Namespace("http://www.w3.org/2004/02/skos/core#")
rdaGr2=Namespace("http://rdvocab.info/ElementsGr2/")


listfile= glob.glob("C:\\Users\\Maral\\Desktop\\Spatial\\*.ttl")

for k in range(0,len(listfile)):

    filename = listfile[k].split('\\',5)[5]

    print(filename)


    namecount = 1000

    g1 = Graph()

    g1.parse(listfile[k], format="turtle")

    g = Graph()

    g.bind('gndo',gndo)
    g.bind('foaf',foaf)
    g.bind('owl',owl)
    g.bind('jl',jl)
    g.bind('edm',edm)
    g.bind('skos',skos)
    g.bind('rdaGr2',rdaGr2)


    spar1= """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX gndo: <http://d-nb.info/standards/elementset/gnd#>
        PREFIX pro: <http://purl.org/hpi/patchr#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX edm: <http://www.europeana.eu/schemas/edm/>
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX dblp: <http://dblp.org/rdf/schema-2015-01-26#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX dbpedia: <http://dbpedia.org/resource/>
        PREFIX jl: <http://data.judaicalink.org/ontology/>
        PREFIX gnd: <http://d-nb.info/gnd/>

    SELECT ?x ?name (group_concat(?ids; SEPARATOR=", ") as ?id) (group_concat(?sames; SEPARATOR=", ") as ?same) (group_concat(?alts; SEPARATOR=", ") as ?alt)

    WHERE{

        ?x a edm:Place.
        ?x edm:identifier ?ids.
        ?x skos:prefLabel ?name.
        ?x owl:sameAs ?sames.
        ?x skos:altLabel ?alts.


     }  group by ?x ?name

        """

    result = g1.query(spar1)

    namesjl=[]

    for item in result:

       #print (item)

       namecount = namecount +1


       #uri = 'https://data.jhn.ngo/persons/' + uriname +'/' + str(namecount)
       uri = item[0]
       print (uri)

       if len(item[3])>25 and len(item[4])>25:

           g.add((URIRef(uri), rdf.type , edm.Place))
           g.add((URIRef(uri), skos.prefLabel ,(Literal(item[1]))))

           count = item[2].count(', ')

           if count !=0 :

                for i in range (0,count+1):

                    #print (item[2].rsplit(', ',count)[count-i])
                    g.add((URIRef(uri), edm.identifier ,(Literal(item[2].rsplit(', ',count)[count-i]))))

           else:

                g.add((URIRef(uri), edm.identifier ,(Literal(item[2]))))


           count = item[3].count(', ')

           if count !=0 :

                for i in range (0,count+1):

                    #print (item[3].rsplit(', ',count)[count-i])
                    g.add((URIRef(uri), owl.sameAs ,(Literal(item[3].rsplit(', ',count)[count-i]))))

           else:

                g.add((URIRef(uri), owl.sameAs ,(Literal(item[3]))))

           count = item[4].count(', ')

           if count !=0 :

                for i in range (0,count+1):

                    #print (item[4].rsplit(', ',count)[count-i])
                    g.add((URIRef(uri), skos.altLabel ,(Literal(item[4].rsplit(', ',count)[count-i]))))

           else:

                g.add((URIRef(uri), skos.altLabel ,(Literal(item[4]))))


g.serialize(destination= 'revised_' + filename  , format="turtle")




