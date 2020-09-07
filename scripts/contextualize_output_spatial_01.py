#this script reads the Europeana project datasets which are online and extracts their spatial infomation and enrich them with jl datasets.
# Maral Dadvar
#08/May/2020

import rdflib
from rdflib import Namespace, URIRef, Graph , Literal
from SPARQLWrapper import SPARQLWrapper2, XML , RDF , JSON, TURTLE
from rdflib.namespace import RDF, FOAF , SKOS ,RDFS
import os
import json
import io
import urllib
from urllib import request , parse
from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry, MetadataReader
import re
import time


start_time = time.time()

os.chdir('C:\\Users\\Maral\\Desktop\\Euroutput\\Spatial')


sparql = SPARQLWrapper2("http://localhost:3030/Datasets/sparql")


def get_names (dataname):

    record_prefix = "rdf:RDF/edm:ProvidedCHO"

    edm_reader = MetadataReader(
        fields={

        'objectId':    ('textList', record_prefix + '/@rdf:about'),
        'spatial':     ('textList', record_prefix + '/dcterms:spatial/text()'),


        },
        namespaces={
    	   'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
    	   'dc':'http://purl.org/dc/elements/1.1/',
    	   'dcterms':'http://purl.org/dc/terms/',
    	   'dct': 'http://purl.org/dc/terms/',
    	   'edm' : 'http://www.europeana.eu/schemas/edm/',
    	   'foaf': 'http://xmlns.com/foaf/0.1/',
    	   'owl' : 'http://www.w3.org/2002/07/owl#',
    	   'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    	   'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
    	   'skos': 'http://www.w3.org/2004/02/skos/core#',
    	   'xsi' : 'http://www.w3.org/2001/XMLSchema-instance',
    	   'ore': 'http://www.openarchives.org/ore/terms/'
    	}
         )


    dictnames={}
    identifier=[]


    if __name__ == "__main__":

        URL = 'https://data.jhn.ngo/oai'

        registry = MetadataRegistry()
        registry.registerReader('edm', edm_reader)
        client = Client(URL, registry )

        k = 0

        for record in client.listRecords(metadataPrefix='edm' , set= dataname ):

            output = record[1].getMap()

            k = k + 1
            print(k)

            if output['spatial'] !=[]:

                if len(output['spatial']) ==1:

                    if len(output['spatial'][0])>3:

                        if [output['spatial'][0],output['objectId'][0]] not in identifier:

                            identifier.append([output['spatial'][0],output['objectId'][0]])

                        if output['spatial'][0] not in dictnames.keys():

                            key = output['spatial'][0]
                            dictnames.setdefault(key,[])
                            dictnames[key].append(output['objectId'][0])

                        else:

                            key = output['spatial'][0]

                            dictnames[key].append(output['objectId'][0])

                else:
                    for j in range (0,len(output['spatial'])):

                        if len(output['spatial'][j])>3:

                            if [output['spatial'][j],output['objectId'][0]] not in identifier:

                                identifier.append([output['spatial'][j],output['objectId'][0]])

                            if output['spatial'][j] not in dictnames.keys():

                                key = output['spatial'][j]
                                dictnames.setdefault(key,[])
                                dictnames[key].append(output['objectId'][0])

                            else:

                                key = output['spatial'][j]

                                dictnames[key].append(output['objectId'][0])

    #print (identifier)


    return dictnames



def context_geo (key, values,dataset,namecount):

    geoname='"' + key + '"'

    spar2= """
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
    PREFIX bibtex: <http://data.bibbase.org/ontology/#>
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>

        select ?x  (group_concat(?alt; SEPARATOR=", ") as ?altname) (group_concat(?sameas; SEPARATOR=", ") as ?same)

        WHERE{{

          graph <http://maral.wisslab.org/graphs/gnd> {{


            	?x (gndo:preferredNameForThePlaceOrGeographicName | gndo:variantNameForThePlaceOrGeographicName){0}.
                optional {{?x gndo:variantNameForThePlaceOrGeographicName ?alt.}}
                optional {{?x owl:sameAs ?sameas.}}
               # ?x geo:hasGeometry ?geo.
               # optional {{?geo geo:asWKT ?coo}}
          }}
          }} group by ?x

        """.format(geoname)

    sparql.setQuery(spar2)
    sparql.setReturnFormat(XML)
    results = sparql.query().convert()



    for i in range(0,len(results.bindings)):

        #print(results.bindings[i])

        uri = 'https://data.jhn.ngo/spatial/' + str(dataset) +'/' + str(namecount)
        graph.add( (URIRef(uri),  RDF.type , edm.Place ) )


        for z in range(0,len(values)):

            graph.add( (URIRef(uri),  edm.identifier , Literal(values[z]) ) )


        graph.add( (URIRef(uri),  skos.prefLabel , Literal(key) ) )

        if 'altname' in results.bindings[i].keys():


            count1 = results.bindings[i]['altname'].value.count(',')

            if count1>0:

                for j in range(0,count1+1):

                    graph.add((URIRef(uri), skos.altLabel ,(Literal(results.bindings[i]['altname'].value.rsplit(', ',count1)[count1-j]))))

            else:

                graph.add((URIRef(uri), skos.altLabel ,(Literal(results.bindings[i]['altname'].value))))


        if 'same' in results.bindings[i].keys():


            count2 = results.bindings[i]['same'].value.count(',')

            if count2>0:

                for j in range(0,count2+1):

                    graph.add((URIRef(uri), owl.sameAs ,(Literal(results.bindings[i]['same'].value.rsplit(', ',count2)[count2-j]))))

            else:

                    graph.add((URIRef(uri), owl.sameAs ,(Literal(results.bindings[i]['same'].value))))



    graph.serialize(destination= dataset + '_Spatial_01.ttl', format="turtle")


listdataset = ['AIUJE1_MARC21', 'AIUJE2_MARC21', 'MCYJE1_MARC21', 'MCYJE2_MARC21', 'JHI', 'YIVO_JE', 'LBI_art', 'LBI_books', 'LBI_periodicals', 'lbi_sound-recordings', 'LBI_photos', 'LBI_ms', 'jhm-museum','AJHS_photographs','AJHS_text','BUL','CCJM','CentralJudaicaDatabase','GUF_cm','GUF_freimann','GUF_inchebr','GUF_jd','GUF_judaicaffm','GUF_mshebr','GUF_rothschild','JTSA','NLI','jhm-documenten','jhm-foto']





for d in range (0,len(listdataset)):

    names = get_names(listdataset[d])

    print (names)

    graph = Graph()

    foaf = Namespace("http://xmlns.com/foaf/0.1/")
    skos = Namespace("http://www.w3.org/2004/02/skos/core#")
    gndo = Namespace("http://d-nb.info/standards/elementset/gnd#")
    jl = Namespace("http://data.judaicalink.org/ontology/")
    owl = Namespace ("http://www.w3.org/2002/07/owl#")
    dcterms = Namespace("http://purl.org/dc/terms/")
    edm = Namespace("http://www.europeana.eu/schemas/edm/")
    rdaGr2=Namespace("http://rdvocab.info/ElementsGr2/")
    dc= Namespace("http://purl.org/dc/elements/1.1/")
    geo = Namespace("http://www.opengis.net/ont/geosparql#")

    graph.bind('skos', skos)
    graph.bind ('foaf' , foaf)
    graph.bind ('jl' , jl)
    graph.bind('gndo',gndo)
    graph.bind ('owl' , owl)
    graph.bind ('dcterms' , dcterms)
    graph.bind ('edm' , edm)
    graph.bind('rdaGr2',rdaGr2)
    graph.bind('dc',dc)
    graph.bind('geo',geo)

    namecount = 1000

    for keys in names.keys():

        namecount = namecount +1

        key = keys

        key = key.replace('.','')
        key = key.replace(' ','')
        key = key.replace(',','')
        key = key.replace('\'','')
        key = key.replace('/','')
        key = key.replace('"','')
        key = key.replace('-','')
        key = key.replace(':','')
        key = key.replace('--','')
        key = key.replace('(','')
        key = key.replace(')','')

        context_geo(key,names[keys],listdataset[d],namecount)


    #print("--- %s seconds ---" % (time.time() - start_time))



