import requests
from functools import wraps


class BaseAPIClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def _get_full_url(self, endpoint):
        return f"{self.base_url}{endpoint}"

    def _handle_response(self, response):
        response.raise_for_status()
        return response.json()

    def get(self, endpoint, **kwargs):
        url = self._get_full_url(endpoint)
        response = requests.get(url, headers=self.headers, **kwargs)
        return self._handle_response(response)

    def post(self, endpoint, **kwargs):
        url = self._get_full_url(endpoint)
        response = requests.post(url, headers=self.headers, **kwargs)
        return self._handle_response(response)

    def put(self, endpoint, **kwargs):
        url = self._get_full_url(endpoint)
        response = requests.put(url, headers=self.headers, **kwargs)
        return self._handle_response(response)

    def patch(self, endpoint, **kwargs):
        url = self._get_full_url(endpoint)
        response = requests.patch(url, headers=self.headers, **kwargs)
        return self._handle_response(response)

    def delete(self, endpoint, **kwargs):
        url = self._get_full_url(endpoint)
        response = requests.delete(url, headers=self.headers, **kwargs)
        return self._handle_response(response)
