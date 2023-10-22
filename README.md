# local-file-AI

This will process files within the designated directory, adding file segments,
files and folders into a vector database for search retrieval and generation

This uses Weaviate's embedded client so no need to spin up a seperate DB. This
is still marked by Weaviate as experimental

# Get Started

1. Update the config file (rename_config.py)
2. Use the main.ipynb to install dependencies and start indexing files
3. Use the search.ipynb to search for documents, folders and document segments

# To do

1. Question and answering / generative responses based on information
2. Have a unique database instance for different directories to maintain
   seperation of directories -> achieved through ability to restore specific
   backups that are named after indexing of specific folders
