import pytest
from requests import HTTPError

from config import get_sf_prod
from ezekia.api import EzekiaAPIClient
from migration_test.mappings import account
from migration_test.ids.account import account_ids


@pytest.fixture(scope="module")
def sf_records():
    """
    Get Salesforce records with fields specified in the account mapping file.
    """
    sf_keys = [r["sourceKey"] for r in account.mapping if "sourceKey" in r]
    sf = get_sf_prod()
    query = f"""
    SELECT {", ".join(sf_keys)}
    FROM Account 
    WHERE Id IN ({", ".join([f"'{sf_id}'" for sf_id in account_ids])})
    """
    result = sf.query(query)
    return result["records"]


@pytest.fixture(scope="module")
def ez_records(sf_records):
    """
    Get Ezekia records by Salesforce ID.
    :param sf_records: Salesforce records list
    :return: Dictionary with Salesforce ID as key and Ezekia record as value
    """
    ezekia = EzekiaAPIClient()
    result = {}
    for record in sf_records:
        sf_id = record["Id"]
        try:
            result[sf_id] = ezekia.companies.get_by_salesforce_id(sf_id)
        except HTTPError as e:
            if e.response.status_code == 404:
                result[sf_id] = None
            else:
                raise
    return result


@pytest.mark.parametrize("sf_id", account_ids)
def test_account_found(sf_id, ez_records):
    """
    Test that each Salesforce account ID has a corresponding Ezekia record.
    """
    assert ez_records.get(sf_id), f"Record with ID {sf_id} is missing"


@pytest.mark.parametrize("sf_id", account_ids)
def test_account_name(sf_id, sf_records, ez_records):
    """
    Test that the account name matches between Salesforce and Ezekia.
    """
    sf_record = next(r for r in sf_records if r["Id"] == sf_id)
    ez_record = ez_records[sf_id]
    assert sf_record["Name"] == ez_record["name"], f"Name mismatch for account {sf_id}"


@pytest.mark.parametrize("sf_id", account_ids)
def test_account_description(sf_id, sf_records, ez_records):
    """
    Test that the account description matches between Salesforce and Ezekia.
    """
    sf_record = next(r for r in sf_records if r["Id"] == sf_id)
    ez_record = ez_records[sf_id]
    assert (
        sf_record["Description"] == ez_record["description"]
    ), f"Description mismatch for account {sf_id}"
