#this script reads the Europeana project datasets which are online and enriches them with gnd datasets.
# Maral Dadvar
#09/April/2020

import rdflib
from rdflib import Namespace, URIRef, Graph , Literal
from SPARQLWrapper import SPARQLWrapper2, XML , RDF , JSON
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

os.chdir('C:\\Users\\Maral\\Desktop\\Euroutput\\GND')

sparql = SPARQLWrapper2("http://localhost:3030/Datasets/sparql")

def get_names (dataname):

    record_prefix = "rdf:RDF/edm:ProvidedCHO"
    # Modidy/add Xpath mappings to get other fields and other objects (agent, place etc)

    edm_reader = MetadataReader(
        fields={
        'title':       ('textList', record_prefix + '/dc:title/text()'),
        'creator':     ('textList', record_prefix + '/dc:creator/text()'),
        'subject':     ('textList', record_prefix + '/dc:subject/text()'),
        'description': ('textList', record_prefix + '/dc:description/text()'),
        'publisher':   ('textList', record_prefix + '/dc:publisher/text()'),
        'contributor': ('textList', record_prefix + '/dc:contributor/text()'),
        'date':        ('textList', record_prefix + '/dc:date/text()'),
        'type':        ('textList', record_prefix + '/dc:type/text()'),
        'format':      ('textList', record_prefix + '/dc:format/text()'),
        'identifier':  ('textList', record_prefix + '/dc:identifier/text()'),
        'source':      ('textList', record_prefix + '/dc:source/text()'),
        'language':    ('textList', record_prefix + '/dc:language/text()'),
        'relation':    ('textList', record_prefix + '/dc:relation/text()'),
        'coverage':    ('textList', record_prefix + '/dc:coverage/text()'),
        'rights':      ('textList', record_prefix + '/dc:rights/text()'),
        'spatial':     ('textList', record_prefix + '/dc:spatial/text()'),
        'objectId':    ('textList', record_prefix + '/@rdf:about'),


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


    names=[]
    identifier=[]


    if __name__ == "__main__":

        URL = 'https://data.jhn.ngo/oai'

        registry = MetadataRegistry()
        registry.registerReader('edm', edm_reader)
        client = Client(URL, registry)
        # To harvest specific dataset, use "set" parameter: set='AIUJE1_MARC21'


        for record in client.listRecords(metadataPrefix='edm' , set= dataname):
            output = record[1].getMap()

            if output['creator'] !=[]:

                names.append([output['creator'][0]])
                identifier.append([output['creator'][0],output['objectId'][0]])

            if output['contributor'] !=[]:

                names.append([output['contributor'][0]])
                identifier.append([output['contributor'][0],output['objectId'][0]])

    print (names)


    return identifier


listdataset = ['AIUJE1_MARC21', 'AIUJE2_MARC21', 'MCYJE1_MARC21', 'MCYJE2_MARC21', 'JHI', 'YIVO_JE', 'LBI_art', 'LBI_books', 'LBI_periodicals', 'lbi_sound-recordings', 'LBI_photos', 'LBI_ms', 'jhm-museum','AJHS_photographs','BUL','CCJM','CentralJudaicaDatabase','GUF_cm','GUF_freimann','GUF_inchebr','GUF_jd','GUF_judaicaffm','GUF_mshebr','GUF_rothschild','JTSA','NLI']


for d in range (0,len(listdataset)):

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

    graph.bind('skos', skos)
    graph.bind ('foaf' , foaf)
    graph.bind ('jl' , jl)
    graph.bind('gndo',gndo)
    graph.bind ('owl' , owl)
    graph.bind ('dcterms' , dcterms)
    graph.bind ('edm' , edm)
    graph.bind('rdaGr2',rdaGr2)
    graph.bind('dc',dc)

    namesinfo={}

    names = get_names(listdataset[d])
    print (names)


    for i in range(0,len(names)): #check if there are birth/death dates in the name strings. etxract and creat a new dict with the info

        if any(j.isdigit() for j in names[i][0]):

            if sum (c.isdigit() for c in names[i][0]) == 4 or sum (c.isdigit() for c in names[i][0]) == 8:
                string1 = re.split(r'(\d+)', names[i][0].strip())
                name = string1[0].strip()
                name = name.replace('.','')
                name = name.replace('/','')
                name = name.replace('(','')
                name = name.replace(')','')
                name = name.replace('-','')
                name = name.replace(':','')
                if name.count(',')>1:
                    name = name.rsplit(',',1)[0]

                if len(string1)>1:
                    if string1[1] !=[]:
                        dateb=string1[1]
                    else:
                        dateb = '-'

                    if len(string1) > 3 :
                        dated=string1[3]
                    else:
                        dated = '-'

                    namesinfo[name] = (dateb,dated)

        else:
            name = names[i][0].strip()
            name = name.replace('.','')
            name = name.replace('/','')
            name = name.replace('(','')
            name = name.replace(')','')
            name = name.replace('-','')
            name = name.replace(':','')
            if name.count(',')>1:
                    name = name.rsplit(',',1)[0]

            namesinfo[name] = ('-','-')

    print (namesinfo)

    sparql.setQuery("""
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
        PREFIX jl: <http://data.judaicalink.org/ontology/>

    select ?xg ?yg ?bdg ?ddg

    where
    {

         GRAPH <http://maral.wisslab.org/graphs/gnd> {

    ?xg a gndo:DifferentiatedPerson.
    ?xg gndo:preferredNameForThePerson  ?yg.

    optional {?xg gndo:dateOfBirth ?bdg}
    optional {?xg gndo:dateOfDeath ?ddg}

        }
        }

    """)

    sparql.setReturnFormat(XML)

    results = sparql.query().convert()

    namecount = 1000

    listjl=[]

    commonname=[]

    for i in range(0,len(results.bindings)):

        if 'bdg' in results.bindings[i].keys() and 'ddg' in results.bindings[i].keys():

                bdg = results.bindings[i]['bdg'].value
                ddg = results.bindings[i]['ddg'].value

                if bdg !='' and ddg !='' :
                    bdg = re.findall(r'\d{4}', bdg)
                    ddg = re.findall(r'\d{4}', ddg)
                    if bdg !='' and bdg!=[] and ddg !='' and ddg!=[]:

                        listjl.append([results.bindings[i]['yg'].value, results.bindings[i]['xg'].value, bdg[0], ddg[0] ])

        elif 'bdg' in results.bindings[i].keys():
                bdg = results.bindings[i]['bdg'].value
                bdg = re.findall(r'\d{4}', bdg)
                if bdg !='' and bdg!=[]:
                    listjl.append([results.bindings[i]['yg'].value, results.bindings[i]['xg'].value, bdg[0], '-' ])

        elif 'ddg' in results.bindings[i].keys():
                ddg = results.bindings[i]['ddg'].value
                ddg = re.findall(r'\d{4}', ddg)
                if ddg !='' and ddg!=[]:
                    listjl.append([results.bindings[i]['yg'].value, results.bindings[i]['xg'].value, '-', ddg[0] ])

        else:
                listjl.append([results.bindings[i]['yg'].value, results.bindings[i]['xg'].value, '-', '-' ])


    for author in namesinfo.keys():

        namecount = namecount+1

        for i in range(0,len(listjl)):

            if author == listjl[i][0]:


                uri = 'https://data.jhn.ngo/persons/' + str(listdataset[d]) +'/' + str(namecount)

                if listjl[i][2] == namesinfo[author][0]:

                    if namesinfo[author][0]!='-':

                        commonname.append(author)


                        graph.add( (URIRef(uri),  RDF.type , edm.Agent ) )
                        graph.add( (URIRef(uri) , skos.prefLabel ,  Literal(author) ))
                        graph.add( (URIRef(uri) , rdaGr2.dateOfBirth ,  Literal(listjl[i][2]) ))
                        if '/ubcompact#ub-ffm:agent:' not in listjl[i][1]:
                            graph.add( (URIRef(uri) , owl.sameAs ,  URIRef(listjl[i][1])))


                        for j in range (0,len(names)):
                            if author in names[j][0]:
                                graph.add( (URIRef(uri) , edm.identifier ,  Literal(names[j][1])))


                if  listjl[i][3] == namesinfo[author][1] :

                    if namesinfo[author][1]!= '-':

                        if author not in commonname:
                            commonname.append(author)

                        graph.add( (URIRef(uri),  RDF.type , edm.Agent ) )
                        graph.add( (URIRef(uri) , skos.prefLabel ,  Literal(author) ))
                        graph.add( (URIRef(uri) , rdaGr2.dateOfDeath ,  Literal(listjl[i][3]) ))

                        if '/ubcompact#ub-ffm:agent:' not in listjl[i][1]:
                            graph.add( (URIRef(uri) , owl.sameAs ,  URIRef(listjl[i][1])))

                        for j in range (0,len(names)):
                            if author in names[j][0]:
                                graph.add( (URIRef(uri) , edm.identifier ,  Literal(names[j][1])))
								

                        print (listjl[i] , namesinfo[author])


    for author in namesinfo.keys():

        namecount = namecount+1

        if author not in commonname:

            if namesinfo[author][0]!= '-':
                birthday= namesinfo[author][0]
            else:
                birthday= '-'

            if namesinfo[author][1]!= '-':
                deathday= namesinfo[author][1]
            else:
                deathday= '-'


            if birthday!='-' or deathday!='-':

                uri = 'https://data.jhn.ngo/persons/' + str(listdataset[d]) +'/' + str(namecount)

                graph.add( (URIRef(uri),  RDF.type , edm.Agent ) )
                graph.add( (URIRef(uri) , skos.prefLabel ,  Literal(author) ))
                graph.add( (URIRef(uri) , rdaGr2.dateOfBirth ,  Literal(birthday) ))
                graph.add( (URIRef(uri) , rdaGr2.dateOfDeath ,  Literal(deathday) ))


                for j in range (0,len(names)):
                            n = names[j][0]
                            n = n.replace('.','')
                            n = n.replace('/','')
                            n = n.replace('(','')
                            n = n.replace(')','')
                            n = n.replace('-','')
                            n = n.replace(':','')
                            if author in n:
                                graph.add( (URIRef(uri) , edm.identifier ,  Literal(names[j][1])))




    graph.serialize(destination= listdataset[d] + '_Contextualized_gnd_01.ttl', format="turtle")

print("--- %s seconds ---" % (time.time() - start_time))

