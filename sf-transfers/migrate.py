from config import get_sf_prod, get_sf_sandbox, get_object_model
from upsert_record import upsert_record_and_references


def migrate(sf_source, sf_target, object_key, object_model, query=None):
    """
    Copies all records from the source to the target Salesforce instance.

    :param sf_source:
    :param sf_target:
    :param object_key:
    :param query:
    :return:
    """
    if query is None:
        query = f"SELECT Id FROM {object_key}"
    records = sf_source.query_all(query)["records"]

    for record in records:
        upsert_record_and_references(
            sf_source,
            sf_target,
            object_key,
            record["Id"],
            {},
            object_model,
        )


if __name__ == "__main__":
    # Get the Salesforce object name to copy from the command line
    import sys

    if len(sys.argv) < 2:
        print("Usage: python copy_entity.py <object_name>")
        sys.exit(1)

    object_name = sys.argv[1]

    sf_prod = get_sf_prod()
    sf_sandbox = get_sf_sandbox()
    object_model = get_object_model()

    migrate(sf_prod, sf_sandbox, object_name, object_model)
