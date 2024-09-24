from config import get_sf_prod, get_sf_sandbox, get_object_model
from migrate import migrate

sf_prod = get_sf_prod()
sf_sandbox = get_sf_sandbox()


def delete_compensation_in_sandbox():
    query = "SELECT Id FROM Compensation__c"
    records = sf_sandbox.query_all(query)["records"]
    for record in records:
        print(f"Deleting Compensation {record['Id']}")
        sf_sandbox.Compensation__c.delete(record["Id"])


def migrate_compensation():
    object_model = get_object_model()
    query = """
        SELECT Id FROM Compensation__c
        WHERE Commission_Amount__c > 0
    """
    migrate(sf_prod, sf_sandbox, "Compensation__c", object_model, query)


def regenerate_compensation():
    delete_compensation_in_sandbox()
    migrate_compensation()


if __name__ == "__main__":
    delete_compensation_in_sandbox()
