def upsert_record(source, target, object_key, object_id, defs):
    """
    Upsert a record from a source Salesforce instance to a target Salesforce instance.

    :param source: simple_salesforce.Salesforce instance
    :param target: simple_salesforce.Salesforce instance
    :param object_key: str
    :param object_id: str
    :return: None
    """
    # Get all field names for the object in the source instance
    # TODO: Optimize, this is a lot of API calls
    # Return this as a param so that it can be memoized and passed in
    fields_metadata = source.__getattr__(object_key).describe()
    exclusions = defs["object_key"].get("exclusions", [])
    exclusions.append("Id")

    fields = [field['name'] for field in fields_metadata['fields'] if
              field['createable'] and field['name'] not in exclusions]

    # Construct a query to get all fields
    query = f"SELECT {', '.join(fields)} FROM {object_key} WHERE Id = '{object_id}'"
    record = source.query_all(query)['records'][0]

    # Dangerous assumption: referenceTo only contains a single reference
    refs = [(field['name'], field['referenceTo'][0]) for field in
            fields_metadata['fields'] if field['type'] == 'reference']

    # TODO: Abstract into own function
    # Return ids, and a way to relate old values with new values to replace later
    for ref in refs:
        ref_object_key = ref[1]
        ref_object_id = record.get(ref[0])
        upsert_record(source, target, ref_object_key, ref_object_id, defs)

    # TODO: Need to replace the references in the record with ref ids
    record_data = {field: record.get(field) for field in fields if field != 'Id'}

    # TODO: Add duplicate detection logic
    try:
        # TODO: Make sure that this is the correct way to upsert, and that id is returned
        id = target.__getattr__(object_key).upsert(object_id, record_data)
        print(f"Upserted {object_key}: {record.get('Name', '')}")
    except Exception as e:
        print(f"Error upserting {object_key} {record.get('Name', '')}: {e}")

    return id, fields_metadata
