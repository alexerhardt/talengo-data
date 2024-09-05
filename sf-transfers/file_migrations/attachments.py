import argparse
import base64
import logging
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from tenacity import stop_after_attempt, wait_exponential, retry

from config import get_sf_prod
from file_migrations.azure_setup import get_blob_container_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

sf = get_sf_prod()
blob_container_client = get_blob_container_client()

MAX_WORKERS = 16
MAX_RETRIES = 5
WAIT_MULTIPLIER = 1


def main(limit=20):
    processed_ids = get_processed_ids()
    attachments = get_attachments_from_salesforce()
    logger.info(f"Retrieved {len(attachments)} attachments from Salesforce")
    attachments_to_process = [
        att for att in attachments if att["Id"] not in processed_ids
    ][:limit]

    logger.info(f"Processing {len(attachments_to_process)} attachments")

    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = {
            executor.submit(process_attachment, att): att
            for att in attachments_to_process
        }
        for future in as_completed(futures):
            record = futures[future]
            try:
                record_id = future.result()
                logger.info(f"Processed record {record_id}")
            except Exception as e:
                logger.error(f"Error processing record {record['Id']}: {str(e)}")


def get_processed_ids():
    blob_names = set()

    blob_list = blob_container_client.list_blobs()
    logger.info(f"Retrieved blob list in the container")
    for blob in blob_list:
        blob_names.add(blob.name)

    return blob_names


def get_attachments_from_salesforce():
    logger.info("Fetching attachments from Salesforce")
    query = """
        SELECT Id, Name, Body, ParentId, Parent.Type FROM Attachment
        WHERE Parent.Type IN ('Curriculum_Vitae__c', 'Contact', 'Asset', 'Entrevista_inicial__c')
    """
    result = sf.query(query)
    return result["records"]


def process_attachment(record):
    record_id = record["Id"]
    body_url = record["Body"]
    file_name = record["Name"]
    parent_id = record["ParentId"]
    parent_type = record["Parent"]["Type"]

    body_encoded = fetch_attachment_body(body_url)
    body_decoded = base64.b64decode(body_encoded)

    metadata = {
        "id": record_id,
        "bodyUrl": body_url,
        "fileName": file_name,
        "parentId": parent_id,
        "type": "Attachment",
        "parentType": parent_type,
    }

    save_file_to_azure(record_id, body_decoded, metadata)

    return record_id


@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_exponential(multiplier=WAIT_MULTIPLIER),
)
def save_file_to_azure(blob_name, content, metadata):
    blob_client = blob_container_client.get_blob_client(blob_name)
    blob_client.upload_blob(content, metadata=metadata)
    logger.info(f"File {blob_name} uploaded to Azure with metadata {metadata}")


@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_exponential(multiplier=WAIT_MULTIPLIER),
)
def fetch_attachment_body(body_url):
    """Fetch the attachment body (binary data) from the Body URL."""
    full_url = sf.base_url + body_url
    headers = {
        "Authorization": f"Bearer {sf.session_id}",
        "Content-Type": "application/octet-stream",
    }
    response = requests.get(full_url, headers=headers)

    if response.status_code == 200:
        return response.content  # This is the binary content of the file
    else:
        raise Exception(f"Failed to fetch body for Attachment {body_url}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process Salesforce attachments to Azure."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Limit the number of files to process (default: 20)",
    )
    args = parser.parse_args()

    logger.info("About to start the party")

    main()
