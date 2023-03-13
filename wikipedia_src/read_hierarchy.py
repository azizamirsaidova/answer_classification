import json
import pandas as pd
import csv

# Read the qid-label mapping from the file
with open('hierarchy2.json') as f:
    hierarchy = json.load(f)

# Loop through the QIDs in wikidata_qid_label.csv
qid_label = {}
with open('wikidata_qid_label.csv') as f:
    reader = csv.reader(f)
    next(reader) 
    for row in reader:
        qid_label[row[0]] = row[1]


qid_info = {}
for item in hierarchy:
    for qid in qid_label:
        if qid in item:
            qid_info[qid] = {
                'level': item['level'],
                'children': item['children'],
                'label': qid_label[qid]
            }
print(len(qid_info))
print(len(hierarchy))

question_subject = "deployment environment"

def get_answer_types(question_subject):
    general_type = None
    for item in qid_info:
        # print(qid_info[i]['label'])
        if qid_info[item]['label'].lower() == question_subject.lower() and (general_type is None or qid_info[item]['level'] > general_type['level']):
            general_type = qid_info[item]
    
    if general_type is None:
        return None, None

    specific_type = general_type
    parent = None
    for item in qid_info:
        if 'children' in item and specific_type['label'] in item['children']:
            parent = item
            break
        specific_type = parent

    return general_type['label'], specific_type['label']

general_type, specific_type = get_answer_types('Albert Einstein')
# print(f"General answer type: {general_type}")
# print(f"Specific answer type: {specific_type}")