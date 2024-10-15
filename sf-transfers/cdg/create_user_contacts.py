from config import get_sf_prod, get_sf_sandbox


def create_user_contacts(sf):
    users = sf.query(
        """
        SELECT Id, Email, FirstName, LastName, Cargo__c 
        FROM User WHERE IsActive = true AND UserType = 'Standard'
        """
    )

    for user in users["records"]:
        if user["Email"].endswith(
            (
                "salesforce.com",
                "alexerhardt.com",
                "hom2eac.ext",
            )
        ):
            continue

        print(
            f"Processing User: "
            f"{user['Id']}, {user['Email']} {user['FirstName']} {user['LastName']}"
        )
        email = user["Email"].replace(".invalid", "")
        first_name = user["FirstName"]
        last_name = user["LastName"]
        cargo = user["Cargo__c"] if user["Cargo__c"] else None

        contact_query = f"SELECT Id, FirstName, LastName, CargoCdG__c FROM Contact WHERE Email = '{email}'"
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
            print(f"Created Employee Contact: {contact['id']} for User: {user['Id']}")
        else:
            contact_id = contact_result["records"][0]["Id"]
            contact_first = contact_result["records"][0]["FirstName"]
            contact_last = contact_result["records"][0]["LastName"]

            if first_name != contact_first or last_name != contact_last:
                print(
                    f"Contact name {contact_first} {contact_last} mismatch: "
                    f"overwrite with user name {first_name} {last_name}"
                )

            update_contact = {
                "FirstName": first_name,
                "LastName": last_name,
                "CargoCdG__c": cargo,
            }
            sf.Contact.update(contact_id, update_contact)
            print(f"Updated Employee Contact: {contact_id} for User: {user['Id']}")


if __name__ == "__main__":
    sf = get_sf_sandbox()
    create_user_contacts(sf)
