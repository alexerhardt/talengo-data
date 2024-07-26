from dotenv import load_dotenv
from simple_salesforce import Salesforce
import os

load_dotenv()

SF_PROD_USERNAME = os.getenv('SF_PROD_USERNAME')
SF_PROD_PASSWORD = os.getenv('SF_PROD_PASSWORD')
SF_PROD_SECURITY_TOKEN = os.getenv('SF_PROD_SECURITY_TOKEN')

SF_SANDBOX_USERNAME = os.getenv('SF_SANDBOX_USERNAME')
SF_SANDBOX_PASSWORD = os.getenv('SF_SANDBOX_PASSWORD')
SF_SANDBOX_SECURITY_TOKEN = os.getenv('SF_SANDBOX_SECURITY_TOKEN')

# Authenticate with the production instance
sf_prod = Salesforce(username=SF_PROD_USERNAME, password=SF_PROD_PASSWORD,
                     security_token=SF_PROD_SECURITY_TOKEN)

# Authenticate with the sandbox instance
sf_sandbox = Salesforce(username=SF_SANDBOX_USERNAME, password=SF_SANDBOX_PASSWORD,
                        security_token=SF_SANDBOX_SECURITY_TOKEN, domain='test')

# Get all field names for the Contact object in production
basic_metadata = sf_prod.Contact.metadata()
fields_metadata = sf_prod.Contact.describe()

# Filter out fields that are not creatable
fields = [field['name'] for field in fields_metadata['fields'] if field['createable']]

# Construct a query to get all fields
query = f"SELECT {', '.join(fields)} FROM Contact WHERE Tipo__c = 'Empleado'"
contacts = sf_prod.query_all(query)['records']

# Upsert data into the sandbox, excluding system fields and handling read-only fields
for contact in contacts:
    # Check that there is no Contact with the same Email in the sandbox
    query = f"SELECT Id FROM Contact WHERE Email = '{contact.get('Email')}'"
    existing_contact = sf_sandbox.query_all(query)['records']
    if existing_contact:
        continue

    contact_data = {field: contact.get(field) for field in fields if
                    field != 'Id' and field != 'AccountId' and field != "Curriculum_Vitae__c" and field != "OwnerId"}
    try:
        sf_sandbox.Contact.create(contact_data)
        print(
            f"Inserted Contact: {contact.get('FirstName', '')} {contact.get('LastName', '')}")
    except Exception as e:
        print(
            f"Error inserting Contact {contact.get('FirstName', '')} {contact.get('LastName', '')}: {e}")
