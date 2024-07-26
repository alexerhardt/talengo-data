import os
import json
import argparse
from dotenv import load_dotenv
from simple_salesforce import Salesforce

load_dotenv()

parser = argparse.ArgumentParser(description='Fetch Salesforce object fields metadata and save to JSON.')
parser.add_argument('salesforce_object', type=str, help='The Salesforce object to describe (e.g., Contact, Account)')
parser.add_argument('output_file', type=str, help='The output JSON file name (e.g., fields.json)')
args = parser.parse_args()

SF_PROD_USERNAME = os.getenv('SF_PROD_USERNAME')
SF_PROD_PASSWORD = os.getenv('SF_PROD_PASSWORD')
SF_PROD_SECURITY_TOKEN = os.getenv('SF_PROD_SECURITY_TOKEN')
SF_SANDBOX_USERNAME = os.getenv('SF_SANDBOX_USERNAME')
SF_SANDBOX_PASSWORD = os.getenv('SF_SANDBOX_PASSWORD')
SF_SANDBOX_SECURITY_TOKEN = os.getenv('SF_SANDBOX_SECURITY_TOKEN')

sf_prod = Salesforce(username=SF_PROD_USERNAME, password=SF_PROD_PASSWORD, security_token=SF_PROD_SECURITY_TOKEN)
sf_sandbox = Salesforce(username=SF_SANDBOX_USERNAME, password=SF_SANDBOX_PASSWORD, security_token=SF_SANDBOX_SECURITY_TOKEN, domain='test')
fields_metadata = sf_prod.__getattr__(args.salesforce_object).describe()

with open(args.output_file, 'w') as f:
    json.dump({field['name']: field for field in fields_metadata['fields']}, f, indent=4)

print(f"Metadata for {args.salesforce_object} object saved to {args.output_file}")
