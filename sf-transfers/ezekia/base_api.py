import requests


class BaseAPIClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def _get_full_url(self, endpoint):
        return f"{self.base_url}{endpoint}"

    def get(self, endpoint, params=None):
        url = self._get_full_url(endpoint)
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def post(self, endpoint, data=None):
        url = self._get_full_url(endpoint)
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()

    def put(self, endpoint, data=None):
        url = self._get_full_url(endpoint)
        response = requests.put(url, headers=self.headers, json=data)
        return response.json()

    def delete(self, endpoint):
        url = self._get_full_url(endpoint)
        response = requests.delete(url, headers=self.headers)
        return response.json()
