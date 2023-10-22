from utils.azure_open_ai import get_chat_completion
from db.folders import new_folder, search_folder_hash, folder_getter, search_folders_path, delete_folder
from db.docs import doc_getter
import tiktoken
import pandas as pd
import os
import xlsxwriter
import hashlib


async def create_folder_table(path, doc_ids, folder_ids):

    # Preparing data for excel
    names = []
    summaries = []

    # Adding document data
    for doc_id in doc_ids:
        doc_object = await doc_getter(doc_id)
        names.append(doc_object["properties"]["name"])
        summaries.append(doc_object["properties"]["summary"])

    # Adding folder data
    for folder_id in folder_ids:
        folder_object = await folder_getter(folder_id)
        names.append(folder_object["properties"]["name"])
        summaries.append(folder_object["properties"]["summary"])

    # Creating DataFrame
    df = pd.DataFrame({'File': names, 'Summary': summaries})

    output_path = os.path.join(path, 'Folder_Contents.xlsx')

    # Check if the file exists
    if os.path.isfile(output_path):
        # If it exists, delete it
        os.remove(output_path)

    # Initialize a writer and save DataFrame to xlsx
    writer = pd.ExcelWriter(output_path, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1', index=False)

    # Get workbook and worksheet for formatting
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']

    # Set column width to autofit and add word wrap
    format = workbook.add_format(
        {'text_wrap': True, 'valign': 'vcenter', 'font_name': 'Arial'})
    worksheet.set_column('A:A', 20, format)
    worksheet.set_column('B:Z', 60, format)

    # Save the result
    writer.close()


async def process_folder(folder_path, document_ids, folder_ids, pbar):
    document_summaries = []
    for doc_id in document_ids:
        doc_object = await doc_getter(doc_id)
        if doc_object["properties"]["summary"]:
            document_summaries.append(doc_object["properties"]["summary"])
    folder_summaries = []
    for folder_id in folder_ids:
        folder_object = await folder_getter(folder_id)
        if folder_object["properties"]["summary"]:
            folder_summaries.append(folder_object["properties"]["summary"])
    # for hash -> sort to ensure same order if no changes
    folder_summaries.sort()
    document_summaries.sort()
    sum_text = '###\n'.join(folder_summaries) + \
        '###\n'.join(document_summaries)

    # test if existing and identical
    folder_hash = hashlib.sha256(
        f"{folder_path}+{sum_text}".encode()).hexdigest()
    existing_folder = await search_folder_hash(folder_hash)
    if existing_folder:
        pbar.update()
        return ({"folder_id": existing_folder[0]["_additional"]["id"]})
    else:
        # test for old and if so, delete
        folder_test = await search_folders_path(folder_path)

        if folder_test:
            for folder in folder_test:
                if folder["file_path"] == folder_path:

                    await delete_folder(folder["_additional"]["id"])
                    folder_id_to_remove = folder["_additional"]["id"]
                    if folder_id_to_remove in folder_ids:
                        folder_ids.remove(folder_id_to_remove)

        # Tokenize the input string.
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        num_tokens = len(encoding.encode(sum_text))

        first_5000_tokens = sum_text

        # reduce string size for summary generation
        if num_tokens > 5000:
            first_5000_tokens = encoding.encode(sum_text)[:5000]
            first_5000_tokens = encoding.decode(first_5000_tokens)

        # get summary of folder
        text_summary = ""
        try:
            summ_message = [{"role": "user", "content": f"Below are summaries for documents and/or folders contained within a folder. Each document should be seperated with ###. Your job is to provide an overall summary of the content that is housed in this folder. Be detailed about the overall makeup of content in the folder but keep it fairly brief. *DO NOT* make specific reference to each sub document or folder. Start your summary with 'This folder'. If there are no provided summaries the folder must be empty and you can just note this fact. \n###\n {first_5000_tokens}"}]
            text_summary = await get_chat_completion(summ_message, max_res_tokens=250)
        except Exception as e:
            text_summary = {"message": {
                "content": "There was an error retrieving a summary for this folder"}}
        new_folder_obj = {}
        if 'message' in text_summary and 'content' in text_summary['message']:
            # new doc object
            new_folder_obj = {"summary": text_summary["message"]["content"], "file_path": folder_path, "name": folder_path.split(
                '/')[-1], "hash": folder_hash}
        else:
            new_folder_obj = {
                {"file_path": folder_path, "name": folder_path.split(
                    '/')[-1], "hash": folder_hash}
            }
        # create folder in db
        folder_id = await new_folder(new_folder_obj, document_ids, folder_ids)

        # create folder summary
        if (len(document_ids) + len(folder_ids)) > 0:
            await create_folder_table(folder_path, document_ids, folder_ids)
        pbar.update()
        return ({"folder_id": folder_id})
