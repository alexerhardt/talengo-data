from config import get_sf_prod, get_sf_sandbox, get_object_model
from migrate import migrate


def migrate_employees(sf_prod, sf_sandbox, object_model):
    """
    Migrates all employee Contacts

    :param sf_prod:
    :param sf_sandbox:
    :param object_model:
    :return:
    """
    query = f"SELECT Id FROM Contact WHERE Tipo__c = 'Empleado'"
    migrate(sf_prod, sf_sandbox, "Contact", object_model, query)


if __name__ == "__main__":
    sf_prod = get_sf_prod()
    sf_sandbox = get_sf_sandbox()
    object_model = get_object_model()
    migrate_employees(sf_prod, sf_sandbox, object_model)
