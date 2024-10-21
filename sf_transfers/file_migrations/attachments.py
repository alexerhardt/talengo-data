import argparse
import logging
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, quote

import requests
from tenacity import stop_after_attempt, wait_exponential, retry, RetryError

from config import get_sf_prod
from file_migrations.azure_setup import get_blob_container_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.propagate = False
logging.getLogger("azure").setLevel(logging.WARNING)

sf = get_sf_prod()
blob_container_client = get_blob_container_client()

MAX_WORKERS = 10
MAX_RETRIES = 5
WAIT_MULTIPLIER = 1
DEFAULT_LIMIT = None
ATTACHMENT_TYPE = "Attachment"
DOCUMENT_TYPE = "ContentDocument"


def main(record_type=ATTACHMENT_TYPE, limit=DEFAULT_LIMIT):
    logger.info(f"Copying {record_type}s from Salesforce to Azure")

    if record_type == DOCUMENT_TYPE:
        records = get_content_document_versions_from_salesforce()
    elif record_type == ATTACHMENT_TYPE:
        records = get_attachments_from_salesforce()
    else:
        raise ValueError(f"Invalid record type: {record_type}")

    logger.info(f"Retrieved {len(records)} {record_type}s from Salesforce")

    processed_ids = get_processed_ids_from_azure()
    records_to_process = filter_processed_records(records, processed_ids, limit)

    logger.info(f"Processing {len(records_to_process)} {record_type}s")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(process_record, rec, record_type): rec
            for rec in records_to_process
        }
        for future in as_completed(futures):
            record = futures[future]
            try:
                future.result()
            except RetryError as e:  # Log the original exception that caused RetryError
                logger.error(
                    f"Error processing {record_type} record {record['Id']}: "
                    f"{str(e.last_attempt.exception())}"
                )
            except Exception as e:
                logger.error(f"Error processing record {record['Id']}: {str(e)}")


def get_processed_ids_from_azure():
    blob_names = set()

    blob_list = blob_container_client.list_blobs()
    for blob in blob_list:
        blob_names.add(blob.name)

    return blob_names


def filter_processed_records(records, processed_ids, limit):
    return [record for record in records if record["Id"] not in processed_ids][:limit]


def get_content_document_versions_from_salesforce():
    parent_records = get_all_document_parent_records()
    raw_records = get_document_versions_from_records(parent_records)
    flattened_records = standardize_document_version_records(raw_records)
    return flattened_records


def get_all_document_parent_records():
    result = []
    s_objects = ["Curriculum_Vitae__c", "Contact", "Asset", "Entrevista_inicial__c"]
    for s_object in s_objects:
        query = f"SELECT Id FROM {s_object}"
        result.extend(sf.query_all(query)["records"])
    return result


def get_document_versions_from_records(records):
    result = []
    ids = [record["Id"] for record in records]
    while len(ids) > 0:
        ids_string = f"'{ids.pop()}'"  # Start the where clause
        while len(ids) > 0 and len(ids_string) < 4000 - 18:
            ids_string += f",'{ids.pop()}'"
        query = create_content_document_link_query(ids_string)
        query_result = sf.query_all(query)
        result.extend(query_result["records"])
    return result


def create_content_document_link_query(ids_string):
    return f"""
        SELECT ContentDocument.LatestPublishedVersion.Id,
               ContentDocument.LatestPublishedVersion.VersionDataUrl,  
               ContentDocument.LatestPublishedVersion.PathOnClient,
               LinkedEntityId,
               LinkedEntity.Type
        FROM ContentDocumentLink
        WHERE LinkedEntityId IN ({ids_string})
        ORDER BY ContentDocumentId
    """


def standardize_document_version_records(records):
    """
    Makes document version records have the same shape as an Attachment record.
    :param records:
    :return:
    """
    result = []
    for record in records:
        latest_content_doc_version = record["ContentDocument"]["LatestPublishedVersion"]
        result.append(
            {
                "Id": latest_content_doc_version["Id"],
                "Body": latest_content_doc_version["VersionDataUrl"],
                "Name": latest_content_doc_version["PathOnClient"],
                "ParentId": record["LinkedEntityId"],
                "Parent": {"Type": record["LinkedEntity"]["Type"]},
            }
        )
    return result


def get_attachments_from_salesforce():
    logger.info("Fetching attachments from Salesforce")

    last_id = None
    all_records = []

    while True:
        query = f"""
                SELECT Id, Name, Body, ParentId, Parent.Type FROM Attachment
                WHERE Parent.Type IN ('Curriculum_Vitae__c', 'Contact', 'Asset', 'Entrevista_inicial__c')
                {f"AND Id > '{last_id}'" if last_id else ""}
                ORDER BY Id
        """
        result = sf.query(query)
        records = result["records"]
        all_records.extend(records)

        if len(records) == 0:
            break

        last_id = records[-1]["Id"]

    return all_records


def process_record(record, record_type):
    record_id = record["Id"]
    body_url = record["Body"]
    file_name = record["Name"]
    parent_id = record["ParentId"]
    parent_type = record["Parent"]["Type"]

    if record_type == ATTACHMENT_TYPE:
        full_url = urljoin(sf.base_url, body_url)
    else:
        full_url = body_url

    body = fetch_file_body_from_salesforce(full_url)

    metadata = {
        "type": record_type,
        "id": record_id,
        "asciiFileName": quote(file_name),  # Azure doesn't like special characters
        "parentId": parent_id,
        "parentType": parent_type,
    }

    save_file_to_azure(record_id, body, metadata)

    return record_id


@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_exponential(multiplier=WAIT_MULTIPLIER),
)
def fetch_file_body_from_salesforce(full_url):
    """
    Fetch the file body (binary data) from the URL.
    """
    headers = {
        "Authorization": f"Bearer {sf.session_id}",
    }
    response = requests.get(full_url, headers=headers)

    if response.status_code == 200:
        return response.content  # This is the binary content of the file
    else:
        raise Exception(
            f"Failed to fetch body for Attachment {full_url}; "
            f"Status Code: {response.status_code}, "
            f"Response Text: {response.text}"
        )


@retry(
    stop=stop_after_attempt(MAX_RETRIES),
    wait=wait_exponential(multiplier=WAIT_MULTIPLIER),
)
def save_file_to_azure(blob_name, content, metadata, tags=None):
    blob_client = blob_container_client.get_blob_client(blob_name)
    blob_client.upload_blob(content, metadata=metadata)
    if tags:
        blob_client.set_tags(tags)
    logger.info(f"File {blob_name} uploaded to Azure with metadata {metadata}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process Salesforce attachments to Azure."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help=f"Limit the number of files to process (default: {DEFAULT_LIMIT})",
    )
    parser.add_argument(
        "--type",
        type=str,
        default=ATTACHMENT_TYPE,
        help="Type of records to process (attachments or documents)",
    )
    args = parser.parse_args()
    main(args.type, args.limit)
