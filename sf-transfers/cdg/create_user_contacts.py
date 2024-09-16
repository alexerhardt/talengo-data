from config import get_sf_sandbox


def create_user_contacts(sf):
    users = sf.query(
        "SELECT Id, Email, FirstName, LastName, Cargo__c FROM User WHERE Cargo__c != NULL"
    )

    for user in users["records"]:
        email = user["Email"].replace(".invalid", "")
        first_name = user["FirstName"]
        last_name = user["LastName"]
        cargo = user["Cargo__c"]

        contact_query = f"SELECT Id, CargoCdG__c FROM Contact WHERE Email = '{email}'"
        contact_result = sf.query(contact_query)

        if contact_result["totalSize"] == 0:
            new_contact = {
                "Email": email,
                "FirstName": first_name,
                "LastName": last_name,
                "Tipo__c": "Empleado",
                "CargoCdG__c": cargo,
                "Salutation": "Sra.",
            }
            contact = sf.Contact.create(new_contact)
            print(f"Created Contact: {contact['id']} for User: {user['Id']}")
        else:
            contact_id = contact_result["records"][0]["Id"]
            update_contact = {"CargoCdG__c": cargo}
            sf.Contact.update(contact_id, update_contact)
            print(f"Updated Contact: {contact_id} for User: {user['Id']}")


if __name__ == "__main__":
    sf = get_sf_sandbox()
    create_user_contacts(sf)