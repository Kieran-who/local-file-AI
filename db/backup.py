from .azure_blob_restore import get_most_recent_folder
import uuid
from datetime import datetime
from config import AZURE_STORAGE_CONNECTION_STRING
import re


def uniq_id():
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    unique_id = f"{date_str}-{uuid.uuid4()}"
    allowed_chars = r'[a-z0-9_-]'
    unique_id_clean = re.sub(f'[^{allowed_chars}]', '', unique_id)
    return unique_id_clean


async def create_backup(client, path):
    if AZURE_STORAGE_CONNECTION_STRING:
        id = f'{path}_10_391_92_6_{uniq_id()}'
        allowed_chars = r'[a-z0-9_-]'
        clean_id = re.sub(f'[^{allowed_chars}]', '', id)
        print(clean_id)
        result = client.backup.create(
            backup_id=clean_id.replace(" ", "_"),
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
