from simple_salesforce import SalesforceResourceNotFound

from config import PRODUCTION_ID_KEY, get_object_model
import copy

GLOBAL_EXCLUSIONS = ["User", "Group", "RecordType"]


def upsert_record_and_references(
    source,
    target,
    object_key,
    object_id,
    metadata_map,
    object_model_map,
    upserted_map={},
    skip_existing=False,
):
    """
    Upserts a record and its dependencies.

    Dependency insertion is done recursively and depth-first, ie,
    the dependencies of a record are inserted before the record itself.
    Returns the Id of the inserted record and the updated metadata map.

    :param source: simple_salesforce.Salesforce source instance
    :param target: simple_salesforce.Salesforce target instance
    :param object_key: str Name of the object in Salesforce (ex: "Contact")
    :param object_id: str Salesforce Id of the source object to insert
    :param metadata_map: dict
    :param object_model_map: dict
    :param upserted_map: dict
    :param skip_existing: bool Whether to skip upserting if the record already exists

    :return: None
    """
    # All records up the tree should have been upserted already
    if object_id in upserted_map:
        return upserted_map[object_id], metadata_map, upserted_map

    if skip_existing:
        existing_id = get_id_in_target(target, object_key, object_id)
        if existing_id:
            print(f"Skipping {object_key} {object_id} as it already exists in target")
            upserted_map[object_id] = existing_id
            return existing_id, metadata_map, upserted_map

    print(f"Upserting {object_key} {object_id}")

    # Updates our metadata definitions if we don't have them
    metadata_map = update_metadata_map(source, object_key, metadata_map)
    object_fields_metadata = metadata_map[object_key]["fields"]

    exclusions = object_model_map[object_key].get("exclusions", [])
    fields_with_refs = get_fields_with_refs(exclusions, object_fields_metadata)

    fields = [field[0] for field in fields_with_refs]
    query = f"SELECT {', '.join(fields)} FROM {object_key} WHERE Id = '{object_id}'"
    record = source.query(query)["records"][0]

    # Before inserting into target, depth-first insert all references
    refs = get_object_refs_to_upsert(fields_with_refs)
    parent_refs = {}

    for ref in refs:
        ref_key, ref_object_key = ref[0], ref[1]
        ref_object_id = record[ref[0]]
        if ref_object_id:
            inserted_id, metadata_map, upserted_map = upsert_record_and_references(
                source,
                target,
                ref_object_key,
                ref_object_id,
                metadata_map,
                object_model_map,
                upserted_map,
                skip_existing,
            )
            parent_refs[ref_key] = inserted_id

    # If the reference has been upserted previously, we replace the value with the Id
    # TODO: Abstract into function
    record_data = {
        field: parent_refs[field] if field in parent_refs else record.get(field)
        for field in fields
    }

    try:
        sf_target_obj = target.__getattr__(object_key)
        if object_key == "Order":
            inserted_id = upsert_order(
                source, target, object_id, record_data, upserted_map
            )
        elif object_key == "PricebookEntry":
            inserted_id = upsert_pricebook_entry(sf_target_obj, object_id, record)
        else:
            inserted_id = upsert_record(sf_target_obj, object_id, record_data)
    except Exception as e:
        raise Exception(f"Upsert error {object_key} {object_id}: {e}")

    upserted_map[object_id] = inserted_id
    print(f"Upserted {object_key} {object_id} {record.get('Name', '')}")

    # We return the fields metadata to avoid having to re-query it
    return inserted_id, metadata_map, upserted_map


def get_id_in_target(sf_obj, object_key, source_id):
    """
    Gets a record by a custom identifier, the production id key.

    Returns
    :param sf_obj:
    :param object_key:
    :param source_id:
    :return:
    """
    try:
        return sf_obj.__getattr__(object_key).get_by_custom_id(
            PRODUCTION_ID_KEY, source_id
        )["Id"]
    except SalesforceResourceNotFound:
        return None


def upsert_record(sf_target_obj, object_id, record_data) -> str:
    """
    Upserts a record in the target Salesforce instance.

    If upsert fails but the object exists, we return the

    :param sf_target_obj: Simple Salesforce object instance
    :param object_id: str Salesforce Id of the object to insert
    :param record_data: dict Data to insert
    :return:
    """
    try:
        sf_target_obj.upsert(f"{PRODUCTION_ID_KEY}/{object_id}", record_data)
    except Exception as e:
        # Sometimes certain field objects cannot updated once created
        # ex: https://salesforce.stackexchange.com/q/70682
        # Retry without the fields that caused the error
        # TODO: Refactor
        if (
            e.content
            and "errorCode" in e.content[0]
            and e.content[0]["errorCode"] == "INVALID_FIELD_FOR_INSERT_UPDATE"
        ):
            print(f"Warning: upsert error {object_id}: {e}. Retrying...")
            fields = e.content[0]["fields"]
            new_data = {k: v for k, v in record_data.items() if k not in fields}
            # sf_target_obj.upsert(f"{PRODUCTION_ID_KEY}/{object_id}", new_data)
            return upsert_record(sf_target_obj, object_id, new_data)
        elif (
            e.content
            and "errorCode" in e.content[0]
            and e.content[0]["errorCode"] == "INACTIVE_OWNER_OR_USER"
        ):
            print(f"Warning: upsert error {object_id}: {e}. Inactive user. Retrying...")
            new_data = copy.deepcopy(record_data)
            # TODO: Move out to .env
            new_data["OwnerId"] = "0058e000002FWPA"  # Foster
            # sf_target_obj.upsert(f"{PRODUCTION_ID_KEY}/{object_id}", new_data)
            return upsert_record(sf_target_obj, object_id, new_data)
        else:
            raise e

    target_id = sf_target_obj.get_by_custom_id(PRODUCTION_ID_KEY, object_id)["Id"]
    return target_id


# TODO: Can remove src_order_id and get from record_data
def upsert_order(sf_source, sf_target, src_order_id, record_data, upserted_map) -> str:
    """
    Upserts a record in the target Salesforce instance.

    :param sf_source: simple_salesforce.Salesforce source instance
    :param sf_target: simple_salesforce.Salesforce target instance
    :param src_order_id: str Salesforce Id of the source Order
    :param record_data: dict Data to insert
    :return:
    """
    order_status = record_data.get("Status")
    record_data["Status"] = "Abierta"
    sf_target_obj = sf_target.Order
    inserted_id = upsert_record(sf_target_obj, src_order_id, record_data)
    upserted_map = copy.deepcopy(upserted_map)
    upserted_map[src_order_id] = inserted_id
    upsert_order_items(sf_source, sf_target, src_order_id, upserted_map)
    sf_target_obj.upsert(inserted_id, {"Status": order_status})
    return inserted_id


def upsert_order_items(sf_source, sf_target, order_src_id, upserted_map):
    """
    Upserts all OrderLineItems for an Order.

    :param sf_source: simple_salesforce.Salesforce source instance
    :param sf_target: simple_salesforce.Salesforce target instance
    :param order_src_id: str Salesforce Id of the source Order
    :param order_target_id: str Salesforce Id of the target Order
    :return:
    """
    query = f"SELECT Id FROM OrderItem WHERE OrderId = '{order_src_id}'"
    records = sf_source.query_all(query)["records"]

    metadata_map = {}
    for record in records:
        _, meta_map, m = upsert_record_and_references(
            sf_source,
            sf_target,
            "OrderItem",
            record["Id"],
            metadata_map,
            get_object_model(),
            upserted_map,
        )


def upsert_pricebook_entry(sf_target_obj, object_id, record_data):
    """
    Upserts a PricebookEntry in the target Salesforce instance.

    :param sf_target: simple_salesforce.Salesforce PricebookEntry instance
    :param object_id: str Salesforce Id of the object to insert
    :param record_data: dict Data to insert
    :return:
    """
    # try:
    #     sf_target_obj.upsert(f"{PRODUCTION_ID_KEY}/{object_id}", record_data)
    # except Exception as e:
    #     raise Exception(f"Upsert error PricebookEntry {object_id}: {e}")

    target_id = sf_target_obj.get_by_custom_id(PRODUCTION_ID_KEY, object_id)["Id"]
    return target_id


def update_metadata_map(sf, object_key, metadata_map):
    """
    Updates the metadata map with the metadata for the object_key if not present.

    :param sf: Simple Salesforce instance
    :param object_key: Name of the object in Salesforce (ex: "Contact")
    :param metadata_map: The existing metadata map
    :return:
    """
    if object_key not in metadata_map:
        new_map = copy.deepcopy(metadata_map)
        new_map[object_key] = sf.__getattr__(object_key).describe()
        return new_map
    return metadata_map


def get_fields_with_refs(exclusions, object_fields_metadata) -> list[tuple[str, str]]:
    """
    Returns a list of fields that have references to other objects.

    :param exclusions:
    :param object_fields_metadata:
    :return: List of tuples with the field name and the reference object name
    """
    return [
        (field["name"], field["referenceTo"])
        for field in object_fields_metadata
        if field["createable"] and field["name"] not in exclusions
    ]


def get_object_refs_to_upsert(fields_with_references) -> list[tuple[str, str]]:
    """
    Further filters the fields with references to exclude system objects.

    :param fields_with_references:
    :return: List of tuples with the field name and the reference object name
    """
    return [
        # We pick the field name and the first reference object;
        # having filtered out User and Group, there shouldn't be more than one reference
        (field[0], field[1][0])
        for field in fields_with_references
        if len(field[1]) > 0
        and field[1][0] != "User"
        and field[1][0] != "Group"
        and field[1][0] != "RecordType"
    ]
