"""
Copies the production id into the sandbox instance.
"""

import logging

from config import get_sf_sandbox, get_sf_prod, PRODUCTION_ID_KEY

logger = logging.getLogger(__name__)


def copy_product_production_id(
    sf_prod, sf_sandbox, production_id_key=PRODUCTION_ID_KEY
):
    query = "SELECT Id, Name FROM Product2 WHERE IsActive = True"
    products_production = sf_prod.query_all(query)["records"]

    for product in products_production:
        product_id = product["Id"]
        product_name = product["Name"]

        sandbox_product = sf_sandbox.query(
            f"SELECT Id FROM Product2 WHERE Name='{product_name}'"
        )

        logger.info(f"Updating {product_name} with production id {product_id}")

        sf_sandbox.Product2.update(
            sandbox_product["records"][0]["Id"], {production_id_key: product_id}
        )


if __name__ == "__main__":
    sf_prod = get_sf_prod()
    sf_sandbox = get_sf_sandbox()
    copy_product_production_id(sf_prod, sf_sandbox)
