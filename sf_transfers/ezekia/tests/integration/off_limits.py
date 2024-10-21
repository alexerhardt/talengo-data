import pytest
from config import get_sf_prod
from ezekia.api import EzekiaAPIClient


def test_off_limits_by_sf_id():
    sf = get_sf_prod()
    query = f"""
    SELECT Id, Off_limit__c, Fecha_de_fin_off_limit__c, Descripcion_de_los_off_limit_de_contacto__c 
    FROM Account 
    WHERE Off_limit__c = True LIMIT 3
    """
    sf_records = sf.query(query)["records"]
    ezekia = EzekiaAPIClient()
    ezekia.off_limits.get_by_list_of_salesforce_company_ids(
        [r["Id"] for r in sf_records]
    )
