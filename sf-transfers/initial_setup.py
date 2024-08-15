import logging

from metadata.create_metadata import create_sandbox_metadata
from metadata.pricebook import copy_pricebook_production_id
from metadata.pricebook_entry import copy_pricebook_entry_production_id
from metadata.products import copy_product_production_id

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def run_initial_setup(sf_prod, sf_sandbox, object_model, production_id_key):
    """
    Runs the initial setup for the Salesforce sandbox.

    :param sf_prod:
    :param sf_sandbox:
    :param object_model:
    :param production_id_key:
    :return:
    """
    create_sandbox_metadata(sf_sandbox, object_model)
    copy_product_production_id(sf_prod, sf_sandbox, production_id_key)
    copy_pricebook_production_id(sf_prod, sf_sandbox, production_id_key)
    copy_pricebook_entry_production_id(sf_prod, sf_sandbox, production_id_key)


if __name__ == "__main__":
    from config import get_sf_prod, get_sf_sandbox, get_object_model, PRODUCTION_ID_KEY

    sf_prod = get_sf_prod()
    sf_sandbox = get_sf_sandbox()
    object_model = get_object_model()

    run_initial_setup(sf_prod, sf_sandbox, object_model, PRODUCTION_ID_KEY)
