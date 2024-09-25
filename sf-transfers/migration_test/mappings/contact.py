contact_mapping = [
    {
        "sourceKey": "Id",
        "targetKey": "manager.CustomValues[].value",
        "mappingType": "nested",
    },
    {
        "sourceKey": "Title",
        "targetKey": "Title",
        "mappingType": "plain",
        "accessor": None,
    },
    {
        "targetKey": "fullName",
        "mappingType": "function",
        "mappingFunction": lambda x: f"{x['FirstName']} {x['LastName']}",
    },
    {
        "targetKey": "lastName",
        "mappingType": "function",
        "mappingFunction": lambda x: f"{x['LastName']} {x['Apellido_2__c']}",
    },
    {
        "sourceKey": "Email",
        "targetKey": "emails[].address",
        "mappingType": "nested",
    },
    {
        "sourceKey": "Email_Personal__c",
        "targetKey": "emails[].address",
        "mappingType": "nested",
    },
    {
        "sourceKey": "Phone",
        "targetKey": "phones[].number",
        "mappingType": "nested",
    },
    {
        "sourceKey": "OtherPhone",
        "targetKey": "phones[].number",
        "mappingType": "nested",
    },
    {
        "sourceKey": "MobilePhone",
        "targetKey": "phones[].number",
        "mappingType": "nested",
    },
    {
        "sourceKey": "LinkedInLink__c",
        "targetKey": "links[].url",
        "mappingType": "nested",
    },
    {
        "sourceKey": "MailingStreet",
        "targetKey": "addresses[].street",
        "mappingType": "nested",
    },
    {
        "sourceKey": "MailingPostalCode",
        "targetKey": "addresses[].postcode",
        "mappingType": "nested",
    },
    {
        "sourceKey": "MailingState",
        "targetKey": "addresses[].state",
        "mappingType": "nested",
    },
    {
        "sourceKey": "MailingCountry",
        "targetKey": "addresses[].country",
        "mappingType": "nested",
    },
]
