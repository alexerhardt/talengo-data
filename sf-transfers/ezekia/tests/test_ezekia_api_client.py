import pytest
from ezekia.api import (
    EzekiaAPIClient,
    PeopleAPI,
    ProjectsAPI,
    CompaniesAPI,
    OffLimitsAPI,
    DEFAULT_PAGE_SIZE,
    ConfigurationError,
)


def test_fails_if_no_token(monkeypatch):
    """
    Test that the EzekiaAPIClient fails if no token is provided.
    """
    monkeypatch.delenv("SECURITY_TOKEN")
    with pytest.raises(ConfigurationError):
        EzekiaAPIClient()


def test_fails_if_no_base_url(monkeypatch):
    """
    Test that the EzekiaAPIClient fails if no base URL is provided.
    """
    monkeypatch.delenv("BASE_URL")
    with pytest.raises(ConfigurationError):
        EzekiaAPIClient()


def test_page_size(monkeypatch):
    """
    Test that the EzekiaAPIClient initializes correctly.
    """
    monkeypatch.setenv("SECURITY_TOKEN", "test_token")
    client = EzekiaAPIClient()
    assert client.page_size == DEFAULT_PAGE_SIZE


def test_people_property(monkeypatch):
    """
    Test the people property initializes PeopleAPI correctly.
    """
    monkeypatch.setenv("EZEKIA_SANDBOX_TOKEN", "test_token")
    client = EzekiaAPIClient()

    people_api = client.people

    assert isinstance(people_api, PeopleAPI)
    assert client._people is people_api
    assert client.people is people_api  # Singleton behavior


def test_projects_property(monkeypatch):
    """
    Test the projects property initializes ProjectsAPI correctly.
    """
    monkeypatch.setenv("EZEKIA_SANDBOX_TOKEN", "test_token")
    client = EzekiaAPIClient()

    projects_api = client.projects

    assert isinstance(projects_api, ProjectsAPI)
    assert client._projects is projects_api
    assert client.projects is projects_api


def test_companies_property(monkeypatch):
    """
    Test the companies property initializes CompaniesAPI correctly.
    """
    monkeypatch.setenv("EZEKIA_SANDBOX_TOKEN", "test_token")
    client = EzekiaAPIClient()

    companies_api = client.companies

    assert isinstance(companies_api, CompaniesAPI)
    assert client._companies is companies_api
    assert client.companies is companies_api


def test_off_limits_property(monkeypatch):
    """
    Test the off_limits property initializes OffLimitsAPI correctly.
    """
    monkeypatch.setenv("EZEKIA_SANDBOX_TOKEN", "test_token")
    client = EzekiaAPIClient()

    off_limits_api = client.off_limits

    assert isinstance(off_limits_api, OffLimitsAPI)
    assert client._off_limits is off_limits_api
    assert client.off_limits is off_limits_api
