import json
import csv

# Load hierarchy data
with open('hierarchy2.json', 'r') as f:
    hierarchy_data = json.load(f)

for item in hierarchy_data:
    qid = list(item.keys())[0]
    level = item['level']
    children = item['children']
    

# Load Qid label data
qid_labels = {}
with open('wikidata_qid_label.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader) # skip header row
    for row in reader:
        qid_labels[row[0]] = row[1]

# Load training data
with open('task1_wikidata_train.json', 'r') as f:
    train_data = json.load(f)
    for item in train_data:
        train_question = item['question']

# Find the closest matching qid label in the hierarchy
best_match = None
best_score = -1
for child in children:
    if child in qid_labels:
        label = qid_labels[child]
        score = len(set(train_question.split()).intersection(label.split()))
        if score > best_score:
            best_match = child
            best_score = score

# Output the predicted answer type
if best_match:
    print("Predicted answer type:", qid_labels[best_match])
else:
    print("No matching qid label found in hierarchy.")
