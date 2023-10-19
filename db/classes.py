
weav_classes = {
    "classes": [
        {
            "class": "Segment",
            "description": "Segments of a document",
            "properties": [
                {
                    "name": "text",
                    "dataType": ["text"],
                    "description": "Content that will be vectorized",
                },
                {
                    "name": "document",
                    "dataType": ["Document"],
                    "description": "Parent document",
                },
            ]
        },
        {
            "class": "Document",
            "description": "Document",
            "properties": [
                {
                    "name": "summary",
                    "dataType": ["text"],
                    "description": "Content that will be vectorized",
                },
                {
                    "name": "name",
                    "dataType": ["text"],
                    "description": "document name",
                },
                {
                    "name": "segments",
                    "dataType": ["Segment"],
                    "description": "list of document segments",
                },
                {
                    "name": "file_path",
                    "dataType": ["text"],
                    "description": "relative file path",
                },
                {
                    "name": "hash",
                    "dataType": ["text"],
                    "description": "hash of document text",
                }
            ]
        },
        {
            "class": "Folder",
            "description": "Folder",
            "properties": [
                {
                    "name": "summary",
                    "dataType": ["text"],
                    "description": "Content that will be vectorized",
                },
                {
                    "name": "name",
                    "dataType": ["text"],
                    "description": "document name",
                },
                {
                    "name": "documents",
                    "dataType": ["Document"],
                    "description": "list of documents",
                },
                {
                    "name": "folders",
                    "dataType": ["Folder"],
                    "description": "list of folders",
                },
                {
                    "name": "file_path",
                    "dataType": ["text"],
                    "description": "relative file path",
                },
                {
                    "name": "hash",
                    "dataType": ["text"],
                    "description": "hash of document text",
                }
            ]
        }
    ]
}
