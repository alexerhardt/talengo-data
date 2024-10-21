import json
import os
from simple_salesforce import Salesforce
from dotenv import load_dotenv

load_dotenv()

SF_PROD_USERNAME = os.getenv("SF_PROD_USERNAME")
SF_PROD_PASSWORD = os.getenv("SF_PROD_PASSWORD")
SF_PROD_SECURITY_TOKEN = os.getenv("SF_PROD_SECURITY_TOKEN")

SF_SANDBOX_USERNAME = os.getenv("SF_SANDBOX_USERNAME")
SF_SANDBOX_PASSWORD = os.getenv("SF_SANDBOX_PASSWORD")
SF_SANDBOX_SECURITY_TOKEN = os.getenv("SF_SANDBOX_SECURITY_TOKEN")

PRODUCTION_ID_KEY = "ProductionId__c"


def get_sf_prod():
    return Salesforce(
        username=SF_PROD_USERNAME,
        password=SF_PROD_PASSWORD,
        security_token=SF_PROD_SECURITY_TOKEN,
    )


def get_sf_sandbox():
    return Salesforce(
        username=SF_SANDBOX_USERNAME,
        password=SF_SANDBOX_PASSWORD,
        security_token=SF_SANDBOX_SECURITY_TOKEN,
        domain="test",
    )


def get_object_model():
    path = os.path.join(os.path.dirname(__file__), "data/model.json")
    with open(path) as f:
        return json.load(f)


def get_db_engine():
    from sqlalchemy import create_engine

    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    connection_string = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    return create_engine(connection_string)
