from config import get_sf_prod
import random

random.seed(42)


def generate_sample_ids(sf, sf_object, n=35):
    """
    Generate a sample of Salesforce record IDs.
    :param sf: Salesforce client
    :param sf_object: Salesforce object name
    :param n: Number of IDs to sample
    :return: List of Salesforce record IDs
    """
    query = f"""
    SELECT Id
    FROM {sf_object}
    """
    result = sf.query(query)
    return random.sample([r["Id"] for r in result["records"]], n)


if __name__ == "__main__":
    sf = get_sf_prod()
    account_ids = generate_sample_ids(sf, "Account")
    print("account_ids =", account_ids)
