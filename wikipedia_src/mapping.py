import json

# Load hierarchy dataset
with open('hierarchy2.json', 'r') as f:
    hierarchy_data = json.load(f)

# Create a dictionary to map qid to hierarchy level
qid_to_level = {}
for item in hierarchy_data:
    qid = list(item.keys())[0]
    level = item['level']
    qid_to_level[qid] = level

# Load qid labels dataset
with open('wikidata_qid_label.csv', 'r') as f:
    qid_labels_data = f.readlines()
    print()

# Create a dictionary to map qid to label
qid_to_label = {}
for line in qid_labels_data:
    qid, label, _ = line.strip().split(',')
    qid_to_label[qid] = label

# Create a dictionary to map qid to hierarchy label
qid_to_hierarchy_label = {}
for qid in qid_to_label.keys():
    if qid in qid_to_level.keys():
        level = qid_to_level[qid]
        hierarchy_labels = hierarchy_data[level - 1][qid]['children']
        hierarchy_labels.append(qid_to_label[qid])
        qid_to_hierarchy_label[qid] = hierarchy_labels
    else:
        qid_to_hierarchy_label[qid] = [qid_to_label[qid]]

# Example usage
qid = 'Q184485'
print(qid_to_hierarchy_label[qid])
