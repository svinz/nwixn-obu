from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk
import ssl 
import json 
import ast
import click

def generate_lines(filename):
    with open(filename) as f:
        for line in f:
            line = line.strip('\n')
            yield line
@click.command()
@click.option("-logfile", help="logfile to upload to Elasticsearch", required=True, type=click.Path(exists=True))

def placeLogToEs(logfile):
    filename = logfile
    
    filename = filename.split(sep="logs/")
    newIndex = filename[1].split(sep=".")
    newIndex = "nwixn" + newIndex[0]
    print(newIndex)

    es = Elasticsearch("URL", http_auth=("username","password"),use_ssl=True,
    verify_certs=True)
    es.indices.create(index=newIndex, ignore=400)
    success = 0
    for ok, action in streaming_bulk(es,index=newIndex, actions=generate_lines(logfile)):
        success += ok
    
    print(success)


    res = es.search(index=newIndex, body={"query": {"match_all": {}}})
    print("Got %d Hits:" % res['hits']['total']['value'])
# for hit in res['hits']['hits']:
#         print("%(timestamp)s %(author)s: %(text)s" % hit["_source"])
if __name__ == '__main__':
    placeLogToEs()