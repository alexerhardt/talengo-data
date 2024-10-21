from config import get_sf_prod, get_sf_sandbox, get_object_model
from migrate import migrate

sf_prod = get_sf_prod()
sf_sandbox = get_sf_sandbox()
object_model = get_object_model()

query = "SELECT Id FROM Facturas__c WHERE Anno_Factura_Reporte__c = 2024"

migrate(sf_prod, sf_sandbox, "Facturas__c", object_model, query, False)
