import os

from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()


def get_blob_container_client():
    AZURE_CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING")
    AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")
    blob_service_client = BlobServiceClient.from_connection_string(
        AZURE_CONNECTION_STRING
    )
    return blob_service_client.get_container_client(AZURE_CONTAINER_NAME)
