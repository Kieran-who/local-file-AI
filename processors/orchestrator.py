from .folders import process_folder
from .docs import process_doc
import os
import logging
from concurrent.futures import ThreadPoolExecutor
import asyncio
from config import FOLDERS_TO_IGNORE, INDEX_PATH

# Enable logging
logging.basicConfig(level=logging.INFO,
                    handlers=[logging.StreamHandler()])

# Array of accepted filetypes.
accepted_filetypes = [".docx", ".pdf", ".pptx", ".xlsx", ".txt"]
avoid_filenames = ["Folder_Contents.xlsx"]
avoid_directories = FOLDERS_TO_IGNORE

# Helper function to traverse and count all valid files & directories


def count_items(INDEX_PATH):
    total_items = 0
    for dirpath, dirnames_, filenames in os.walk(INDEX_PATH):
        dirnames = [d for d in dirnames_ if d not in avoid_directories]
        filenames = [
            f
            for f in filenames
            if any(f.endswith(ft) for ft in accepted_filetypes) and not any(f == afn for afn in avoid_filenames)
        ]
        total_items += len(filenames) + len(dirnames)
    return total_items


async def process_directory(path, pbar):  # Add pbar as a parameter
    futures = []
    for dirpath, dirnames_, filenames in os.walk(path):
        # Filter directory names to exclude the directories in avoid_directories.
        dirnames = [d for d in dirnames_ if d not in avoid_directories]

        # Filter filenames for the accepted filetypes and not matching avoided files.
        filenames = [
            {
                "name": f,
                "path": os.path.join(dirpath, f),
            }
            for f in filenames
            if any(f.endswith(ft) for ft in accepted_filetypes) and not any(f == afn for afn in avoid_filenames)
        ]

        if filenames:
            # gather creates a future aggregating results from several coroutines
            doc_infos = await asyncio.gather(*[process_doc(f, pbar) for f in filenames])

            doc_ids = [doc_info['id'] for doc_info in doc_infos]

        else:
            doc_ids, doc_summaries = [], []

        folder_ids, folder_summaries = [], []

        if dirnames:
            for dirname in dirnames:
                # Creating task for asyncio to handle task scheduling
                future = asyncio.create_task(
                    process_directory(os.path.join(dirpath, dirname), pbar))
                futures.append(future)

        # Wait for all futures and collect folder_ids and folder_summaries
        for future in futures:
            result = await future
            folder_ids.append(result['folder_id'])

        return await process_folder(dirpath, doc_ids, folder_ids, pbar)
