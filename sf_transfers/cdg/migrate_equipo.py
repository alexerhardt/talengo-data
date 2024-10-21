from config import get_sf_prod, get_sf_sandbox, get_object_model
from migrate import migrate

sf_prod = get_sf_prod()
sf_sandbox = get_sf_sandbox()
object_model = get_object_model()


def migrate_equipo():
    # query = """
    # SELECT Id FROM Equipo_de_trabajo__c
    # WHERE Referencia__r.Status = 'Activada' OR Referencia__r.EffectiveDate >= 2024-01-01
    # """
    query = """
    SELECT Id FROM Equipo_de_trabajo__c 
    WHERE Referencia__r.Status = 'Activada' AND Miembro_del_equipo__c = 'Rosalía Tapia'
    """
    migrate(
        sf_prod,
        sf_sandbox,
        "Equipo_de_trabajo__c",
        object_model,
        query,
    )


if __name__ == "__main__":
    migrate_equipo()
