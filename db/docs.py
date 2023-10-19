from .db_instance import DBClient
from .segment import delete_seg, get_doc_segs
from utils.azure_open_ai import get_vector
import pandas as pd
from IPython.display import HTML

"""
document = {
summary: str,
name: str,
file_path: str,
hash: str,
segments: array of segment
}
"""


def display_res(data):
    def flatten(item):

        return {
            "Distance": item.get("_additional", {}).get("distance"),
            "Name": item["name"],
            "File Path": item["file_path"],
            "Summary": item["summary"].replace("\n", "<br/>"),
        }

    def explore_json(json_list):
        rows = []
        for item in json_list:
            rows.append(flatten(item))
        return rows

    df = pd.DataFrame(explore_json(data))
    return HTML(df.to_html(escape=False, index=False))

# semantic search


async def search_docs(query):
    client = await DBClient()
    vector = await get_vector(query)
    result = (
        client.query
        .get("Document", ["summary", "name", "file_path"])
        .with_near_vector({
            "vector": vector})
        .with_additional(["id", "creationTimeUnix", "distance"])
        .do()
    )

    return {"raw": result["data"]["Get"]["Document"], "notebook": display_res(result["data"]["Get"]["Document"])}

# test doc's existence via path


async def search_docs_hash(doc_hash):
    client = await DBClient()
    where_filter = {
        "path": ["hash"],
        "operator": "Equal",
        "valueText": doc_hash
    }
    result = (
        client.query
        .get("Document", ["summary", "name", "file_path", "hash"])
        .with_where(where_filter)
        .with_additional(["id", "creationTimeUnix"])
        .do()
    )

    return result["data"]["Get"]["Document"]


async def search_docs_path(doc_path):
    client = await DBClient()
    where_filter = {
        "path": ["file_path"],
        "operator": "Equal",
        "valueText": doc_path
    }
    result = (
        client.query
        .get("Document", ["summary", "name", "file_path", "hash"])
        .with_where(where_filter)
        .with_additional(["id", "creationTimeUnix"])
        .do()
    )

    return result["data"]["Get"]["Document"]


async def get_all_docs():
    client = await DBClient()
    result = (
        client.query
        .get("Document", ["summary", "name", "file_path", "hash",  "segments { ... on Segment { text } }"])
        .with_additional(["id", "creationTimeUnix"])
        .do()
    )
    return result["data"]["Get"]["Document"]


async def doc_getter(id):
    client = await DBClient()
    doc = client.data_object.get_by_id(id, class_name="Document")
    return doc


async def delete_doc(id):
    client = await DBClient()
    segments = await get_doc_segs(id)
    for seg in segments:
        await delete_seg(seg['_additional']['id'])
    client.data_object.delete(
        id,
        class_name="Document",
    )


async def new_doc(data_obj):
    client = await DBClient()
    custom_vector = await get_vector(data_obj["summary"])
    new_doc = client.data_object.create(
        data_obj,
        "Document",
        vector=custom_vector
    )
    return new_doc


async def update_doc_segs(segments, doc_id):

    client = await DBClient()
    for ids in segments:
        client.data_object.reference.add(
            doc_id,
            "segments",
            ids,
            from_class_name="Document",
            to_class_name="Segment",
        )
    return
