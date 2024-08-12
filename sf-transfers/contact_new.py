from config import get_sf_prod, get_sf_sandbox, get_object_model
from upsert_recursively import upsert_record_and_references

sf_prod = get_sf_prod()
sf_sandbox = get_sf_sandbox()
object_model = get_object_model()

query = f"SELECT Id FROM Contact WHERE Tipo__c = 'Empleado'"
contacts = sf_prod.query_all(query)["records"]

for contact in contacts:
    upsert_record_and_references(
        sf_prod,
        sf_sandbox,
        "Contact",
        contact["Id"],
        {},
        object_model,
    )
