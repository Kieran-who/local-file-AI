from .azure_blob_restore import get_most_recent_folder
import uuid
from datetime import datetime
from config import AZURE_STORAGE_CONNECTION_STRING


def uniq_id():
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    unique_id = f"{date_str}-{uuid.uuid4()}"
    return unique_id


async def create_backup(client):
    if AZURE_STORAGE_CONNECTION_STRING:
        id = uniq_id()
        result = client.backup.create(
            backup_id=id,
            backend='azure',
            wait_for_completion=True,
        )
        return result
    else:
        return "No Azure Back up String Provided"


async def restore_backup(client):
    latest_id = get_most_recent_folder()
    result = await client.backup.restore(
        backup_id=latest_id,
        backend="azure",
        wait_for_completion=True,
    )
    return result
