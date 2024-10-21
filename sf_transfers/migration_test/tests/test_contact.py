import pytest
from requests import HTTPError

from config import get_sf_prod
from ezekia.api import EzekiaAPIClient
from migration_test.mappings.contact import contact_mapping


@pytest.fixture(scope="module")
def sf_records():
    sf_keys = [r["sourceKey"] for r in contact_mapping if "sourceKey" in r]
    sf = get_sf_prod()
    query = f"""
    SELECT {", ".join(sf_keys)}
    FROM Contact
    WHERE Id = '0038e000006pqakAAA'
    """
    result = sf.query(query)
    return result["records"]


@pytest.fixture(scope="module")
def ez_records(sf_records):
    ezekia = EzekiaAPIClient()
    result = {}
    for record in sf_records:
        email = record["Email"]
        try:
            result[email] = ezekia.people.get_by_email(record["Email"])
        except HTTPError as e:
            if e.response.status_code == 404:
                result[email] = None
            else:
                raise
    return result


def test_contacts_found(sf_records, ez_records):
    missing = []
    for record in sf_records:
        email = record["Email"]
        if not ez_records[email]:
            missing.append(email)
    assert not missing, f"Missing records: {missing}"
