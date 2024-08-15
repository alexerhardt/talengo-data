import logging

from config import PRODUCTION_ID_KEY

logger = logging.getLogger(__name__)


def copy_pricebook_production_id(
    sf_prod, sf_sandbox, production_id_key=PRODUCTION_ID_KEY
):
    """
    Copies the production id for PriceBook into the sandbox instance.

    Pricebook records are copied by default on sandbox creation, so we match them
    by Name, which should form a unique identifying tuple.

    Assumes that the the production_id field has already been added to the object.

    :param sf_prod:
    :param sf_sandbox:
    :param production_id_key:
    :return:
    """
    prod_query = """
        SELECT Id, Name
        FROM Pricebook2
    """
    prod_results = sf_prod.query_all(prod_query)

    for record in prod_results["records"]:
        prod_id = record["Id"]
        logger.info(f"Updating Pricebook with production id {prod_id}")
        sandbox_query = f"""
            SELECT Id 
            FROM Pricebook2
            WHERE Name = '{record["Name"]}'
        """
        sandbox_results = sf_sandbox.query(sandbox_query)
        sandbox_id = sandbox_results["records"][0]["Id"]
        sf_sandbox.Pricebook2.update(sandbox_id, {production_id_key: prod_id})
