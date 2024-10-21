import requests


class BaseAPIClient(requests.Session):
    def __init__(self, base_url, token):
        super().__init__()
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

    def request(self, method, url, **kwargs):
        full_url = f"{self.base_url}{url}"
        response = super().request(method, full_url, headers=self.headers, **kwargs)
        response.raise_for_status()
        return response.json()
