# TODO: Add logging with numbers of calls, etc
# Add info on id and object being inserted
import copy

GLOBAL_EXCLUSIONS = ["User", "Group"]


def update_metadata_map(sf, object_key, metadata_map):
    if object_key not in metadata_map:
        new_map = copy.deepcopy(metadata_map)
        new_map[object_key] = sf.__getattr__(object_key).describe()
        return new_map
    return metadata_map


def upsert_record_and_references(
    source, target, object_key, object_id, metadata_map, object_model_map
):
    """
    Recursively upserts a record and its dependencies

    :param source: simple_salesforce.Salesforce source instance
    :param target: simple_salesforce.Salesforce target instance
    :param object_key: str
    :param object_id: str
    :param metadata_map: dict
    :return: None
    """
    # Updates our metadata definitions if we don't have them
    fields_metadata = update_metadata_map(source, object_key, metadata_map)

    # Get all the object data we want to migrate, minus non-creatable and exclusions
    exclusions = object_model_map["object_key"].get("exclusions", [])
    fields = [
        field["name"]
        for field in fields_metadata["fields"]
        if field["createable"] and field["name"] not in exclusions
    ]
    query = f"SELECT {', '.join(fields)} FROM {object_key} WHERE Id = '{object_id}'"
    record = source.query_all(query)["records"][0]

    # The only references with more than one referenceTo are User and Group; excluded
    refs = [
        (field["name"], field["referenceTo"][0])
        for field in fields_metadata["fields"]
        if field["type"] == "reference"
        and field["referenceTo"][0] != "User"
        or field["referenceTo"][0] != "Group"
    ]

    # Before inserting into target, depth-first insert all references
    for ref in refs:
        ref_object_key = ref[1]
        ref_object_id = record.get(ref[0])
        fields_metadata = upsert_record_and_references(
            source, target, ref_object_key, ref_object_id, object_model_map
        )

    # TODO: Need to replace the references in the record with ref ids
    record_data = {field: record.get(field) for field in fields}
    record_data["ProductionId__c"] = record["Id"]

    try:
        target.__getattr__(object_key).upsert(
            f"ProductionId__c/{object_id}", record_data
        )
        print(f"Upserted {object_key}: {record.get('Name', '')}")
    except Exception as e:
        print(f"Error upserting {object_key} {record.get('Name', '')}: {e}")

    # We return the fields metadata to avoid having to re-query it
    return fields_metadata
