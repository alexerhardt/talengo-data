import os

from dotenv import load_dotenv

from ezekia.base_api import BaseAPIClient

load_dotenv()

DEFAULT_PAGE_SIZE = 200


class EzekiaAPIClient(BaseAPIClient):
    def __init__(self, page_size=DEFAULT_PAGE_SIZE):
        EZEKIA_TOKEN = os.getenv("EZEKIA_SANDBOX_TOKEN")
        EZEKIA_SANDBOX_BASE_API = "https://migrations2.ezekia.com/api"
        super().__init__(EZEKIA_SANDBOX_BASE_API, EZEKIA_TOKEN)
        self.page_size = page_size
        self._people = None
        self._projects = None

    @property
    def people(self):
        if self._people is None:
            self._people = PeopleAPI(self)
        return self._people

    @property
    def projects(self):
        if self._projects is None:
            self._projects = ProjectsAPI(self)
        return self._projects


class PeopleAPI:
    def __init__(self, client):
        self.client = client
        self.page_size = self.client.page_size

    @staticmethod
    def create():
        return PeopleAPI(EzekiaAPIClient())

    def get_count(self):
        count = 0

        res = self.client.get(
            "/people", params={"count": self.page_size, "page": 1, "sortBy": "id"}
        )

        data = res["data"]
        if len(data) == 0:
            return count

        count += len(data)
        last_id = data[-1]["id"]
        while len(data) == self.page_size:
            res = self.client.get(
                "/people",
                params={"count": self.page_size, "sortBy": "id", "from": last_id},
            )
            data = res["data"]
            count += len(data)

        return count

    def get_all(self):
        pass


class ProjectsAPI:
    def __init__(self):
        self.client = EzekiaAPIClient()

    def get_count(self):
        pass

    def get_all(self):
        pass
