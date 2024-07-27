import os
from simple_salesforce import Salesforce
from dotenv import load_dotenv

load_dotenv()

SF_PROD_USERNAME = os.getenv('SF_PROD_USERNAME')
SF_PROD_PASSWORD = os.getenv('SF_PROD_PASSWORD')
SF_PROD_SECURITY_TOKEN = os.getenv('SF_PROD_SECURITY_TOKEN')

SF_SANDBOX_USERNAME = os.getenv('SF_SANDBOX_USERNAME')
SF_SANDBOX_PASSWORD = os.getenv('SF_SANDBOX_PASSWORD')
SF_SANDBOX_SECURITY_TOKEN = os.getenv('SF_SANDBOX_SECURITY_TOKEN')


def get_sf_prod():
    return Salesforce(username=SF_PROD_USERNAME, password=SF_PROD_PASSWORD,
                      security_token=SF_PROD_SECURITY_TOKEN)


def get_sf_sandbox():
    return Salesforce(username=SF_SANDBOX_USERNAME, password=SF_SANDBOX_PASSWORD,
                      security_token=SF_SANDBOX_SECURITY_TOKEN, domain='test')
