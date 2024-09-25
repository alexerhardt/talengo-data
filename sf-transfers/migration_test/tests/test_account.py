import pytest
from requests import HTTPError

from config import get_sf_prod
from ezekia.api import EzekiaAPIClient
from migration_test.mappings import account


@pytest.fixture(scope="module")
def sf_records():
    sf_keys = [r["sourceKey"] for r in account.mapping if "sourceKey" in r]
    sf = get_sf_prod()
    query = f"""
    SELECT {", ".join(sf_keys)}
    FROM Account 
    WHERE Id = '0014H00002N3BJAQA3'
    """
    result = sf.query(query)
    return result["records"]


@pytest.fixture(scope="module")
def ez_records(sf_records):
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


def test_accounts_found(sf_records, ez_records):
    missing = []
    for record in sf_records:
        sf_id = record["Id"]
        if not ez_records[sf_id]:
            missing.append(sf_id)
    assert not missing, f"Missing records: {missing}"
