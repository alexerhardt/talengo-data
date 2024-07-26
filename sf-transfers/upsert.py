def upsert_record(source, target, object_key, object_id, refs, exclusions):
    """
    Upsert a record from a source Salesforce instance to a target Salesforce instance.

    :param source: simple_salesforce.Salesforce instance
    :param target: simple_salesforce.Salesforce instance
    :param object_key: str
    :param object_id: str
    :param refs: dict
    :param exclusions: list
    :return: None
    """
    # Get all field names for the object in the source instance
    fields_metadata = source.__getattr__(object_key).describe()
    fields = [field['name'] for field in fields_metadata['fields']]

    # Construct a query to get all fields
    query = f"SELECT {', '.join(fields)} FROM {object_key} WHERE Id = '{object_id}'"
    record = source.query_all(query)['records'][0]

    # Insert data into the target instance, excluding system fields and handling read-only fields
    record_data = {field: record.get(field) for field in fields if field not in exclusions}
    for key, value in refs.items():
        record_data[key] = value
    try:
        target.__getattr__(object_key).upsert(object_id, record_data)
        print(f"Upserted {object_key}: {record.get('Name', '')}")
    except Exception as e:
        print(f"Error upserting {object_key} {record.get('Name', '')}: {e}")
