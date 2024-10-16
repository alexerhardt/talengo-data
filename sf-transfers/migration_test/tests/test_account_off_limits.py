import pytest
from config import get_sf_prod
from ezekia.api import EzekiaAPIClient

sf = get_sf_prod()
query = f"""
SELECT Id, Off_limit__c, Fecha_de_fin_off_limit__c, Descripcion_de_los_off_limit_de_contacto__c 
FROM Account 
WHERE Off_limit__c = True
"""
sf_records = sf.query(query)["records"]

ezekia = EzekiaAPIClient()
sf_to_ezekia_mapped_off_limits = (
    ezekia.off_limits.get_by_list_of_salesforce_company_ids(
        [r["Id"] for r in sf_records]
    )
)
all_ezekia_off_limits = ezekia.off_limits.get_all_for_companies()


@pytest.mark.parametrize("sf_id", sf_to_ezekia_mapped_off_limits)
def test_off_limits_found(sf_id):
    # Check that the value for the mapped Salesforce ID exists and is not None
    assert sf_to_ezekia_mapped_off_limits[sf_id], f"Record with ID {sf_id} is missing"


@pytest.mark.parametrize("ez_ol", all_ezekia_off_limits)
def test_no_extraneous_off_limits(ez_ol, sf_records):
    pass
