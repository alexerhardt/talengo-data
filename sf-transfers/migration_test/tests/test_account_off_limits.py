from pathlib import Path
import pytest
from joblib import Memory
from config import get_sf_prod
from ezekia.api import EzekiaAPIClient

memory = Memory(Path(__file__).parent / "cache" / "account_off_limits", verbose=0)


@memory.cache
def get_sf_records(sf):
    query = f"""
    SELECT Id, Name, Off_limit__c, Fecha_de_fin_off_limit__c, Descripcion_de_los_Off_limit_de_Contacto__c
    FROM Account 
    WHERE Off_limit__c = True AND Fecha_de_fin_off_limit__c >= TODAY
    """
    return sf.query(query)["records"]


@memory.cache
def get_sf_id_ezekia_off_limits_map(ez, sf_records):
    return ez.off_limits.get_by_list_of_salesforce_company_ids(
        [r["Id"] for r in sf_records]
    )


sf = get_sf_prod()
sf_records = get_sf_records(sf)
sf_records_map = {r["Id"]: r for r in sf_records}

ezekia = EzekiaAPIClient()
sf_id_ezekia_off_limits_map = get_sf_id_ezekia_off_limits_map(ezekia, sf_records)
all_ezekia_off_limits = ezekia.off_limits.get_all_for_companies()


def id_func(sf_id):
    """
    Test helper to get a string representation of a Salesforce ID.
    :param sf_id:
    :return:
    """
    company_name = sf_records_map.get(sf_id, {}).get("Name", "Unknown")
    return f"{company_name} (SF Id: {sf_id})"


@pytest.mark.parametrize("sf_id", sf_id_ezekia_off_limits_map, ids=id_func)
def test_off_limits_found(sf_id):
    assert sf_id_ezekia_off_limits_map[sf_id], f"Off-limits not found"


def test_count():
    assert len(sf_records) == len(all_ezekia_off_limits)


@pytest.mark.parametrize("sf_id", sf_id_ezekia_off_limits_map, ids=id_func)
def test_end_dates_match(sf_id):
    assert (
        sf_id_ezekia_off_limits_map[sf_id]["endDate"]
        == sf_records_map[sf_id]["Fecha_de_fin_off_limit__c"]
    )


@pytest.mark.parametrize("sf_id", sf_id_ezekia_off_limits_map, ids=id_func)
def test_descriptions_match(sf_id):
    assert (
        sf_id_ezekia_off_limits_map[sf_id]["description"]
        == sf_records_map[sf_id]["Descripcion_de_los_Off_limit_de_Contacto__c"]
    )
