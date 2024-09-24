import pytest
from unittest.mock import patch

from ezekia.api import PeopleAPI


def test_get_count_no_data():
    """
    Test that get_count returns 0 when the API returns no data.
    """
    people_api = PeopleAPI.create()

    with patch.object(people_api.client, "get") as mock_get:
        # Mock the get method to return empty data
        mock_get.return_value = {"data": []}

        count = people_api.get_count()
        assert count == 0
        assert mock_get.call_count == 1


def test_get_count_partial_data():
    """
    Test that get_count returns correct count when the API returns less than page_size items.
    """
    people_api = PeopleAPI.create()
    data = [{"id": i} for i in range(1, 100)]  # Less than default page_size (200)

    with patch.object(people_api.client, "get") as mock_get:
        mock_get.return_value = {"data": data}

        count = people_api.get_count()
        assert count == len(data)
        assert mock_get.call_count == 1
