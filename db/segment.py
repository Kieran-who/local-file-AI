from .db_instance import DBClient
from utils.azure_open_ai import get_vector
import pandas as pd
from IPython.display import HTML

"""
seg = {
text: str,
document: parent document,
}
"""


def display_res(data):
    def flatten(item):

        return {
            "Distance": item.get("_additional", {}).get("distance"),
            "Document": item["document"][0]["name"],
            "Text": item["text"].replace("\n", "<br/>"),
        }

    def explore_json(json_list):
        rows = []
        for item in json_list:
            rows.append(flatten(item))
        return rows

    df = pd.DataFrame(explore_json(data))
    # df = df.style.set_table_styles([
    #     {
    #         'selector': 'table',
    #         'props': 'width: 100%'
    #     }
    # ])
    return HTML(df.to_html(escape=False, index=False))


async def search_segs(query):
    client = await DBClient()
    vector = await get_vector(query)
    result = (
        client.query
        .get("Segment", ["text", "document { ... on Document { name } }"])
        .with_near_vector({
            "vector": vector})
        .with_additional(["id", "creationTimeUnix", "distance"])
        .do()
    )
    print(result)
    return {"raw": result["data"]["Get"]["Segment"], "notebook": display_res(result["data"]["Get"]["Segment"])}

# Search segs by doc id


async def get_doc_segs(doc_id):
    client = await DBClient()
    where_filter = {
        "path": ["document", "Document", "id"],
        "operator": "Equal",
        "valueText": doc_id
    }
    result = (
        client.query
        .get("Segment")
        .with_where(where_filter)
        .with_additional(["id"])
        .do()
    )

    return result["data"]["Get"]["Segment"]


async def delete_seg(id):
    client = await DBClient()
    client.data_object.delete(
        id,
        class_name="Segment",
    )


async def get_all_segs():
    client = await DBClient()
    result = (
        client.query
        .get("Segment", ["text", "document { ... on Document { name } }"])
        .with_limit(10000)
        .with_additional(["id", "creationTimeUnix"])
        .do()
    )
    return result["data"]["Get"]["Segment"]


async def seg_getter(id):
    client = await DBClient()
    seg = client.data_object.get_by_id(id, class_name="Segment")
    return seg


async def new_seg(data_obj, doc_id):
    client = await DBClient()
    custom_vector = await get_vector(data_obj["text"])
    new_seg = client.data_object.create(
        data_obj,
        "Segment",
        vector=custom_vector
    )
    client.data_object.reference.add(
        new_seg,
        "document",
        doc_id,
        from_class_name="Segment",
        to_class_name="Document"
    )
    return new_seg
