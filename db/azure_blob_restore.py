from config import AZURE_STORAGE_CONNECTION_STRING, AZURE_CONTAINER_NAME
from azure.storage.blob import BlobServiceClient


async def get_most_recent_folder():
    connection_str = AZURE_STORAGE_CONNECTION_STRING
    container_name = AZURE_CONTAINER_NAME

    # Create a Blob Service Client object
    blob_service_client = BlobServiceClient.from_connection_string(
        connection_str)
    container_client = blob_service_client.get_container_client(container_name)

    # Initialize an empty dictionary to hold names and creation times
    backups = {}

    # List all blobs in the container
    for blob in container_client.list_blobs():

        if '/' in blob.name:
            name = blob.name.split('/')[0]

        if name not in backups:
            backups[name] = blob.last_modified

    # Get the with the most recent blob
    most_recent_folder = max(backups, key=backups.get)

    return most_recent_folder
