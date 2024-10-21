from config import get_sf_sandbox


def change_employee_record_types(sf):
    record_type_name = "Empleado"

    # Fetch the RecordType, as we need its id
    query = f"SELECT Id FROM RecordType WHERE SObjectType = 'Contact' AND DeveloperName = '{record_type_name}'"
    result = sf.query(query)
    if not result["records"]:
        raise ValueError(f"No RecordType found for {record_type_name}")
    record_type_id = result["records"][0]["Id"]

    # Query all Contacts with Tipo__c = 'Empleado'
    contacts_query = "SELECT Id, Tipo__c FROM Contact WHERE Tipo__c = 'Empleado'"
    contacts_result = sf.query_all(contacts_query)

    for contact in contacts_result["records"]:
        contact_id = contact["Id"]
        update_data = {"RecordTypeId": record_type_id}
        # Update the contact
        sf.Contact.update(contact_id, update_data)
        print(f"Updated Contact {contact_id} with RecordType 'Empleado'")


if __name__ == "__main__":
    sf = get_sf_sandbox()
    change_employee_record_types(sf)
