import argparse

from config import get_sf_prod
import random

random.seed(42)


def _get_global_sf_query(object_name):
    return f"""
    SELECT Id
    FROM {object_name}
    """


def generate_sample_ids(sf, query, n=35):
    """
    Generate a sample of Salesforce record IDs.
    :param sf: Salesforce client
    :param sf_object: Salesforce object name
    :param n: Number of IDs to sample
    :return: List of Salesforce record IDs
    """
    result = sf.query(query)
    return random.sample([r["Id"] for r in result["records"]], n)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-q", "--query", type=str, help="Query to filter records")
    group.add_argument("-o", "--sf_object", type=str, help="Salesforce object name")
    parser.add_argument("-n", type=int, help="Number of IDs to sample")

    args = parser.parse_args()

    if args.query:
        query = args.query
    elif args.sf_object:
        query = _get_global_sf_query(args.sf_object)
    else:
        raise ValueError("Either query or object name must be provided")

    sf = get_sf_prod()
    account_ids = generate_sample_ids(sf, query, args.n)

    print("\n".join(account_ids))
