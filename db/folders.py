from .db_instance import DBClient
from utils.azure_open_ai import get_vector
import pandas as pd
from IPython.display import HTML

"""
folder = {
summary: str,
name: str,
file_path: str,
documents: array of documents,
folders: array of folders
}
"""

# function for jupyter notebook styling


def display_res(data):
    def flatten(item):
        documents = item.get("documents") or []
        folders = item.get("folders") or []

        return {
            "Distance": item.get("_additional", {}).get("distance"),
            "Name": item["name"],
            "File Path": item["file_path"],
            "Summary": item["summary"].replace("\n", "<br/>"),
            "Documents": "<br>– ".join([doc['name'] for doc in documents])[6:] if documents else "",
            "Folders": "<br>– ".join([folder['name'] for folder in folders])[6:] if folders else "",
        }

    def explore_json(json_list):
        rows = []
        for item in json_list:
            rows.append(flatten(item))
        return rows

    df = pd.DataFrame(explore_json(data))
    return HTML(df.to_html(escape=False, index=False))


async def search_folders(query):
    client = await DBClient()
    vector = await get_vector(query)
    result = (
        client.query
        .get("Folder", ["summary", "name", "file_path", "folders { ... on Folder { name summary file_path } }", "documents { ... on Document { name summary file_path} }"])
        .with_near_vector({
            "vector": vector})
        .with_additional(["id", "creationTimeUnix", "distance"])
        .do()
    )
    return {"raw": result["data"]["Get"]["Folder"], "notebook": display_res(result["data"]["Get"]["Folder"])}


async def delete_folder(id):
    client = await DBClient()
    client.data_object.delete(
        id,
        class_name="Folder",
    )


async def get_all_folders():
    client = await DBClient()
    result = (
        client.query
        .get("Folder", ["summary", "name", "file_path", "folders { ... on Folder { name } }", "documents { ... on Document { name } }"])
        .with_additional(["id", "creationTimeUnix"])
        .do()
    )
    return result["data"]["Get"]["Folder"]


async def folder_getter(id):
    client = await DBClient()
    doc = client.data_object.get_by_id(id, class_name="Folder")
    return doc


async def new_folder(data_obj, document_ids, folder_ids):
    client = await DBClient()
    custom_vector = []
    if data_obj["summary"]:
        custom_vector = await get_vector(data_obj["summary"])
    else:  # if no summary, use name
        custom_vector = await get_vector(data_obj["name"])
    new_folder = client.data_object.create(
        data_obj,
        "Folder",
        vector=custom_vector
    )
    if document_ids:
        for doc_id in document_ids:
            client.data_object.reference.add(
                new_folder,
                "documents",
                doc_id,
                from_class_name="Folder",
                to_class_name="Document",
            )
    if folder_ids:
        for folder_id in folder_ids:
            client.data_object.reference.add(
                new_folder,
                "folders",
                folder_id,
                from_class_name="Folder",
                to_class_name="Folder",
            )
    return new_folder


async def search_folder_hash(folder_hash):
    client = await DBClient()
    where_filter = {
        "path": ["hash"],
        "operator": "Equal",
        "valueText": folder_hash
    }
    result = (
        client.query
        .get("Folder", ["hash", "summary"])
        .with_where(where_filter)
        .with_additional(["id"])
        .do()
    )

    return result["data"]["Get"]["Folder"]


async def search_folders_path(folder_path):
    client = await DBClient()
    where_filter = {
        "path": ["file_path"],
        "operator": "Equal",
        "valueText": folder_path
    }
    result = (
        client.query
        .get("Folder", ["name", "file_path",])
        .with_where(where_filter)
        .with_additional(["id"])
        .do()
    )

    return result["data"]["Get"]["Folder"]
