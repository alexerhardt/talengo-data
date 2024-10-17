import os

from dotenv import load_dotenv

from ezekia.base_api import BaseAPIClient

load_dotenv()

DEFAULT_PAGE_SIZE = 500


class ConfigurationError(Exception):
    pass


class NotFoundException(Exception):
    pass


class DuplicateFoundException(Exception):
    pass


class EzekiaAPIClient(BaseAPIClient):
    """
    Client for the Ezekia API.
    We use delegation to separate the different API endpoints, and allowing access like:
    ezekia.entity_name.method_name()
    """

    def __init__(self, page_size=DEFAULT_PAGE_SIZE):
        base_url = os.getenv("BASE_URL")
        if not base_url:
            raise ConfigurationError("BASE_URL not set in environment variables.")

        token = os.getenv("SECURITY_TOKEN")
        if not token:
            raise ConfigurationError("SECURITY_TOKEN not set in environment variables.")

        super().__init__(base_url, token)

        self.page_size = page_size
        self._people = None
        self._projects = None
        self._companies = None
        self._off_limits = None

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

    @property
    def off_limits(self):
        if self._off_limits is None:
            self._off_limits = OffLimitsAPI(self)
        return self._off_limits

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

    def get_by_salesforce_id(self, salesforce_id: str):
        res = self.client.get(
            "/v3/people",
            params={
                "query": salesforce_id,
                "filterOn": ["customField"],
                "fields": ["manager.customValues"],
                "fuzzy": False,
            },
        )
        if len(res["data"]) > 1:
            raise DuplicateFoundException(
                f"Multiple people found with salesforceId: {salesforce_id}"
            )
        # Ezekia API does not return 404 on not found
        if not res["data"]:
            raise NotFoundException(f"No people with salesforceId: {salesforce_id}")
        return res["data"][0]

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
                "fuzzy": False,
            },
        )
        if len(res["data"]) > 1:
            raise DuplicateFoundException(
                f"Multiple companies found with salesforceId: {salesforce_id}"
            )
        # Ezekia API does not return 404 on not found
        if not res["data"]:
            raise NotFoundException(
                f"No company found with salesforceId: {salesforce_id}"
            )
        return res["data"][0]

    def get_by_salesforce_id_list(self, salesforce_ids: list) -> dict:
        """
        Retrieves a list of companies by Salesforce ID.
        If a company is not found, the value will be None.
        :param salesforce_ids:
        :return: Map of Salesforce ID to company data
        """
        result = {}
        for salesforce_id in salesforce_ids:
            try:
                result[salesforce_id] = self.get_by_salesforce_id(salesforce_id)
            except NotFoundException:
                result[salesforce_id] = None
        return result


class ProjectsAPI:
    def __init__(self, client):
        self.client = client

    def get_count(self):
        return self.client._get_count("projects")

    def get_all(self):
        pass


class OffLimitsAPI:
    def __init__(self, client):
        self.client = client

    def get_count(self):
        pass

    def get_all_for_companies(self):
        """
        Get all off-limits agreements for all companies.
        :return:
        """
        res = self.client.get("/off-limits/agreements/companies")
        return res["data"]

    def get_all_for_people(self):
        """
        Get all off-limits agreements for all people.
        :return:
        """
        res = self.client.get("/off-limits/agreements/people")
        return res["data"]

    def get_by_company_id(self, company_id: str):
        """
        Get all off-limit agreements for a specific company.
        :param company_id:
        :return: A list of off-limit agreements
        """
        res = self.client.get(
            f"/off-limits/agreements/companies/{company_id}",
        )
        if not res["data"]:
            raise NotFoundException(f"No off limits found with companyId: {company_id}")
        # I don't know how this could happen, it'd be undocumented behavior
        if len(res["data"]) > 1:
            raise DuplicateFoundException(
                f"Multiple off limits found with companyId: {company_id}"
            )
        return res["data"][0]

    def get_by_person_id(self, person_id: str):
        """
        Get all off-limit agreements for a specific person.
        :param person_id:
        :return: A list of off-limit agreements
        """
        res = self.client.get(
            f"/off-limits/agreements/people/{person_id}",
        )
        if not res["data"]:
            raise NotFoundException(f"No off limits found with personId: {person_id}")
        # I don't know how this could happen, it'd be undocumented behavior
        if len(res["data"]) > 1:
            raise DuplicateFoundException(
                f"Multiple off limits found with personId: {person_id}"
            )
        return res["data"][0]

    def get_by_list_of_salesforce_company_ids(self, salesforce_company_ids: list):
        """
        Get all off-limit agreements for a list of companies by salesforce IDs.
        Fetches first the company ID from the salesforce ID.
        :param salesforce_company_ids:
        :return: A list of off-limit agreements
        """
        result = {}
        for salesforce_id in salesforce_company_ids:
            # This will raise NotFoundException if not found
            # Expected, because we assume company exists and should fail loudly
            company = self.client.companies.get_by_salesforce_id(salesforce_id)
            company_id = company["id"]
            try:
                result[salesforce_id] = self.get_by_company_id(company_id)
            except NotFoundException:
                result[salesforce_id] = None
        return result

    def get_by_list_of_salesforce_person_ids(self, salesforce_person_ids: list):
        """
        Get all off-limit agreements for a list of people by salesforce IDs.
        Fetches first the person ID from the salesforce ID.
        :param salesforce_person_ids:
        :return: A list of off-limit agreements
        """
        result = {}
        for salesforce_id in salesforce_person_ids:
            # This will raise NotFoundException if not found
            # Expected, because we assume person exists and should fail loudly
            person = self.client.people.get_by_salesforce_id(salesforce_id)
            person_id = person["id"]
            try:
                result[salesforce_id] = self.get_by_person_id(person_id)
            except NotFoundException:
                result[salesforce_id] = None
        return result
