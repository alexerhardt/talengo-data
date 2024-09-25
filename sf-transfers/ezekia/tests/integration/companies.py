import pytest
from ezekia.api import EzekiaAPIClient


@pytest.fixture
def client():
    """Fixture to initialize the EzekiaAPIClient."""
    return EzekiaAPIClient()


def test_find_by_salesforce_id(client):
    res = client.companies.get_by_salesforce_id("0014H00002N3BJAQA3")
    assert res["name"] == "Delin Property"
