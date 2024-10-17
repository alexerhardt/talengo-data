import pytest
from ezekia.base_api import BaseAPIClient

methods = [
    {
        "name": "get",
        "has_data": False,
    },
    {
        "name": "post",
        "has_data": True,
    },
    {
        "name": "put",
        "has_data": True,
    },
    {
        "name": "delete",
        "has_data": False,
    },
    {
        "name": "patch",
        "has_data": True,
    },
]


@pytest.mark.parametrize("method", methods)
def test_method_exists(method):
    """
    Test that the method exists on the client.
    """
    base_url = "https://example.com"
    token = "test_token"
    client = BaseAPIClient(base_url, token)
    request_method = getattr(client, method["name"])
    assert callable(request_method)


@pytest.mark.parametrize("method", methods)
def test_method_called_with_auth_header(method, mocker):
    """
    Test that the method is called with the Authorization header.
    """
    base_url = "https://example.com"
    token = "test_token"
    client = BaseAPIClient(base_url, token)

    mock_method = mocker.patch(f'requests.{method["name"]}')
    mock_method.return_value.status_code = 200
    mock_method.return_value.json.return_value = {}

    request_method = getattr(client, method["name"])
    request_method("/test")

    mock_method.assert_called_once()
    args, kwargs = mock_method.call_args
    assert kwargs["headers"]["Authorization"] == f"Bearer {token}"


@pytest.mark.parametrize("method", methods)
def test_kwargs_passed_to_request(method, mocker):
    """
    Test that the method is called with the correct arguments.
    """
    base_url = "https://example.com"
    token = "test_token"
    client = BaseAPIClient(base_url, token)

    mock_method = mocker.patch(f'requests.{method["name"]}')
    mock_method.return_value.status_code = 200
    mock_method.return_value.json.return_value = {}

    request_method = getattr(client, method["name"])
    request_method("/test", key="value")

    mock_method.assert_called_once()
    args, kwargs = mock_method.call_args
    assert kwargs["key"] == "value"


@pytest.mark.parametrize("method", methods)
def test_response_returned_as_dict(method, mocker):
    """
    Test that the response is returned as a dictionary.
    """
    base_url = "https://example.com"
    token = "test_token"
    client = BaseAPIClient(base_url, token)

    mock_method = mocker.patch(f'requests.{method["name"]}')
    mock_method.return_value.status_code = 200
    mock_method.return_value.json.return_value = {"key": "value"}

    request_method = getattr(client, method["name"])
    response = request_method("/test")

    assert response == {"key": "value"}
