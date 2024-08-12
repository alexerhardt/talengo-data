from config import get_sf_prod, get_sf_sandbox, get_object_model
from copy_entities import migrate

sf_prod = get_sf_prod()
sf_sandbox = get_sf_sandbox()
object_model = get_object_model()

query = f"SELECT Id FROM Contact WHERE Tipo__c = 'Empleado'"
migrate(sf_prod, sf_sandbox, "Contact", object_model, query)
