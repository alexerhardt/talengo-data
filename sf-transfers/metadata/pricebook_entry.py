import logging

from config import get_sf_sandbox, get_sf_prod, PRODUCTION_ID_KEY

logger = logging.getLogger(__name__)


def copy_pricebook_entry_production_id(
    sf_prod, sf_sandbox, production_id_key=PRODUCTION_ID_KEY
):
    """
    Copies the production id for PriceBookEntry into the sandbox instance.

    PricebookEntry records are copied by default on sandbox creation, so we match them
    by Pricebook2.Name, Product2.Name, CurrencyIsoCode, and UnitPrice, which should
    form a unique identifying tuple.

    Assumes that the the production_id field has already been added to the object.

    :param sf_prod:
    :param sf_sandbox:
    :param production_id_key:
    :return:
    """
    prod_query = """
        SELECT Id, Pricebook2Id, Product2Id, Pricebook2.Name, Product2.Name, CurrencyIsoCode, UnitPrice
        FROM PricebookEntry 
        WHERE IsActive = true
    """
    prod_results = sf_prod.query_all(prod_query)

    for record in prod_results["records"]:
        prod_id = record["Id"]
        logger.info(f"Updating PricebookEntry with production id {prod_id}")
        sandbox_query = f"""
            SELECT Id 
            FROM PricebookEntry 
            WHERE Pricebook2.Name = '{record["Pricebook2"]["Name"]}' 
            AND Product2.Name = '{record["Product2"]["Name"]}'
            AND CurrencyIsoCode = '{record["CurrencyIsoCode"]}'
            AND UnitPrice = {record["UnitPrice"]}
            AND IsActive = true
        """
        sandbox_results = sf_sandbox.query(sandbox_query)
        sandbox_id = sandbox_results["records"][0]["Id"]
        sf_sandbox.PricebookEntry.update(sandbox_id, {production_id_key: prod_id})


if __name__ == "__main__":
    sf_sandbox = get_sf_sandbox()
    sf_prod = get_sf_prod()
    copy_pricebook_entry_production_id(sf_prod, sf_sandbox)
