import os

from dotenv import load_dotenv

from ezekia.base_api import BaseAPIClient

load_dotenv()

DEFAULT_PAGE_SIZE = 500


class EzekiaAPIClient(BaseAPIClient):
    def __init__(self, page_size=DEFAULT_PAGE_SIZE):
        EZEKIA_TOKEN = os.getenv("EZEKIA_SANDBOX_TOKEN")
        EZEKIA_SANDBOX_BASE_API = "https://migrations2.ezekia.com/api"
        super().__init__(EZEKIA_SANDBOX_BASE_API, EZEKIA_TOKEN)
        self.page_size = page_size
        self._people = None
        self._projects = None
        self._companies = None

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

    @property
    def companies(self):
        if self._companies is None:
            self._companies = CompaniesAPI(self)
        return self._companies

    def _get_count(self, entity: str) -> int:
        # if entity not in ["people", "projects"]:
        #     raise ValueError(f"Invalid entity: {entity}")

        count = 0
        path = f"/{entity}"

        res = self.get(
            path, params={"count": self.page_size, "page": 1, "sortBy": "id"}
        )

        data = res["data"]
        if len(data) == 0:
            return count

        count += len(data)
        last_id = data[-1]["id"]
        print(f"count: {count} last_id: {last_id}")
        while last_id:
            res = self.get(
                path,
                params={"count": self.page_size, "sortBy": "id", "from": last_id},
            )
            data = res["data"]
            # We need to decrease the count by 1 because the last item's id is used
            # as the starting point for the next page, ie, already counted
            count += len(data) - 1 if data else 0
            last_id = data[-1]["id"] if data else None
            print(f"count: {count} last_id: {last_id}")

        return count


class PeopleAPI:
    def __init__(self, client):
        self.client = client
        self.page_size = self.client.page_size

    @staticmethod
    def create():
        return PeopleAPI(EzekiaAPIClient())

    def get_count(self) -> int:
        return self.client._get_count("v3/people")

    def get_all(self):
        pass

    def get_by_email(self, email: str):
        res = self.client.get(
            "/v3/people", params={"query": email, "filterOn": ["email"]}
        )
        if len(res["data"]) > 1:
            raise ValueError(f"Multiple people found with email: {email}")
        return res["data"]


class CompaniesAPI:
    def __init__(self, client):
        self.client = client

    def get_count(self):
        pass

    def get_all(self):
        pass

    def get_by_salesforce_id(self, salesforce_id: str):
        res = self.client.get(
            "/v3/companies",
            params={
                "query": salesforce_id,
                "filterOn": ["customField"],
                "fields": ["manager.customValues"],
            },
        )
        if len(res["data"]) > 1:
            raise ValueError(
                f"Multiple companies found with salesforceId: {salesforce_id}"
            )
        if not res["data"]:
            raise ValueError(f"No company found with salesforceId: {salesforce_id}")
        return res["data"][0]


class ProjectsAPI:
    def __init__(self, client):
        self.client = client

    def get_count(self):
        return self.client._get_count("projects")

    def get_all(self):
        pass
