import csv, time
import ssl
import json
from urllib.error import HTTPError
from http.client import RemoteDisconnected
from collections import defaultdict
from wikidata.client import Client
from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.SPARQLExceptions import QueryBadFormed, EndPointInternalError


ssl._create_default_https_context = ssl._create_unverified_context
# headers = { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
agent_header = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent=agent_header)
sparql.setMethod("POST")

client = Client()

get_entity_for_qid = {}

def get_parent_ids(child):
    return [parent['mainsnak']['datavalue']['value']['id'] for parent in child.attributes['claims']['P279'] if 'datavalue' in parent['mainsnak']] if 'P279' in child.attributes['claims'] else []


def get_entity_level_bfs(entity_id):
    frontier = [(entity_id, 0)]
    while frontier:
        new_ent_id, new_ent_level = frontier.pop(0)
        entity_class = client.get(new_ent_id)
        parent_ids = get_parent_ids(entity_class)
        if not parent_ids:
            return new_ent_level
        frontier.extend([(parent_id, new_ent_level + 1) for parent_id in parent_ids])

def get_children(parent_id) -> list:
    query = f"""
    SELECT ?child
    WHERE {{
      ?child wdt:P279 wd:{parent_id}.
    }}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    while True:
        try:
            results = sparql.query().convert()
            break
        except (QueryBadFormed, EndPointInternalError, RemoteDisconnected) as e:
            print(e.args[0]) # for debugging
            raise e
        except HTTPError as e:
            retries = list(filter(lambda x: x[0] == 'retry-after', e.headers._headers))
            for retry_header in retries:
                print(f'Query limit reached. Waiting {retry_header[1]} second(s) before retry.')
                time.sleep(int(retry_header[1]))
    if 'results' in results:
        return [binding['child']['value'].rpartition('/')[-1] for binding in results['results']['bindings']]
    else:
        return []

def append_to_jsonl_file(data, file):
    """ Appends json dictionary as new line to file """
    with open(file, 'a+') as out_file:
        out_file.write(json.dumps(data, indent=4)+',')

with open('wikidata_qid_label.csv', newline='') as vocab_file:
    label_to_id = csv.reader(vocab_file, delimiter=',')
    next(label_to_id)

    for row in label_to_id:
        #print(row[0], row[1], end='')
        children = get_children(row[0])
        level = get_entity_level_bfs(row[0])
        get_entity_for_qid[row[0]] = {row[0]: row[1], 'level': level, 'children': children}
        if level != 0 or (len(children) != 0):
            print(row[0], row[1])
            append_to_jsonl_file(get_entity_for_qid[row[0]], "hierarchy3.json")

            
