import pytest
from unittest.mock import patch

from ezekia.api import PeopleAPI


@pytest.fixture
def people_api():
    return PeopleAPI.create()


@pytest.fixture
def mock_get(people_api):
    with patch.object(people_api.client, "get") as mock_get:
        yield mock_get


def test_get_count_no_data(people_api, mock_get):
    """
    Test that get_count returns 0 when the API returns no data.
    """
    mock_get.return_value = {"data": []}

    count = people_api.get_count()
    assert count == 0
    assert mock_get.call_count == 1


def test_get_count_partial_data(people_api, mock_get):
    """
    Test that get_count returns correct count when the API returns less than page_size items.
    """
    data = [{"id": i} for i in range(1, 100)]  # Less than default page_size (200)

    mock_get.return_value = {"data": data}

    count = people_api.get_count()
    assert count == len(data)
    assert mock_get.call_count == 1


def test_get_count_exact_page_size(people_api, mock_get):
    """
    Test that get_count correctly handles data exactly equal to page_size.
    """
    page_size = people_api.page_size
    first_page = [{"id": i} for i in range(1, page_size + 1)]
    second_page = [{"id": page_size}]

    mock_get.side_effect = [{"data": first_page}, {"data": second_page}]

    count = people_api.get_count()
    assert count == page_size
    assert mock_get.call_count == 2


def test_get_count_multiple_pages(people_api, mock_get):
    """
    Test that get_count correctly counts multiple pages of data.
    """
    page_size = people_api.page_size

    # The next page starts with the previous id, this is due to Ezekia API limitations
    # Ids per page: 1 [1-200]; 2 [200, 399]; 3 [399, 409]
    data_page_1 = [{"id": i} for i in range(1, page_size + 1)]
    data_page_2 = [{"id": i} for i in range(page_size, 2 * page_size)]
    data_page_3 = [{"id": i} for i in range(2 * page_size - 1, 2 * page_size + 10)]
    total_count = page_size * 2 + 9

    mock_get.side_effect = [
        {"data": data_page_1},
        {"data": data_page_2},
        {"data": data_page_3},
    ]

    count = people_api.get_count()
    assert count == total_count
    assert mock_get.call_count == 3


def test_get_count_multiple_full_pages(people_api, mock_get):
    """
    Test that get_count correctly handles when total data is a multiple of page_size.
    """
    page_size = people_api.page_size

    # The next page starts with the previous id, this is due to Ezekia API limitations
    # Ids per page: 1 [1-200]; 2 [200, 399]; 3 [399, 599]; 4 [599, 600]
    # TODO: Could abstract this into a generator function
    data_page_1 = [{"id": i} for i in range(1, page_size + 1)]
    data_page_2 = [{"id": i} for i in range(page_size, 2 * page_size)]
    data_page_3 = [{"id": i} for i in range(2 * page_size - 1, 3 * page_size - 1)]
    data_page_4 = [{"id": 598}, {"id": 599}, {"id": 600}]
    total_count = 600

    mock_get.side_effect = [
        {"data": data_page_1},
        {"data": data_page_2},
        {"data": data_page_3},
        {"data": data_page_4},  # Last call returns empty data
    ]

    count = people_api.get_count()
    assert count == total_count
    assert mock_get.call_count == 4


def test_get_count_no_data_key(people_api, mock_get):
    """
    Test that get_count raises KeyError when the API response lacks 'data' key.
    """
    mock_get.return_value = {}

    with pytest.raises(KeyError):
        people_api.get_count()
