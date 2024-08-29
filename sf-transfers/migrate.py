import argparse

from config import get_sf_prod, get_sf_sandbox, get_object_model
from upsert_record import upsert_record_and_references


def migrate(sf_source, sf_target, object_key, object_model, query=None):
    """
    Copies all records from the source to the target Salesforce instance.

    :param sf_source:
    :param sf_target:
    :param object_key:
    :param object_model:
    :param query:
    :return:
    """
    if query is None:
        # If no query provided, query all records
        query = f"SELECT Id FROM {object_key}"
    records = sf_source.query_all(query)["records"]

    print(f"Found {len(records)} records to migrate")

    i = 0
    for record in records:
        print(f"Migrating record {i + 1} of {len(records)}")
        upsert_record_and_references(
            sf_source,
            sf_target,
            object_key,
            record["Id"],
            {},
            object_model,
            {},
            True,
        )
        i += 1


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Migrate Salesforce objects or queries between environments."
    )
    parser.add_argument(
        "object_key", help="The Salesforce object name or SOQL query to migrate"
    )
    parser.add_argument(
        "--query",
        type=str,
        help="Optionally provide an SOQL query string to execute instead of object name migration",
    )

    # Parse arguments
    args = parser.parse_args()

    # Check if input is provided (argparse ensures this, so no need for manual check)
    sf_prod = get_sf_prod()
    sf_sandbox = get_sf_sandbox()
    object_model = get_object_model()

    # Call migrate with the flag
    migrate(sf_prod, sf_sandbox, args.object_key, object_model, args.query)
