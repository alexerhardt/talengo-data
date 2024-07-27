import copy
import json
import os

from init import get_sf_prod

sf_prod = get_sf_prod()

MAX_DEPTH = 20
starting_object = "compensation__c"


def get_relations_recursive(object_name, rels_map, depth=0):
    if depth > MAX_DEPTH:
        raise RecursionError("Max depth reached")

    if object_name in rels_map:
        return rels_map

    rels_map = copy.deepcopy(rels_map)

    fields_metadata = sf_prod.__getattr__(object_name).describe()
    fields = [
        (field["name"], field["referenceTo"])
        for field in fields_metadata["fields"]
        if field["createable"] and field["type"] == "reference"
    ]

    for field in fields:
        rels_map.setdefault(object_name, {})[field[0]] = field[1]
        for rel_object_name in field[1]:
            rels_map = get_relations_recursive(rel_object_name, rels_map, depth + 1)

    return rels_map


rels_map = get_relations_recursive(starting_object, {})


path_out = os.path.join(os.path.dirname(__file__), "data/relations_recursive.json")
with open(path_out, "w") as f:
    json.dump(rels_map, f, indent=2)
