from pathlib import Path
import pytest
from joblib import Memory
from config import get_sf_prod
from ezekia.api import EzekiaAPIClient

memory = Memory(Path(__file__).parent / ".cache" / "contact_off_limits", verbose=0)


@memory.cache
def get_sf_records(sf):
    query = f"""
    SELECT Id, FirstName, LastName, Off_limit__c, Fecha_Fin_Off_Limit__c, Motivo_de_Off_Limit__c, Tipo__c
    FROM Contact 
    WHERE Off_limit__c = True 
    AND Fecha_Fin_Off_Limit__c >= TODAY 
    AND Tipo__c != 'Participante' AND Tipo__c != 'Interlocutor'
    """
    return sf.query(query)["records"]


@memory.cache
def get_sf_id_ezekia_off_limits_map(sf_records):
    return EzekiaAPIClient().off_limits.get_by_list_of_salesforce_person_ids(
        [r["Id"] for r in sf_records]
    )


sf = get_sf_prod()
sf_records = get_sf_records(sf)
sf_records_map = {r["Id"]: r for r in sf_records}

sf_id_ezekia_off_limits_map = get_sf_id_ezekia_off_limits_map(sf_records)
all_ezekia_off_limits = EzekiaAPIClient().off_limits.get_all_for_people()


def id_func(sf_id):
    """
    Test helper to get a string representation of a Salesforce ID.
    :param sf_id:
    :return:
    """
    first = sf_records_map.get(sf_id, {}).get("FirstName", "Unknown")
    last = sf_records_map.get(sf_id, {}).get("LastName", "Unknown")
    return f"{first} {last} (SF Id: {sf_id})"


@pytest.mark.parametrize("sf_id", sf_id_ezekia_off_limits_map, ids=id_func)
def test_off_limits_found(sf_id):
    assert sf_id_ezekia_off_limits_map[sf_id], f"Off-limits not found"


def test_count():
    assert len(sf_records) == len(all_ezekia_off_limits)


@pytest.mark.parametrize("sf_id", sf_id_ezekia_off_limits_map, ids=id_func)
def test_end_dates_match(sf_id):
    assert (
        sf_id_ezekia_off_limits_map[sf_id]["endDate"]
        == sf_records_map[sf_id]["Fecha_Fin_Off_Limit__c"]
    )


@pytest.mark.parametrize("sf_id", sf_id_ezekia_off_limits_map, ids=id_func)
def test_descriptions_match(sf_id):
    assert (
        sf_id_ezekia_off_limits_map[sf_id]["description"]
        == sf_records_map[sf_id]["Motivo_de_Off_Limit__c"]
    )
