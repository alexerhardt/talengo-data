def copy_user_to_employee(sf, env="sandbox"):
    """
    Copies user to employee in Equipo_de_trabajo__c

    :param sf: Salesforce instance
    :param env: Whether the environment is sandbox or production
    :return:
    """
    query = "SELECT Id, Usuario__r.Email FROM Equipo_de_trabajo__c"
    records = sf.query_all(query)["records"]

    for record in records:
        if not record["Usuario__r"]:
            print(f"User not found for Equipo_de_trabajo__c {record['Id']}")
            continue

        email = record["Usuario__r"]["Email"]

        if env == "sandbox":
            email = email.replace(".invalid", "")

        contact = sf.query(f"SELECT Id FROM Contact WHERE Email = '{email}'")["records"]

        if not contact:
            print(f"Contact not found for email {email}")
            continue

        if len(contact) > 1:
            print(f"Multiple contacts found for email {email}")
            continue

        contact_id = contact[0]["Id"]
        try:
            sf.Equipo_de_trabajo__c.update(
                record["Id"], {"ContactoEmpleado__c": contact_id}
            )
            print(
                f"Updated Equipo_de_trabajo__c {record['Id']} with Contact {contact_id} "
                f"email {email}"
            )
        except Exception as e:
            print(
                f"Error updating Equipo_de_trabajo__c {record['Id']} email {email}: "
                f"{e}"
            )


if __name__ == "__main__":
    from config import get_sf_sandbox, get_sf_prod

    sf = get_sf_sandbox()
    copy_user_to_employee(sf)
