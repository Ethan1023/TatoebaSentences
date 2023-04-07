import re
import os
import pickle
import csv

DATA_PATH = "data"

# Get matching tsvs from folder
def get_data_tsvs():
    data_tsvs = []
    for file in os.listdir(DATA_PATH):
        if os.path.isfile(os.path.join(DATA_PATH, file)) and re.search("tsv$", file):
            data_tsvs.append(os.path.join(DATA_PATH, file))
    return data_tsvs

def get_language_pairs(names):
    pairs = []
    for name in names:
        pairs.append(get_language_pair(name))
    return pairs

def get_language_pair(name):
    obj = re.search("Sentence pairs in ([^-]*)-([^-]*)-.*tsv", name)
    if obj:
        return [obj[1].strip(), obj[2].strip()]
    return []

def load_database():
    try:
        with open(DATA_PATH + "/data.pkl", "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return {"sentences": {}, "languages": {}}

def save_database(data):
    with open(DATA_PATH + "/data.pkl", "wb") as file:
        pickle.dump(data, file)

def import_databases(filenames, data):
    sentences = data["sentences"]
    print(f"Initial database size = {len(sentences)}")
    for filename in filenames:
        lang1, lang2 = get_language_pair(filename)
        if lang1 not in data["languages"]:
            data["languages"][lang1] = {"confidences": [set()]}
        if lang2 not in data["languages"]:
            data["languages"][lang2] = {"confidences": [set()]}
        with open(filename, encoding="utf-8-sig") as file:
            tsv = csv.reader(file, delimiter="\t", quoting=csv.QUOTE_NONE)
            for line in tsv:
                id1 = int(line[0])
                if not len(line) == 4:
                    print(line)
                id2 = int(line[2])

                if id1 not in sentences:
                    sentences[id1] = {"sen": {}, "ids": set()}
                sentences[id1]["sen"] = line[1]
                sentences[id1]["lang"] = lang1
                sentences[id1]["ids"].add(id2)

                if id2 not in sentences:
                    sentences[id2] = {"sen": {}, "ids": set()}
                sentences[id2]["sen"] = line[3]
                sentences[id2]["lang"] = lang2
                sentences[id2]["ids"].add(id1)
    print(f"Final database size = {len(sentences)}")
