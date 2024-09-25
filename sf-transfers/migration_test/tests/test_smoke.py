import pytest
from ezekia.api import EzekiaAPIClient


@pytest.fixture
def client():
    """Fixture to initialize the EzekiaAPIClient."""
    return EzekiaAPIClient()


def test_find_by_email(client):
    res = client.people.get_by_email("gioconda.pina@cavipetrol.com")
    assert len(res) == 1


def test_people_count(client):
    """Integration smoke test for people count."""
    try:
        count = client.people.get_count()
        print(f"People Count: {count}")
    except Exception as e:
        pytest.fail(f"People count test failed: {e}")


def test_projects_count(client):
    """Integration smoke test for projects count."""
    try:
        count = client.projects.get_count()
        print(f"Projects Count: {count}")
    except Exception as e:
        pytest.fail(f"Projects count test failed: {e}")
