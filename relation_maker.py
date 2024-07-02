#!env python3

import requests
from collections import namedtuple
from typing import Tuple, List
import json
from os.path import exists
from pyzotero import zotero
import time
from tqdm import tqdm
import itertools

Paper = namedtuple("Paper", ["doi", "title", "authors"])

SEMANTIC_SCHOLAR_API_URI = "https://api.semanticscholar.org/graph/v1/paper/"
FIELDS = "citations.externalIds,citations.title,citations.authors,references.externalIds,references.title,references.authors"

CONNECTION_DATA = {
    "library_id": 0,
    "library_type": "user",
    "api_key": ""
}

CONNECTION_DATA_FILE = "secret.json"

def paper_from_json(json_paper) -> Paper:
    authors = [json_author["name"] for json_author in json_paper["authors"]]
    if not json_paper["externalIds"] is None and "DOI" in json_paper["externalIds"]:
        doi = json_paper["externalIds"]["DOI"]
    else:
        doi = ""
    return Paper(doi, json_paper["title"], authors)

def get_cites_and_refs_from_doi(doi: str) -> Tuple[List[Paper], List[Paper]]:
    url = SEMANTIC_SCHOLAR_API_URI + doi
    output = requests.get(url, params={"fields": FIELDS})
    if not output.ok:
        tqdm.write(f"Error: {output.reason}")
        return ([],[])
    json_data = json.loads(output.content)
    citations = [paper_from_json(cit_json) for cit_json in json_data["citations"]]
    references = [paper_from_json(ref_json) for ref_json in json_data["references"]]
    
    return citations, references

def add_to_relations(relations, rel_item):
    # id = rel_item["library"]["id"]
    # name = rel_item["library"]["name"]
    href = rel_item["links"]["self"]["href"]
    href = href.replace("https://api.", "http://")
    if not href in relations:
        relations.append(href)
    return relations
    
def update_item(it, items):
    if not "DOI" in it["data"] or it["data"]["DOI"] == "":
        tqdm.write(f"No DOI for item {it['key']}")
        return it
    doi = it["data"]["DOI"]
    citations, references = get_cites_and_refs_from_doi(doi)
    dois = [p.doi for p in itertools.chain(citations, references) if p.doi != ""]
    titles = [p.title for p in itertools.chain(citations, references)]
    rel_items = [item for item in items if ("DOI" in item["data"] and item["data"]["DOI"] in dois) or ("title" in item["data"] and item["data"]["title"] in titles)]
    
    if "dc:relation" in it["data"]["relations"]:
        relations = it["data"]["relations"]["dc:relation"]
        if type(relations) is str:
            relations = [relations]
    else:
        relations = []
    keys = [r['key'] for r in rel_items]
    tqdm.write(f"{keys}")
    # obsidian_keys = []
    for rel_item in rel_items:
        relations = add_to_relations(relations, rel_item)
        # date = ""
        # if "date" in rel_item["data"]:
        #     date = rel_item["data"]["date"]
        # obsidian_keys.append({"creators": rel_item["data"]["creators"], "date": date})
    it["data"]["relations"]["dc:relation"] = relations
    return it
    
def update_items(zot:zotero.Zotero):
    print("Collecting all Zotero papers...")
    # items = zot.top(limit=30)
    items = zot.all_top()
    updated_items = []
    print("Updating papers...")
    for it in tqdm(items):
        tqdm.write(f"Updating {it['key']}")
        new_it = update_item(it, items)
        updated_items.append(new_it)
        time.sleep(1)
    print("Zotero Update API call...")
    zot.update_items(updated_items)

def load_connection_data():
    global CONNECTION_DATA
    if exists(CONNECTION_DATA_FILE):
        with open(CONNECTION_DATA_FILE, "r") as file:
            CONNECTION_DATA = json.load(file)
            return True
    else:
        with open(CONNECTION_DATA_FILE, "w") as file:
            json.dump(CONNECTION_DATA, file)
    return False
    
def main():
    if not load_connection_data():
        print("Not possible to load connection data")
        return
    
    print("Zotero connection...")
    zot = zotero.Zotero(**CONNECTION_DATA)
    update_items(zot)
    print("Finished!")
    
if __name__ == "__main__":
    main()
