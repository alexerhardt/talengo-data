"""
Copies the production id into the sandbox instance.
"""

from config import get_sf_sandbox, get_sf_prod

sf_production = get_sf_prod()
sf_sandbox = get_sf_sandbox()

query = "SELECT Id, Name FROM Product2 WHERE IsActive = True"
products_production = sf_production.query_all(query)["records"]

for product in products_production:
    product_id = product["Id"]
    product_name = product["Name"]

    sandbox_product = sf_sandbox.query(
        f"SELECT Id FROM Product2 WHERE Name='{product_name}'"
    )

    print(f"Updating {product_name} with production id {product_id}")

    sf_sandbox.Product2.update(
        sandbox_product["records"][0]["Id"], {"ProductionId__c": product_id}
    )
